import os
from pyrogram import Client
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
GROUP_IDS = os.getenv("GROUP_IDS", "").split(",")
ADMIN_CHAT_IDS = [int(x) for x in os.getenv("ADMIN_CHAT_IDS", "").split(",")]
REDIRECT_BASE_URL = os.getenv("REDIRECT_BASE_URL")

app = Client("cleanup_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
mongo = MongoClient(MONGO_URI)
db = mongo["telegram_cleanup_bot"]
group_ids = [int(gid.strip()) for gid in GROUP_IDS]
