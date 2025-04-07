from pyrogram import Client, filters
from apscheduler.schedulers.background import BackgroundScheduler
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import app, db, group_ids, REDIRECT_BASE_URL, ADMIN_CHAT_IDS
from datetime import datetime, timedelta

scheduler = BackgroundScheduler(timezone="Asia/Kolkata")
scheduler.start()

def get_wrapped_invite(group_id):
    raw_link = app.export_chat_invite_link(group_id)
    return f"{REDIRECT_BASE_URL}{raw_link}"

def notify_admins(text):
    for admin_id in ADMIN_CHAT_IDS:
        app.send_message(admin_id, text)

def remove_non_admins(group_id):
    try:
        admins = [admin.user.id for admin in app.get_chat_members(group_id, filter="administrators")]
        removed = []
        for member in app.get_chat_members(group_id):
            if not member.user.is_bot and member.user.id not in admins:
                app.kick_chat_member(group_id, member.user.id)
                invite_link = get_wrapped_invite(group_id)
                app.send_message(
                    member.user.id,
                    "You were removed for inactivity. Click below to rejoin:",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("Rejoin Group", url=invite_link)]
                    ])
                )
                removed.append(member.user.id)
        notify_admins(f"[{group_id}] Cleanup Done. Removed: {len(removed)}")
    except Exception as e:
        notify_admins(f"Error during cleanup in group {group_id}: {e}")

def schedule_daily_cleanup():
    for group_id in group_ids:
        scheduler.add_job(
            remove_non_admins,
            trigger="cron",
            hour=0,
            minute=0,
            args=[group_id],
            id=f"cleanup_{group_id}",
            replace_existing=True
        )

@app.on_message(filters.command("start"))
def start_handler(client, message: Message):
    message.reply("Bot is alive and ready!")

@app.on_message(filters.command("cleanupnow"))
def manual_cleanup(client, message: Message):
    for group_id in group_ids:
        remove_non_admins(group_id)
    message.reply("Manual cleanup complete.")

@app.on_message(filters.command("broadcast"))
def broadcast_handler(client, message: Message):
    if message.from_user.id not in ADMIN_CHAT_IDS:
        return message.reply("You are not authorized.")
    
    message.reply("Send the message to broadcast to all groups.")

    @app.on_message(filters.private & filters.reply)
    def do_broadcast(client, m):
        for group_id in group_ids:
            app.send_message(group_id, m.text)
        m.reply("Broadcast sent.")

schedule_daily_cleanup()
app.run()
