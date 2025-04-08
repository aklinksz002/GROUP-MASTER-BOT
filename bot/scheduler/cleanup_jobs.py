from pytz import timezone
from apscheduler.triggers.cron import CronTrigger
from pyrogram.errors import ChatAdminRequired
from config import config
from bot.helpers.db import get_db

async def cleanup_group(app, group_id):
    db = get_db()
    members = await app.get_chat_members(group_id)
    for member in members:
        if not member.user.is_bot and not member.status in ("administrator", "creator"):
            try:
                await app.kick_chat_member(group_id, member.user.id)
                await app.send_message(member.user.id, "You’ve been removed. Rejoin using the invite link sent below.")
            except:
                pass

def schedule_cleanup(scheduler, app):
    trigger = CronTrigger(hour=0, minute=0, timezone=timezone("Asia/Kolkata"))
    for group_id in config.GROUP_IDS:
        scheduler.add_job(cleanup_group, trigger, args=[app, group_id])
