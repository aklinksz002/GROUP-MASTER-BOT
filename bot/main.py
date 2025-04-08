import os
import asyncio
from pyrogram import Client, filters
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from motor.motor_asyncio import AsyncIOMotorClient
from aiohttp import web

# Load environment variables
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
MONGO_URL = os.environ.get("MONGO_URL")
REDIRECT_URL = os.environ.get("REDIRECT_URL")
ADMINS = list(map(int, os.environ.get("ADMINS", "").split()))

# Init bot and database
app = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
db = AsyncIOMotorClient(MONGO_URL).botdb
scheduler = AsyncIOScheduler()

# You can add your handlers here
@app.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    await message.reply("Bot is up and running!")

# Add other command/feature handlers here

# Daily task example
async def daily_cleanup():
    print("Running daily cleanup...")
    # Your cleanup logic

scheduler.add_job(daily_cleanup, "cron", hour=0, minute=0)  # Run at 12:00 AM IST
scheduler.start()

# Minimal web server to avoid "No open ports detected"
async def handle(request):
    return web.Response(text="Bot is running")

async def start_web_server():
    app_web = web.Application()
    app_web.router.add_get("/", handle)
    runner = web.AppRunner(app_web)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(os.environ.get("PORT", 8080)))
    await site.start()

# Start bot and web server
loop = asyncio.get_event_loop()
loop.create_task(start_web_server())
app.run()
