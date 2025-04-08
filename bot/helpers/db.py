from motor.motor_asyncio import AsyncIOMotorClient
from config import config
from datetime import datetime, timedelta

# MongoDB Client Setup with default database using Motor (async)
client = AsyncIOMotorClient(config.MONGODB_URI)
db = client.cleanup_bot  # Ensure to specify the database name

# Function to initialize the database (create indexes)
async def init_db():
    await db.reports.create_index("group_id")
    await db.reports.create_index("report_date")

    await db.stats.create_index("group_id")
    await db.invites.create_index("group_id")
    await db.settings.create_index("group_id")

    await db.user_activity.create_index("user_id")
    await db.user_activity.create_index("group_id")

# Function to get the database object (for other modules to use)
def get_db():
    return db

# Save report to the database
async def save_report(group_id, admin_id, report_type, report_data):
    report = {
        "group_id": group_id,
        "admin_id": admin_id,
        "report_type": report_type,
        "report_date": datetime.utcnow(),
        "report_data": report_data,
    }
    await db.reports.insert_one(report)

# Get the last X reports
async def get_last_reports(group_id, report_type, limit=10):
    cursor = db.reports.find({"group_id": group_id, "report_type": report_type}) \
                       .sort("report_date", -1).limit(limit)
    return await cursor.to_list(length=limit)

# Generate redirect invite link
async def generate_redirect_invite(client, group_id):
    collection = db.invites
    existing = await collection.find_one({"group_id": group_id})

    if existing:
        invite_link = existing.get("invite_link")
        expire_at = existing.get("expire_at")
        if expire_at and expire_at > datetime.utcnow():
            return f"https://aklinksz1206.blogspot.com/2025/01/waiting-page.html?{invite_link}"

    try:
        invite = await client.create_chat_invite_link(
            group_id,
            expire_date=datetime.utcnow() + timedelta(hours=24),
            member_limit=1
        )
        new_link = invite.invite_link
        await collection.update_one(
            {"group_id": group_id},
            {"$set": {
                "invite_link": new_link,
                "expire_at": datetime.utcnow() + timedelta(hours=24)
            }},
            upsert=True
        )
        return f"https://aklinksz1206.blogspot.com/2025/01/waiting-page.html?{new_link}"
    except Exception as e:
        print(f"Failed to create invite: {e}")
        return "https://t.me/your_default_fallback_link"
