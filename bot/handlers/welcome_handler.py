from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from helpers.utils import get_group_settings, generate_redirect_invite
from helpers.db import get_db

# Register function to avoid circular imports
def register(app: Client):

    # Handle new chat members and member leaves
    @app.on_message(filters.group & (filters.new_chat_members | filters.left_chat_member))
    async def handle_join_leave(client: Client, message: Message):
        chat_id = message.chat.id
        db = get_db()
        settings = await get_group_settings(chat_id)

        # Handle new member join
        if message.new_chat_members:
            for member in message.new_chat_members:
                if settings.get("welcome_enabled", True):
                    welcome_text = settings.get("welcome_text", "Welcome!")
                    sent_msg = await message.reply_text(
                        f"{welcome_text} {member.mention}",
                    )
                    await sent_msg.delete(delay=10)  # Deletes the welcome message after 10 seconds

                # Record the join event in the database
                await db.joins.update_one(
                    {"group_id": chat_id, "user_id": member.id},
                    {"$set": {"joined_at": message.date}},
                    upsert=True
                )

        # Handle member leaving
        elif message.left_chat_member:
            user = message.left_chat_member
            if settings.get("removal_msg_enabled", True):
                removal_text = settings.get("removal_text", "You have been removed from the group.")
                sent_msg = await message.reply_text(
                    f"{removal_text} {user.mention}",
                )
                await sent_msg.delete(delay=10)  # Deletes the removal message after 10 seconds

    # Handle the "Ask Join Link" callback query
    @app.on_callback_query(filters.regex(r"^ask_join_link_(\-\d+)$"))
    async def ask_join_link_callback(client, callback):
        group_id = int(callback.data.split("_")[3])  # Extract the group ID from callback data

        # Generate a new invite link
        invite_link = await generate_redirect_invite(client, group_id)
        
        # Send the generated join link to the user
        await callback.message.reply_text(
            f"Here is your join link: {invite_link}"
        )
        
        # Acknowledge the callback to close the button interaction
        await callback.answer()
