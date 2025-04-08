# bot/main.py

from pyrogram import Client
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import config
from bot.scheduler.cleanup_jobs import schedule_cleanup_jobs
from bot.handlers import admin_panel, broadcast, welcome_handler, rejoin_request
from bot.helpers.db import init_db
from flask import Flask
import asyncio
import logging
from threading import Thread

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the Pyrogram bot
app = Client(
    name="cleanup_bot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN,
)

# Initialize APScheduler
scheduler = AsyncIOScheduler()

# Register all message/callback handlers
def register_handlers():
    admin_panel.register(app)
    broadcast.register(app)
    welcome_handler.register(app)
    rejoin_request.register(app)
    logger.info("Handlers registered.")

# Flask web server
web_app = Flask(__name__)

@web_app.route("/")
def home():
    return "Bot is live and running!"

# Function to run the web server in a separate thread
def run_webserver():
    web_app.run(host="0.0.0.0", port=5000, use_reloader=False)

# Async main function to initialize bot and components
async def main():
    logger.info("Starting cleanup bot service...")

    # Initialize the database and indexes
    await init_db()
    logger.info("Database initialized.")

    # Register all bot handlers
    register_handlers()

    # Start the cleanup job scheduler
    scheduler.start()
    schedule_cleanup_jobs(app, scheduler)
    logger.info("Scheduler started and jobs scheduled.")

    # Start Flask in background thread
    Thread(target=run_webserver).start()
    logger.info("Web server running on port 5000.")

    # Start the Pyrogram bot
    await app.start()
    logger.info("Bot started.")

    # Keep bot running
    await app.idle()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Bot encountered an error: {e}")
