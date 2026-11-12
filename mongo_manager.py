"""Encrypted registry and health checks for additional MongoDB Atlas clusters.

This module deliberately does NOT shard the bot's existing collections. It manages
connections safely; collection-level routing requires a separate migration-aware
storage adapter and is not enabled by this release.
"""
from __future__ import annotations
import hashlib
from datetime import datetime, timezone
from typing import Any
from cryptography.fernet import Fernet, InvalidToken
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import PyMongoError


class MongoClusterManager:
    def __init__(self, control_uri: str, control_db_name: str, encryption_key: str):
        if not control_uri:
            raise ValueError("MONGO_CONTROL_URI is required")
        if not encryption_key:
            raise ValueError("MONGO_ENCRYPTION_KEY is required")
        self.control_client = AsyncIOMotorClient(control_uri, serverSelectionTimeoutMS=8000)
        self.control_db = self.control_client[control_db_name]
        self.registry = self.control_db["mongo_cluster_registry"]
        self.fernet = Fernet(encryption_key.encode())
        self._clients: dict[str, AsyncIOMotorClient] = {}

    @staticmethod
    def fingerprint(uri: str) -> str:
        return hashlib.sha256(uri.strip().encode()).hexdigest()

    async def add(self, uri: str, label: str) -> tuple[str, str]:
        uri = uri.strip()
        if not uri.startswith(("mongodb://", "mongodb+srv://")):
            raise ValueError("URI must start with mongodb:// or mongodb+srv://")
        key = self.fingerprint(uri)
        if await self.registry.find_one({"_id": key}):
            raise ValueError("This MongoDB URI is already registered")
        test_client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=8000)
        try:
            await test_client.admin.command("ping")
        finally:
            test_client.close()
        encrypted = self.fernet.encrypt(uri.encode()).decode()
        await self.registry.insert_one({
            "_id": key,
            "label": label[:60],
            "uri_encrypted": encrypted,
            "active": True,
            "created_at": datetime.now(timezone.utc),
            "last_check": datetime.now(timezone.utc),
            "status": "healthy",
        })
        return key[:12], "healthy"

    async def list_clusters(self) -> list[dict[str, Any]]:
        rows = []
        async for item in self.registry.find({}, {"uri_encrypted": 0}).sort("created_at", 1):
            item["short_id"] = item["_id"][:12]
            rows.append(item)
        return rows

    async def _uri_for(self, key: str) -> str:
        item = await self.registry.find_one({"_id": key})
        if not item:
            raise ValueError("Cluster not found")
        try:
            return self.fernet.decrypt(item["uri_encrypted"].encode()).decode()
        except InvalidToken as exc:
            raise RuntimeError("Cannot decrypt saved URI; check MONGO_ENCRYPTION_KEY") from exc

    async def test(self, short_id: str) -> tuple[bool, str]:
        item = await self.registry.find_one({"_id": {"$regex": f"^{short_id}"}})
        if not item:
            return False, "Cluster not found"
        uri = self.fernet.decrypt(item["uri_encrypted"].encode()).decode()
        client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=8000)
        try:
            await client.admin.command("ping")
            await self.registry.update_one({"_id": item["_id"]}, {"$set": {"status": "healthy", "last_check": datetime.now(timezone.utc)}})
            return True, "Connection successful"
        except Exception as exc:
            await self.registry.update_one({"_id": item["_id"]}, {"$set": {"status": "error", "last_check": datetime.now(timezone.utc)}})
            return False, str(exc)[:250]
        finally:
            client.close()

    async def set_active(self, short_id: str, active: bool) -> bool:
        result = await self.registry.update_one(
            {"_id": {"$regex": f"^{short_id}"}}, {"$set": {"active": active}}
        )
        return result.modified_count > 0 or result.matched_count > 0

    async def remove(self, short_id: str) -> bool:
        item = await self.registry.find_one({"_id": {"$regex": f"^{short_id}"}})
        if not item:
            return False
        await self.registry.delete_one({"_id": item["_id"]})
        client = self._clients.pop(item["_id"], None)
        if client:
            client.close()
        return True

    async def close(self):
        for client in self._clients.values():
            client.close()
        self._clients.clear()
        self.control_client.close()
