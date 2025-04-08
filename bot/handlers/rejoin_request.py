from pyrogram import filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from config import config
from bot.helpers.db import get_db

def register(app):
    @app.on_callback_query(filters.regex("rejoin_request"))
    async def handle_rejoin_request(client, callback: CallbackQuery):
        db = get_db()
        user_id = callback.from_user.id

        for admin_id in config.ADMIN_IDS:
            await client.send_message(
                admin_id,
                f"User {callback.from_user.mention} is requesting to rejoin. Approve?",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Approve", callback_data=f"approve_{user_id}")]
                ])
            )
        await callback.answer("Request sent to admin.", show_alert=True)

    @app.on_callback_query(filters.regex(r"approve_(\d+)"))
    async def approve_user(client, callback: CallbackQuery):
        user_id = int(callback.matches[0].group(1))
        for group_id in config.GROUP_IDS:
            invite = await client.create_chat_invite_link(group_id, member_limit=1, expires_in=3600)
            await client.send_message(user_id, f"✅ Approved. Join using this link:\n{invite.invite_link}")
        await callback.answer("User approved and invited.")
