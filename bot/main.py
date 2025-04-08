from pyrogram import Client
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import config
from scheduler.cleanup_jobs import schedule_cleanup_jobs
from handlers import admin_panel, broadcast, welcome_handler, rejoin_request
from helpers.db import init_db
from webserver import run_webserver
import asyncio
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the bot client
app = Client(
    name="cleanup_bot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN,
)

# Set up the scheduler
scheduler = AsyncIOScheduler()

# Register all handlers
def register_handlers():
    admin_panel.register(app)
    broadcast.register(app)  # Ensure 'broadcast.register' is defined properly
    welcome_handler.register(app)
    rejoin_request.register(app)

# Initialize the bot and run all setup tasks
async def run():
    # Initialize the database (create collections and indexes)
    await init_db()
    logger.info("Database initialized.")

    # Register all handlers
    register_handlers()
    logger.info("Handlers registered.")

    # Schedule the cleanup jobs
    schedule_cleanup_jobs(app, scheduler)
    logger.info("Cleanup jobs scheduled.")

    # Start the scheduler
    scheduler.start()
    logger.info("Scheduler started.")

    # Keep the bot running
    await app.start()
    logger.info("Bot started.")
    await app.idle()

# This part runs the bot and webserver
async def start_services():
    # Start the bot
    await run()

    # Start the web server
    await run_webserver()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    # Start bot and web server in parallel
    loop.create_task(start_services())  # Run both bot and web server concurrently
    loop.run_forever()
