from pyrogram import filters
from pyrogram.types import Message
from config import config
from bot.helpers.db import get_db
from bot.helpers.utils import generate_redirect_invite

def register(app):
    @app.on_message(filters.new_chat_members)
    async def welcome_new_member(client, message: Message):
        if message.chat.id not in config.GROUP_IDS:
            return

        db = get_db()
        settings = await db.settings.find_one({"group_id": message.chat.id}) or {}
        welcome_msg = settings.get("welcome_message", "Welcome to the group!")

        for user in message.new_chat_members:
            if not user.is_bot:
                await message.reply_text(f"{user.mention}, {welcome_msg}")

    @app.on_message(filters.command("setwelcome") & filters.user(config.ADMIN_IDS))
    async def set_welcome(client, message: Message):
        db = get_db()
        new_msg = message.text.split(None, 1)[1] if len(message.command) > 1 else None
        if not new_msg:
            return await message.reply("Send a message like:\n`/setwelcome Welcome to the group!`")

        await db.settings.update_one(
            {"group_id": message.chat.id},
            {"$set": {"welcome_message": new_msg}},
            upsert=True
        )
        await message.reply("✅ Welcome message updated!")

    @app.on_message(filters.command("setremove") & filters.user(config.ADMIN_IDS))
    async def set_removal_message(client, message: Message):
        db = get_db()
        new_msg = message.text.split(None, 1)[1] if len(message.command) > 1 else None
        if not new_msg:
            return await message.reply("Usage:\n`/setremove You've been removed. Click below to rejoin.`")

        await db.settings.update_one(
            {"group_id": message.chat.id},
            {"$set": {"remove_message": new_msg}},
            upsert=True
        )
        await message.reply("✅ Removal message updated!")
