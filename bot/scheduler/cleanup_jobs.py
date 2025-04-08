import pytz
from apscheduler.triggers.cron import CronTrigger
from pyrogram.types import ChatMemberUpdated, Message
from datetime import datetime, timedelta
from helpers.utils import get_admin_ids, is_member_admin
from helpers.db import get_db
from config import config

IST = pytz.timezone("Asia/Kolkata")

async def remove_inactive_members(app, chat_id):
    db = get_db()
    removed_users = []
    admin_ids = await get_admin_ids(app, chat_id)

    async for member in app.get_chat_members(chat_id):
        user_id = member.user.id
        if user_id in admin_ids:
            continue
        try:
            await app.kick_chat_member(chat_id, user_id)
            removed_users.append(user_id)
        except Exception as e:
            print(f"[ERROR] Failed to remove {user_id}: {e}")

    # Log cleanup
    if removed_users:
        await db.cleanups.insert_one({
            "group_id": chat_id,
            "removed_users": removed_users,
            "timestamp": datetime.now(IST)
        })
    return removed_users

async def send_daily_report(app, chat_id, removed_users):
    if not removed_users:
        return
    admin_ids = await get_admin_ids(app, chat_id)
    for admin_id in admin_ids:
        try:
            await app.send_message(
                admin_id,
                f"**Daily Cleanup Report** for `{chat_id}`\n"
                f"Removed {len(removed_users)} members at 12 AM."
            )
        except:
            pass

def schedule_cleanup_jobs(app, scheduler):
    @app.on_chat_member_updated()
    async def handle_join_leave(_, member: ChatMemberUpdated):
        # auto delete join/leave messages handled elsewhere
        pass

    async def daily_cleanup():
        db = get_db()
        groups = await db.groups.find().to_list(None)
        for group in groups:
            chat_id = group["chat_id"]
            removed_users = await remove_inactive_members(app, chat_id)
            await send_daily_report(app, chat_id, removed_users)

    scheduler.add_job(
        daily_cleanup,
        CronTrigger(hour=0, minute=0, timezone=IST),
        name="Daily Group Cleanup"
    )
