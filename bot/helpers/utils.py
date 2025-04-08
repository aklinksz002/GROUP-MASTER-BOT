from config import config
from helpers.db import get_db
from datetime import datetime, timedelta
from pyrogram import Client
from pyrogram.errors import InviteHashExpired, UserAlreadyParticipant

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

# Remove inactive members from group
async def remove_inactive_members(client: Client, group_id: int):
    db = get_db()
    group_stats = await db.stats.find_one({"group_id": group_id}) or {}

    if not group_stats.get("members"):
        return []

    removed = []
    members = group_stats["members"]
    for user_id, last_active_str in members.items():
        try:
            last_active = datetime.strptime(last_active_str, "%Y-%m-%d %H:%M:%S")
            if datetime.utcnow() - last_active > timedelta(days=7):
                await client.kick_chat_member(group_id, int(user_id))
                removed.append(int(user_id))
        except Exception as e:
            print(f"Error removing {user_id}: {e}")
    return removed

# Get stats for a user in a group
async def get_user_stats(group_id: int, user_id: int):
    db = get_db()
    stats = await db.stats.find_one({"group_id": group_id})
    if not stats:
        return None
    return stats.get("members", {}).get(str(user_id))
