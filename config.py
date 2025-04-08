from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    API_ID = int(os.getenv("API_ID"))
    API_HASH = os.getenv("API_HASH")
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    MONGO_URI = os.getenv("MONGO_URI")
    GROUP_IDS = list(map(int, os.getenv("GROUP_IDS", "").split(",")))
    ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(",")))
    REDIRECT_BASE_URL = os.getenv("REDIRECT_BASE_URL")

config = Config()
