from pyrogram import Client
from datetime import datetime, timedelta
from helpers.db import get_db

# Get settings for a group
async def get_group_settings(group_id):
    db = get_db()
    settings = await db.settings.find_one({"group_id": group_id})
    if not settings:
        default_settings = {
            "group_id": group_id,
            "welcome_enabled": True,
            "removal_msg_enabled": True,
            "rejoin_enabled": True,
            "welcome_text": "Welcome to the group!",
            "removal_text": "You have been removed from the group.",
            "silent_mode": False,
            "whitelist": [],
        }
        await db.settings.insert_one(default_settings)
        return default_settings
    return settings

# Invite redirect link wrapper
async def generate_redirect_invite(client: Client, group_id: int):
    db = get_db()
    collection = db.invites
    existing = await collection.find_one({"group_id": group_id})

    if existing:
        invite_link = existing.get("invite_link")
        expire_at = existing.get("expire_at")
        if expire_at and expire_at > datetime.utcnow():
            return f"https://aklinksz1206.blogspot.com/2025/01/waiting-page.html?{invite_link}"

    try:
        chat = await client.get_chat(group_id)
        invite = await client.create_chat_invite_link(group_id, expire_date=datetime.utcnow() + timedelta(hours=24), member_limit=1)
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

# Remove inactive members from the group (example implementation)
async def remove_inactive_members(client: Client, group_id: int, inactivity_threshold: timedelta):
    db = get_db()
    current_time = datetime.utcnow()
    inactive_members = await db.user_activity.find({
        "group_id": group_id,
        "last_activity": {"$lt": current_time - inactivity_threshold}
    }).to_list(length=100)  # Modify the length according to your needs

    for member in inactive_members:
        user_id = member['user_id']
        try:
            # Attempt to kick inactive member
            await client.kick_chat_member(group_id, user_id)
            print(f"Removed inactive user: {user_id}")
            await db.user_activity.delete_one({"user_id": user_id, "group_id": group_id})  # Remove from user_activity collection
        except Exception as e:
            print(f"Failed to remove user {user_id}: {e}")
