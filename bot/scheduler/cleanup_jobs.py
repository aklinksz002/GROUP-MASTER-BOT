from apscheduler.triggers.cron import CronTrigger
from pyrogram import Client
from helpers.db import get_db
from helpers.utils import remove_inactive_members, get_group_settings, generate_redirect_invite
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

async def cleanup_job(app: Client, group_id: int):
    db = get_db()
    settings = await get_group_settings(group_id)

    if settings.get("silent_mode"):
        return  # Skip cleanup in silent mode

    removed_users = await remove_inactive_members(app, group_id)

    for user_id in removed_users:
        try:
            # Send message to each removed user with Ask Join Link button
            await app.send_message(
                user_id,
                f"You have been removed from the group. You can request a join link below.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Ask Join Link", callback_data=f"ask_join_link_{group_id}")]
                ])
            )
        except Exception as e:
            print(f"Failed to message removed user {user_id}: {e}")

    # Store report in DB
    await db.reports.insert_one({
        "group_id": group_id,
        "removed_users": removed_users,
        "timestamp": settings.get("last_cleanup", None)
    })

    # Send report to admins
    admins = settings.get("admins", [])
    if not admins:
        async for admin in app.get_chat_members(group_id, filter="administrators"):
            admins.append(admin.user.id)

    report_text = f"**Daily Cleanup Report** for group `{group_id}`\n"
    report_text += f"Total Removed: `{len(removed_users)}`\n\n"
    if removed_users:
        report_text += "Removed User IDs:\n"
        report_text += "\n".join([f"`{uid}`" for uid in removed_users])

    for admin_id in admins:
        try:
            await app.send_message(admin_id, report_text)
        except Exception as e:
            print(f"Couldn't send report to {admin_id}: {e}")

def schedule_cleanup_jobs(app: Client, scheduler):
    db = get_db()

    async def setup_jobs():
        groups = await db.settings.find({}).to_list(length=1000)
        for group in groups:
            group_id = group["group_id"]
            scheduler.add_job(
                cleanup_job,
                CronTrigger(hour=0, minute=0),  # Runs at 12:00 AM IST
                args=[app, group_id],
                id=f"cleanup_{group_id}",
                replace_existing=True
            )

    import asyncio
    asyncio.create_task(setup_jobs())
