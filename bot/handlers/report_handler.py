from pyrogram import Client, filters
from pyrogram.types import Message
from helpers.db import get_db
from helpers.utils import is_member_admin
from datetime import datetime, timedelta
import pytz

IST = pytz.timezone("Asia/Kolkata")

def register(app: Client):
    @app.on_message(filters.command("report") & filters.group)
    async def handle_report(client: Client, message: Message):
        if not await is_member_admin(client, message.chat.id, message.from_user.id):
            return await message.reply("Only admins can send reports.")

        report_text = message.text.split(" ", 1)
        if len(report_text) < 2:
            return await message.reply("Please add report text. Usage: `/report your report`", quote=True)

        db = get_db()
        await db.reports.insert_one({
            "group_id": message.chat.id,
            "admin_id": message.from_user.id,
            "report": report_text[1],
            "timestamp": datetime.now(IST)
        })
        await message.reply("✅ Report submitted successfully.")

    @app.on_message(filters.command("report_history") & filters.group)
    async def handle_report_history(client: Client, message: Message):
        if not await is_member_admin(client, message.chat.id, message.from_user.id):
            return await message.reply("Only admins can view report history.")

        db = get_db()
        ten_days_ago = datetime.now(IST) - timedelta(days=10)
        reports = await db.reports.find({
            "group_id": message.chat.id,
            "timestamp": {"$gte": ten_days_ago}
        }).sort("timestamp", -1).to_list(length=10)

        if not reports:
            return await message.reply("No reports found in the last 10 days.")

        report_lines = [
            f"📝 {r['timestamp'].strftime('%Y-%m-%d %H:%M')} - {r['report']}"
            for r in reports
        ]
        report_text = "**Last 10 Days Report History:**\n\n" + "\n".join(report_lines)
        await message.reply(report_text, quote=True)
