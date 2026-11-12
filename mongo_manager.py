from pyrogram import Client, filters
from pyrogram.types import Message


def _owner(client, message):
    return message.from_user and message.from_user.id == client.owner


@Client.on_message(filters.private & filters.command("mongo"))
async def mongo_help(client: Client, message: Message):
    if not _owner(client, message):
        return await message.reply("Owner only.")
    if client.mongo_manager is None:
        return await message.reply("Mongo manager is disabled. Set MONGO_ENCRYPTION_KEY and MONGO_CONTROL_URI.")
    await message.reply_text(
        "<b>Riku MongoDB Manager</b>\n\n"
        "/mongo_add — register and ping-test a cluster\n"
        "/mongo_list — list registered clusters\n"
        "/mongo_test ID — test a cluster\n"
        "/mongo_on ID — enable in registry\n"
        "/mongo_off ID — disable in registry\n"
        "/mongo_remove ID — remove registry entry\n\n"
        "<i>Note: this release registers and monitors connections only. It does not yet route existing bot collections across clusters.</i>"
    )


@Client.on_message(filters.private & filters.command("mongo_add"))
async def mongo_add(client: Client, message: Message):
    if not _owner(client, message):
        return await message.reply("Owner only.")
    if client.mongo_manager is None:
        return await message.reply("Mongo manager is disabled. Configure MONGO_ENCRYPTION_KEY.")
    await message.reply("Send a label for this cluster (example: Atlas-02).", quote=True)
    try:
        label_msg = await client.ask(chat_id=message.chat.id, text="Send a label for this cluster (example: Atlas-02).", filters=filters.text, timeout=90)
        label = (label_msg.text or "").strip()
        if not label:
            return await message.reply("Invalid label. Cancelled.")
        await message.reply("Now send the MongoDB connection URI in this private chat. It will be encrypted before storage.")
        uri_msg = await client.ask(chat_id=message.chat.id, text="Send the MongoDB connection URI in this private chat.", filters=filters.text, timeout=120)
        uri = (uri_msg.text or "").strip()
        if not uri:
            return await message.reply("No URI received. Cancelled.")
        result = await client.mongo_manager.add(uri, label)
        try:
            await uri_msg.delete()
        except Exception:
            pass
        await message.reply(f"✅ Registered <b>{label}</b>\nID: <code>{result[0]}</code>\nStatus: {result[1]}")
    except Exception as exc:
        await message.reply(f"❌ Could not add cluster: <code>{str(exc)[:300]}</code>")


@Client.on_message(filters.private & filters.command("mongo_list"))
async def mongo_list(client: Client, message: Message):
    if not _owner(client, message):
        return await message.reply("Owner only.")
    if client.mongo_manager is None:
        return await message.reply("Mongo manager is disabled. Configure MONGO_ENCRYPTION_KEY.")
    try:
        rows = await client.mongo_manager.list_clusters()
        if not rows:
            return await message.reply("No additional MongoDB clusters registered yet.")
        lines = ["<b>Registered MongoDB clusters</b>"]
        for row in rows:
            lines.append(f"• <b>{row.get('label','Unnamed')}</b> — <code>{row['short_id']}</code> — {'ON' if row.get('active') else 'OFF'} — {row.get('status','unknown')}")
        for start in range(0, len(lines), 35):
            await message.reply("\n".join(lines[start:start+35]))
    except Exception as exc:
        await message.reply(f"Registry error: <code>{str(exc)[:250]}</code>")


async def _cluster_action(client, message, action):
    if not _owner(client, message):
        return await message.reply("Owner only.")
    if client.mongo_manager is None:
        return await message.reply("Mongo manager is disabled. Configure MONGO_ENCRYPTION_KEY.")
    args = message.text.split(maxsplit=1)
    if len(args) != 2:
        return await message.reply(f"Usage: /mongo_{action} CLUSTER_ID")
    short_id = args[1].strip()
    try:
        if action == "test":
            ok, detail = await client.mongo_manager.test(short_id)
            return await message.reply(("✅ " if ok else "❌ ") + detail)
        if action in ("on", "off"):
            ok = await client.mongo_manager.set_active(short_id, action == "on")
            return await message.reply("✅ Updated." if ok else "Cluster not found.")
        if action == "remove":
            ok = await client.mongo_manager.remove(short_id)
            return await message.reply("✅ Registry entry removed." if ok else "Cluster not found.")
    except Exception as exc:
        await message.reply(f"❌ {str(exc)[:250]}")


@Client.on_message(filters.private & filters.command("mongo_test"))
async def mongo_test(client, message):
    await _cluster_action(client, message, "test")


@Client.on_message(filters.private & filters.command("mongo_on"))
async def mongo_on(client, message):
    await _cluster_action(client, message, "on")


@Client.on_message(filters.private & filters.command("mongo_off"))
async def mongo_off(client, message):
    await _cluster_action(client, message, "off")


@Client.on_message(filters.private & filters.command("mongo_remove"))
async def mongo_remove(client, message):
    await _cluster_action(client, message, "remove")
