from pyrogram import filters
from pyrogram.types import Message
from config import config
from bot.helpers.db import get_db

def register(app):
    @app.on_message(filters.command("broadcast") & filters.user(config.ADMIN_IDS))
    async def broadcast_handler(client, message: Message):
        if not message.reply_to_message:
            return await message.reply("Reply to the message you want to broadcast.")

        db = get_db()
        users = await db.users.find().to_list(length=None)
        count = 0
        for user in users:
            try:
                await client.copy_message(chat_id=user["user_id"], from_chat_id=message.chat.id, message_id=message.reply_to_message.message_id)
                count += 1
            except:
                pass
        await message.reply(f"✅ Broadcast sent to {count} users.")
