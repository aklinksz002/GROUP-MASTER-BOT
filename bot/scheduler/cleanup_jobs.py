# bot/scheduler/cleanup_jobs.py

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import config
from helpers.db import get_db
from helpers.utils import remove_inactive_members

scheduler = AsyncIOScheduler()

def schedule_cleanup_jobs(app):
    import asyncio
    from pyrogram.errors import FloodWait

    @scheduler.scheduled_job("cron", hour=0, minute=0, timezone="Asia/Kolkata")
    async def daily_cleanup():
        db = get_db()
        groups = db.groups.find()
        async for group in groups:
            group_id = group["_id"]
            try:
                await remove_inactive_members(app, group_id)
            except FloodWait as e:
                await asyncio.sleep(e.value)
            except Exception as ex:
                print(f"[Cleanup Error] Group: {group_id} — {ex}")

    scheduler.start()
