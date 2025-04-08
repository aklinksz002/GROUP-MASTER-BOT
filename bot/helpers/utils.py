# bot/helpers/utils.py

from config import config
from helpers.db import get_db
from pyrogram.errors import RPCError

# Remove non-admin members from a group
async def remove_inactive_members(app, group_id: int):
    db = get_db()
    group_settings = await db.groups.find_one({"_id": group_id}) or {}

    if not group_settings.get("auto_cleanup_enabled", True):
        return

    async for member in app.get_chat_members(group_id):
        try:
            if not member.user.is_bot and member.status not in ("administrator", "creator"):
                await app.kick_chat_member(group_id, member.user.id)
                await app.unban_chat_member(group_id, member.user.id)  # Allow rejoin
                print(f"Removed inactive member {member.user.id} from group {group_id}")
        except RPCError as e:
            print(f"Failed to remove user {member.user.id}: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

# Generate redirect-wrapped invite link
def generate_redirect_invite(invite_link: str) -> str:
    base_redirect = config.REDIRECT_BASE_URL.rstrip("?&")
    return f"{base_redirect}?{invite_link}"
