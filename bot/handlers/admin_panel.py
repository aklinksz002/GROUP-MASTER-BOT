from pyrogram import filters
from pyrogram.types import Message
from config import config

toggles = {
    "autocleanup": True,
    "welcome": True,
    "remove_msg": True,
    "rejoin_link": True,
    "invite_protect": True,
    "preview_mode": False,
    "broadcast": True
}

def register(app):
    @app.on_message(filters.command("settings") & filters.user(config.ADMIN_IDS))
    async def settings_panel(client, message: Message):
        status = "\n".join([f"{k}: {'ON' if v else 'OFF'}" for k, v in toggles.items()])
        await message.reply(f"**Feature Status:**\n{status}")

    @app.on_message(filters.command(["on", "off"]) & filters.user(config.ADMIN_IDS))
    async def toggle_feature(client, message: Message):
        if len(message.command) < 2:
            return await message.reply("Usage: /on or /off <featurename>")
        status = message.command[0]
        key = message.command[1].lower()
        if key not in toggles:
            return await message.reply("Invalid feature.")
        toggles[key] = True if status == "on" else False
        await message.reply(f"{key} is now {'ENABLED' if toggles[key] else 'DISABLED'}.")
