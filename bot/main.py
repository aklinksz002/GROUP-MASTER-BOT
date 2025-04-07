from pyrogram import Client, filters
from apscheduler.schedulers.background import BackgroundScheduler
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import app, db, group_ids, redirect_url, ADMIN_CHAT_ID
from datetime import datetime, timedelta

scheduler = BackgroundScheduler()
scheduler.start()

def get_invite_link(group_id):
    link = app.export_chat_invite_link(group_id)
    return f"{redirect_url}{link}"

def remove_non_admins(group_id):
    admins = [admin.user.id for admin in app.get_chat_members(group_id, filter="administrators")]
    removed = []
    for member in app.get_chat_members(group_id):
        if not member.user.is_bot and member.user.id not in admins:
            app.kick_chat_member(group_id, member.user.id)
            app.send_message(
                member.user.id,
                "You were removed for inactivity. Click below to rejoin:",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Rejoin Group", url=get_invite_link(group_id))]
                ])
            )
            removed.append(member.user.id)
    app.send_message(ADMIN_CHAT_ID, f"Group {group_id} Cleanup Complete. Removed {len(removed)} users.")

def schedule_cleanup():
    for group_id in group_ids:
        scheduler.add_job(
            remove_non_admins,
            "cron",
            hour=0,
            minute=0,
            args=[group_id],
            id=f"cleanup_{group_id}",
            replace_existing=True
        )

@app.on_message(filters.command("start"))
def start_handler(client, message: Message):
    message.reply("Bot is alive and scheduled cleanup is active.")

@app.on_message(filters.command("cleanupnow"))
def manual_cleanup(client, message: Message):
    for group_id in group_ids:
        remove_non_admins(group_id)
    message.reply("Manual cleanup triggered.")

@app.on_message(filters.command("broadcast"))
def broadcast_handler(client, message: Message):
    app.set_chat_action(message.chat.id, "typing")
    msg = message.reply("Send me the message to broadcast.")

    @app.on_message(filters.private & filters.reply)
    def get_broadcast(client, m):
        text = m.text
        for group_id in group_ids:
            app.send_message(group_id, text)
        m.reply("Broadcast complete.")

schedule_cleanup()

app.run()
