from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from utils.settings_manager import get_channels

def get_main_keyboard():
    keyboard = [
        [KeyboardButton("📦 Upload ZIP"), KeyboardButton("ℹ️ Help")],
        [KeyboardButton("📜 Rules"), KeyboardButton("📢 Join Channel")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_join_channel_keyboard():
    channels = get_channels()
    required_channels = [ch for ch in channels if ch.get("required", True)]
    
    keyboard = []
    for channel in required_channels:
        keyboard.append([
            InlineKeyboardButton(
                f"📢 Join @{channel['username']}", 
                url=f"https://t.me/{channel['username']}"
            )
        ])
    
    keyboard.append([InlineKeyboardButton("✅ I've Joined", callback_data="check_membership")])
    return InlineKeyboardMarkup(keyboard)

def get_back_keyboard():
    keyboard = [
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)
