from pyrogram import Client, filters
from pyrogram.types import Message
from config import config

# Delete system join/leave messages
def register(app: Client):
    @app.on_message(filters.group & filters.service)
    async def auto_delete_join_leave(client: Client, message: Message):
        try:
            await message.delete()
        except Exception as e:
            print(f"[ERROR] Failed to delete system message: {e}")
