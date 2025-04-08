from pyrogram import Client
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import config
from scheduler.cleanup_jobs import schedule_cleanup_jobs
from handlers import admin_panel, broadcast, welcome_handler, rejoin_request
from helpers.db import init_db
from flask import Flask
import asyncio
import logging
from threading import Thread

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
    broadcast.register(app)
    welcome_handler.register(app)
    rejoin_request.register(app)

# Initialize Flask (web server)
web_app = Flask(__name__)

# Simple route for web server
@web_app.route("/")
def home():
    return "Bot is running!"

# Function to run the Flask web server in a separate thread
def run_webserver():
    web_app.run(host='0.0.0.0', port=5000, use_reloader=False)  # Run the server on port 5000

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

    # Start the web server in a separate thread to avoid blocking the event loop
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, run_webserver)  # Run the Flask app in a separate thread

    # Start the bot
    await app.start()
    logger.info("Bot started.")
    
    # Keep the bot running using the appropriate method for Pyrogram 2.x
    await app.run()  # This replaces await app.idle() for Pyrogram 2.x
    logger.info("Bot idle...")

if __name__ == "__main__":
    # Run the bot and web server in parallel
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())  # Run the bot and the tasks
