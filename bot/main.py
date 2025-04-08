from pyrogram import Client
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import config
from scheduler.cleanup_jobs import schedule_cleanup_jobs
from handlers import admin_panel, broadcast, welcome_handler, rejoin_request
from helpers.db import init_db
from webserver import run_webserver
import asyncio

app = Client(
    name="cleanup_bot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN,
)

scheduler = AsyncIOScheduler()

# Register all handlers
def register_handlers():
    admin_panel.register(app)
    broadcast.register(app)
    welcome_handler.register(app)
    rejoin_request.register(app)

# Run bot and scheduler
async def run():
    await init_db()
    register_handlers()
    schedule_cleanup_jobs(app, scheduler)
    scheduler.start()
    print("Bot started.")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    # Start bot and web server in parallel
    loop.create_task(app.start())
    loop.create_task(run())
    loop.run_in_executor(None, run_webserver)
    loop.run_forever()
