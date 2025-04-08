import os
import logging
from pyrogram import Client, filters
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from motor.motor_asyncio import AsyncIOMotorClient
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
ADMIN_IDS = [int(i) for i in os.getenv("ADMIN_IDS", "").split(",") if i]
GROUP_IDS = [int(i) for i in os.getenv("GROUP_IDS", "").split(",") if i]
REDIRECT_URL = os.getenv("REDIRECT_URL")

app = Client("cleanup_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
scheduler = AsyncIOScheduler()
db = AsyncIOMotorClient(MONGO_URI).auto_cleanup_bot

logging.basicConfig(level=logging.INFO)

# Helper functions
def wrap_invite(invite_link):
    return f"{REDIRECT_URL}{invite_link}"

async def remove_non_admins(group_id):
    admins = [m.user.id async for m in app.get_chat_members(group_id, filter="administrators")]
    async for member in app.get_chat_members(group_id):
        if member.user.id not in admins:
            try:
                await app.kick_chat_member(group_id, member.user.id)
                await app.send_message(
                    member.user.id,
                    "You were removed from the group. Click below to rejoin.",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("Rejoin", callback_data=f"rejoin:{group_id}")
                    ]])
                )
                await db.removed.insert_one({
                    "user_id": member.user.id,
                    "group_id": group_id,
                    "date": datetime.utcnow()
                })
            except Exception as e:
                logging.warning(f"Failed to remove user {member.user.id}: {e}")

async def daily_cleanup():
    for group_id in GROUP_IDS:
        await remove_non_admins(group_id)
        invite_link = await app.create_chat_invite_link(group_id, expire_date=datetime.utcnow() + timedelta(days=1))
        wrapped = wrap_invite(invite_link.invite_link)
        for admin_id in ADMIN_IDS:
            try:
                await app.send_message(admin_id, f"New Invite Link for Group {group_id}: {wrapped}")
            except:
                pass

# Bot commands
@app.on_message(filters.command("start"))
async def start_cmd(_, msg: Message):
    await msg.reply("Bot is alive!")

@app.on_message(filters.command("cleanupnow") & filters.user(ADMIN_IDS))
async def cleanup_now(_, msg: Message):
    await msg.reply("Running manual cleanup...")
    for group_id in GROUP_IDS:
        await remove_non_admins(group_id)
    await msg.reply("Cleanup complete.")

@app.on_message(filters.command("broadcast") & filters.user(ADMIN_IDS))
async def broadcast(_, msg: Message):
    await msg.reply("Send the message to broadcast.")
    reply = await app.listen(msg.chat.id)
    for group_id in GROUP_IDS:
        async for member in app.get_chat_members(group_id):
            if member.status != "administrator":
                try:
                    await app.send_message(member.user.id, reply.text)
                except:
                    pass
    await msg.reply("Broadcast sent.")

@app.on_callback_query(filters.regex("^rejoin:"))
async def rejoin_callback(_, query):
    group_id = int(query.data.split(":")[1])
    try:
        invite = await app.create_chat_invite_link(group_id, expire_date=datetime.utcnow() + timedelta(days=1))
        wrapped = wrap_invite(invite.invite_link)
        await query.message.reply(f"Click here to rejoin: {wrapped}")
    except:
        await query.message.reply("Failed to generate invite link.")

# Schedule daily task
scheduler.add_job(daily_cleanup, "cron", hour=0, minute=0)
scheduler.start()

print("Bot started...")
app.run()
