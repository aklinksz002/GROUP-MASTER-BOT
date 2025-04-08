from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from helpers.utils import get_group_settings, auto_delete_join_leave
from helpers.db import get_db

def register(app: Client):

    @app.on_message(filters.group & (filters.new_chat_members | filters.left_chat_member))
    async def handle_join_leave(client: Client, message: Message):
        await auto_delete_join_leave(client, message)

        chat_id = message.chat.id
        db = get_db()
        settings = await get_group_settings(chat_id)

        # Handle new member join
        if message.new_chat_members:
            for member in message.new_chat_members:
                if settings.get("welcome_enabled"):
                    welcome_text = settings.get("welcome_text", "Welcome!")
                    sent_msg = await message.reply_text(
                        f"{welcome_text} {member.mention}",
                    )
                    await sent_msg.delete(delay=10)

                await db.joins.update_one(
                    {"group_id": chat_id, "user_id": member.id},
                    {"$set": {"joined_at": message.date}},
                    upsert=True
                )

        # Handle member left
        elif message.left_chat_member:
            user = message.left_chat_member
            if settings.get("removal_msg_enabled"):
                removal_text = settings.get("removal_text", "You have been removed from the group.")
                sent_msg = await message.reply_text(
                    f"{removal_text} {user.mention}",
                )
                await sent_msg.delete(delay=10)

    @app.on_callback_query(filters.regex(r"^ask_join_link_(\-\d+)$"))
    async def ask_join_link_callback(client, callback):
        group_id = int(callback.data.split("_")[3])
        from helpers.utils import generate_redirect_invite

        invite_link = await generate_redirect_invite(client, group_id)
        await callback.message.reply_text(
            f"Here is your join link: {invite_link}"
        )
        await callback.answer()
