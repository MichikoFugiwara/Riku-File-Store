# Riku File Store — Multi-storage implementation status

## Included in this build

- Riku branding retained.
- `/mongo` help, `/mongo_add`, `/mongo_list`, `/mongo_test ID`, `/mongo_on ID`, `/mongo_off ID`, `/mongo_remove ID` owner-only commands.
- Additional MongoDB connection strings are ping-tested and encrypted with Fernet before they are stored in the control database.
- Duplicate URI detection; masked short IDs; enable/disable/remove registry entries.
- Private chat is required when adding a URI. The URI message is deleted after successful registration when Telegram permits deletion.
- File uploads are distributed round-robin over active Telegram DB channels, with retry/fallback to another channel if an upload fails. Message IDs remain encoded with the actual destination channel ID so old/new links can resolve through the existing multi-channel lookup logic.

## Important limitation — read before deploying

**MongoDB collection-level automatic rollover is NOT enabled in this build.** The Mongo manager is a secure connection registry and health checker only. Existing application collections (`users`, `pros`, `channels`, `fsub_status`, `request_sub`, and settings) still use the original primary MongoDB connection. This build does not automatically move new user/premium/settings records to the next Atlas cluster when storage reaches 85%.

Do not interpret `/mongo_on` as activating data sharding. It only marks a registered connection active in the registry. Automatic rollover requires a migration-aware repository layer, per-record shard-location indexes, cross-cluster query support, capacity telemetry, and recovery tests. It must be implemented and tested before relying on multiple clusters for production data.

## Environment setup

- `DB_URI` and `DB_NAME`: existing primary MongoDB used by current bot code.
- `MONGO_CONTROL_URI`: control/registry database URI. May be the same as `DB_URI`.
- `MONGO_CONTROL_DB`: database name for registry collection.
- `MONGO_ENCRYPTION_KEY`: stable Fernet key. Generate using:

  `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`

Keep the key in hosting secrets. If lost/changed, previously encrypted cluster URIs cannot be decrypted. Never commit `.env` or real URIs to GitHub.

## Deploy

1. Upload the repository contents (not the ZIP itself) to a new GitHub repository.
2. Add all required environment variables in the hosting dashboard.
3. Ensure the bot is admin in every Telegram DB channel with permission to post messages.
4. Start with a test channel and test files before moving production links.
5. Run `/mongo` as the owner to manage connection registry entries.

## Tests

This build was syntax-checked. Live Telegram API, MongoDB Atlas permissions, URI connectivity, and production load were not tested in this environment.
