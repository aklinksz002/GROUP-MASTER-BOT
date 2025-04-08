# bot/helpers/utils.py

from pyrogram.types import ChatMemberUpdated
from config import config
from helpers.db import get_db
from pyrogram.errors import RPCError

async def remove_inactive_members(app, group_id: int):
    db = get_db()
    group_settings = await db.groups.find_one({"_id": group_id}) or {}
    
    if not group_settings.get("auto_cleanup_enabled", True):
        return
    
    async for member in app.get_chat_members(group_id):
        try:
            if not member.user.is_bot and not member.status in ("administrator", "creator"):
                await app.kick_chat_member(group_id, member.user.id)
                await app.unban_chat_member(group_id, member.user.id)  # optional: allow rejoin
                print(f"Removed inactive member {member.user.id} from group {group_id}")
        except RPCError as e:
            print(f"Failed to remove user {member.user.id}: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
