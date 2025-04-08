from pyrogram import Client, filters
from pyrogram.types import CallbackQuery
from helpers.db import get_db
from helpers.utils import generate_redirect_invite
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Callback handler for "Ask Join Link" button
@app.on_callback_query(filters.regex('ask_join_link'))
async def ask_join_link(client: Client, callback_query: CallbackQuery):
    group_id = callback_query.message.chat.id
    user_id = callback_query.from_user.id

    # Retrieve the invite link (ensure it's the current day's link)
    invite_link = await generate_redirect_invite(client, group_id)

    # Send the join link to the user
    await callback_query.message.reply(
        f"Here is your join link for today: {invite_link}",
        reply_markup=None
    )

    # Optionally, log or track user actions
    db = get_db()
    await db.user_activity.insert_one({
        "user_id": user_id,
        "group_id": group_id,
        "action": "requested join link",
        "timestamp": datetime.utcnow()
    })

# Send a message with the "Ask Join Link" button
async def send_join_link_button(client: Client, chat_id: int):
    button = InlineKeyboardButton("Ask Join Link", callback_data="ask_join_link")
    keyboard = InlineKeyboardMarkup([[button]])

    await client.send_message(
        chat_id,
        "Click the button below to get your daily join link:",
        reply_markup=keyboard
    )
