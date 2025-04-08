# bot/helpers/db.py

from motor.motor_asyncio import AsyncIOMotorClient
from config import config

_db = None

async def connect_db():
    global _db
    client = AsyncIOMotorClient(config.MONGO_URI)
    _db = client["cleanup_bot"]

def get_db():
    if _db is None:
        raise RuntimeError("Database not connected. Call connect_db() first.")
    return _db
