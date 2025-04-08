import os
from aiohttp import web

async def handle(request):
    return web.Response(text="Telegram Cleanup Bot is running!", content_type="text/plain")

def run_webserver():
    app = web.Application()
    app.add_routes([web.get("/", handle)])

    port = int(os.getenv("PORT", 8080))
    web.run_app(app, port=port)
