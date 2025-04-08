from motor.motor_asyncio import AsyncIOMotorClient
from config import config

db = None

async def connect_db():
    global db
    client = AsyncIOMotorClient(config.MONGO_URI)
    db = client["cleanup_bot"]

def get_db():
    return db
