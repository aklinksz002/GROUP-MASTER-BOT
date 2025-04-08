import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    API_ID = int(os.getenv("API_ID", ""))
    API_HASH = os.getenv("API_HASH", "")
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")
    MONGODB_URI = os.getenv("MONGODB_URI", "")
    OWNER_ID = int(os.getenv("OWNER_ID", "0"))  # Your Telegram user ID
    GROUP_IDS = os.getenv("GROUP_IDS", "").split(",")  # Comma-separated list of group IDs
    REDIRECT_BASE = os.getenv("REDIRECT_BASE")
    TIMEZONE = os.getenv("TIMEZONE", "Asia/Kolkata")

config = Config()
