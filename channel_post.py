import asyncio
from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait
from helper.helper_func import encode

#===============================================================#

@Client.on_message(filters.private & ~filters.command(['start', 'shortner','users','broadcast','batch','genlink','stats', 'pbroadcast', 'db', 'adddb', 'add_db', 'removedb', 'rm_db',  'ban', 'unban', 'addpremium', 'delpremium', 'premiumusers', 'request', 'profile']))
async def channel_post(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
    reply_text = await message.reply_text("Please Wait...!", quote=True)
    # Round-robin upload across all active DB channels; retry the next channel on failure.
    channels = []
    for channel_id, data in getattr(client, "db_channels", {}).items():
        if data.get("is_active", True):
            channels.append(int(channel_id))
    if not channels:
        channels = [getattr(client, "primary_db_channel", client.db)]
    start_index = getattr(client, "db_write_index", 0) % len(channels)
    ordered = channels[start_index:] + channels[:start_index]
    post_message = None
    target_channel = None
    last_error = None
    for channel_id in ordered:
        try:
            post_message = await message.copy(chat_id=channel_id, disable_notification=True)
            target_channel = channel_id
            client.db_write_index = (channels.index(channel_id) + 1) % len(channels)
            break
        except FloodWait as e:
            await asyncio.sleep(e.value)
            try:
                post_message = await message.copy(chat_id=channel_id, disable_notification=True)
                target_channel = channel_id
                client.db_write_index = (channels.index(channel_id) + 1) % len(channels)
                break
            except Exception as retry_error:
                last_error = retry_error
        except Exception as e:
            last_error = e
            continue
    if post_message is None:
        await reply_text.edit_text(f"Could not upload to any active DB channel: {str(last_error)[:200]}")
        return
    converted_id = post_message.id * abs(target_channel)
    string = f"get-{converted_id}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]])

    await reply_text.edit(f"<b>Here is your link</b>\n\n{link}", reply_markup=reply_markup, disable_web_page_preview = True)

    if not client.disable_btn:
        await post_message.edit_reply_markup(reply_markup)

#===============================================================#

@Client.on_message(filters.channel & filters.incoming)
async def new_post(client: Client, message: Message):
    if message.chat.id not in [int(cid) for cid in getattr(client, "db_channels", {})] and message.chat.id != client.db:
        return
    if client.disable_btn:
        return

    converted_id = message.id * abs(message.chat.id)
    string = f"get-{converted_id}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]])
    try:
        await message.edit_reply_markup(reply_markup)
    except Exception as e:
        print(e)

        pass





