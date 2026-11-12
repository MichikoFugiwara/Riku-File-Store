import logging
import os
from logging.handlers import RotatingFileHandler

# Bot Configuration
LOG_FILE_NAME = "bot.log"
PORT = int(os.getenv("PORT", "8080"))
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

MSG_EFFECT = 5046509860389126442

SHORT_URL = "linkshortify.com" # shortner url 
SHORT_API = "" 
SHORT_TUT = "https://t.me/How_to_Download_7x/26"

# Bot Configuration
SESSION = "riku"
TOKEN = os.getenv("BOT_TOKEN", "")
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
WORKERS = 5

DB_URI = os.getenv("DB_URI", os.getenv("MONGO_URI", ""))
DB_NAME = os.getenv("DB_NAME", "riku_file_store")

FSUBS = []  # Add force-sub channels from the bot settings after deployment.
# Database Channel (Primary)
DB_CHANNEL = int(os.getenv("DB_CHANNEL", "0"))  # Required: private database channel ID
# Multiple Database Channels (can be set via bot settings)
# DB_CHANNELS = {
#     "-1002595092736": {"name": "Primary DB", "is_primary": True, "is_active": True},
#     "-1001234567890": {"name": "Secondary DB", "is_primary": False, "is_active": True}
# }
# Auto Delete Timer (seconds)
AUTO_DEL = 300
# Admin IDs
ADMINS = [int(x.strip()) for x in os.getenv("ADMINS", "").split(",") if x.strip().isdigit()]
# Bot Settings
DISABLE_BTN = True
PROTECT = True

# Messages Configuration
MESSAGES = {
    "START": "<b>✦ Welcome to Riku File Store, {first}! ✦</b>\n\n<blockquote>Your files, neatly organized and ready to access. Choose an option below to get started.</blockquote>",
    "FSUB": "<b>✦ One quick step! ✦</b>\n\nPlease join the required channel(s) below, then try your file link again.",
    "ABOUT": "<b>✦ Riku File Store ✦</b>\n\nA simple and reliable Telegram file store bot.\n\n<b>Features</b>\n• Fast file access\n• Batch links\n• User-friendly controls\n• Premium and admin tools\n\n<b>Powered by:</b> Pyrogram and MongoDB",
    "REPLY": "<b>Welcome to Riku File Store.</b> Use /start to get started.",
    "SHORT_MSG": "<b>✦ Hello {first}! ✦\n\nYour file link is ready. Tap the button below to continue.</b>",
    "START_PHOTO": "",
    "FSUB_PHOTO": "",
    "SHORT_PIC": "",
    "SHORT": ""
}

def LOGGER(name: str, client_name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    formatter = logging.Formatter(
        f"[%(asctime)s - %(levelname)s] - {client_name} - %(name)s - %(message)s",
        datefmt='%d-%b-%y %H:%M:%S'
    )
    file_handler = RotatingFileHandler(LOG_FILE_NAME, maxBytes=50_000_000, backupCount=10)
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger
