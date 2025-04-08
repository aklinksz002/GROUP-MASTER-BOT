from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import config

def generate_redirect_invite(original_link):
    return f"{config.REDIRECT_BASE_URL}?{original_link}"

def create_rejoin_button():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Request Rejoin", callback_data="rejoin_request")]
    ])
