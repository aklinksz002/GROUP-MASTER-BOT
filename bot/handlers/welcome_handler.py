from pyrogram import Client, filters
from pyrogram.types import Message, ChatMemberUpdated, InlineKeyboardMarkup, InlineKeyboardButton
from config import config
from helpers.db import get_db
from helpers.utils import generate_redirect_invite, get_group_settings, get_user_stats

@Client.on_chat_member_updated(filters.group)
async def handle_member_updates(client: Client, update: ChatMemberUpdated):
    group_id = update.chat.id
    user_id = update.new_chat_member.user.id

    db = get_db()
    settings = await get_group_settings(group_id)

    # New member joined
    if update.old_chat_member.status in ["left", "kicked"] and update.new_chat_member.status == "member":
        if settings.get("welcome_enabled", True):
            welcome_text = settings.get("welcome_text", f"Welcome {update.new_chat_member.user.mention}!")
            await client.send_message(group_id, welcome_text)

    # Member removed
    elif update.old_chat_member.status == "member" and update.new_chat_member.status in ["left", "kicked"]:
        if update.old_chat_member.user.is_bot:
            return

        # Send private rejoin link if enabled
        if settings.get("rejoin_enabled", True):
            redirect_link = await generate_redirect_invite(client, group_id)
            try:
                await client.send_message(
                    user_id,
                    f"You've been removed from {update.chat.title}. Tap below to rejoin (valid for 24 hours):",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Rejoin", url=redirect_link)]])
                )
            except Exception:
                pass

        # Custom removal message
        if settings.get("removal_msg_enabled", True):
            removal_text = settings.get("removal_text", "You have been removed.")
            try:
                await client.send_message(user_id, removal_text)
            except Exception:
                pass
