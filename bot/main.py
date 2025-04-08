import os
import asyncio
import logging
import http.server
import socketserver
import threading
from datetime import datetime
from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

# Load environment variables
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_IDS = list(map(int, os.environ.get("ADMIN_IDS", "").split(',')))
GROUP_IDS = list(map(int, os.environ.get("GROUP_IDS", "").split(',')))
REDIRECT_URL = os.environ.get("REDIRECT_URL")
MONGO_URI = os.environ.get("MONGO_URI")

app = Client("cleanup-bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
db = AsyncIOMotorClient(MONGO_URI).get_database("telegram_bot")
scheduler = AsyncIOScheduler()

logging.basicConfig(level=logging.INFO)

# Keep-alive HTTP server for Render Free
def keep_alive():
    port = int(os.environ.get("PORT", 8080))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Keep-alive server running on port {port}")
        httpd.serve_forever()

threading.Thread(target=keep_alive).start()

# Send broadcast to all groups
@app.on_message(filters.command("broadcast") & filters.user(ADMIN_IDS))
async def broadcast_start(_, message: Message):
    await message.reply("Send the message to broadcast.")
    user_id = message.from_user.id

    @app.on_message(filters.private & filters.user(user_id))
    async def broadcast_send(_, msg: Message):
        for group_id in GROUP_IDS:
            try:
                await app.send_message(group_id, msg.text)
            except Exception as e:
                print(f"Failed to send to {group_id}: {e}")
        await msg.reply("Broadcast sent.")
        app.remove_handler(broadcast_send)

# Welcome message
@app.on_message(filters.new_chat_members)
async def welcome(client, message: Message):
    for user in message.new_chat_members:
        await message.reply(f"Welcome {user.mention}!\nPlease follow the rules.")

# Cleanup command to remove non-admins now
@app.on_message(filters.command("cleanupnow") & filters.user(ADMIN_IDS))
async def manual_cleanup(client, message: Message):
    await remove_non_admins(message.chat.id, notify=True)

# Send invite links and cleanup daily
async def daily_tasks():
    for group_id in GROUP_IDS:
        try:
            link = await app.export_chat_invite_link(group_id)
            wrapped_link = REDIRECT_URL + link.replace("https://", "")
            for admin_id in ADMIN_IDS:
                await app.send_message(admin_id, f"Daily invite link for group `{group_id}`:\n{wrapped_link}")
            await remove_non_admins(group_id, notify=False)
        except Exception as e:
            print(f"Error in daily task for group {group_id}: {e}")

# Remove non-admin users from group
async def remove_non_admins(chat_id, notify=True):
    try:
        admins = await app.get_chat_members(chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS)
        admin_ids = [admin.user.id for admin in admins]

        async for member in app.get_chat_members(chat_id):
            if member.user.id not in admin_ids:
                try:
                    await app.send_message(
                        member.user.id,
                        "You have been removed from the group. Click the button to rejoin.",
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton("Rejoin Group", callback_data=f"rejoin_{chat_id}")
                        ]])
                    )
                except:
                    pass
                await app.ban_chat_member(chat_id, member.user.id)
                await asyncio.sleep(0.5)
        if notify:
            await app.send_message(chat_id, "Cleanup completed: Non-admins removed.")
    except Exception as e:
        print(f"Error during cleanup: {e}")

# Handle /start
@app.on_message(filters.command("start"))
async def start(_, message: Message):
    await message.reply("Bot is alive and running!")

# Handle rejoin button
@app.on_callback_query(filters.regex("rejoin_"))
async def rejoin_callback(client, callback):
    chat_id = int(callback.data.split("_")[1])
    try:
        link = await app.export_chat_invite_link(chat_id)
        wrapped = REDIRECT_URL + link.replace("https://", "")
        await callback.message.reply(f"Here is your rejoin link:\n{wrapped}")
        await callback.answer("Rejoin link sent!", show_alert=True)
    except Exception as e:
        await callback.message.reply("Could not generate invite link.")
        print(e)

# Daily scheduler
scheduler.add_job(daily_tasks, "cron", hour=0, minute=0)  # 12:00 AM IST
scheduler.start()

# Run the bot
print("Bot running...")
app.run()
