import os
from pyrogram import Client
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
GROUP_IDS = os.getenv("GROUP_IDS", "").split(",")
REDIRECT_BASE_URL = os.getenv("REDIRECT_BASE_URL")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))

app = Client("cleanup_bot", bot_token=BOT_TOKEN)
db = MongoClient(MONGO_URI).bot_data

group_ids = [int(gid.strip()) for gid in GROUP_IDS]
redirect_url = REDIRECT_BASE_URL
