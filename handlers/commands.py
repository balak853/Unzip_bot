import os
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from config import ADMIN_ID, DATA_DIR, CHANNEL_LINK
from utils.user_manager import register_user, get_total_users, get_user_info_text
from utils.channel_check import is_user_member
from utils.zip_handler import create_backup_zip
from handlers.keyboards import get_main_keyboard, get_join_channel_keyboard

WELCOME_MESSAGE = """
🤖 <b>Welcome to ZIP Extractor Bot!</b>

I can help you extract ZIP files quickly and easily.

<b>How to use:</b>
1. Make sure you've joined our channel
2. Send me any ZIP file
3. I'll extract and show you the contents

Use the buttons below to navigate!
"""

HELP_MESSAGE = """
ℹ️ <b>Help & Instructions</b>

<b>📦 Upload ZIP</b>
Simply send any ZIP file and I'll extract its contents for you.

<b>📜 Rules</b>
View the bot usage rules.

<b>📢 Join Channel</b>
Join our official channel to use this bot.

<b>Commands:</b>
/start - Start the bot
/help - Show this help message

Need more help? Contact the admin!
"""

RULES_MESSAGE = """
📜 <b>Bot Usage Rules</b>

1️⃣ You must join our channel to use this bot
2️⃣ Only ZIP files are supported
3️⃣ Maximum file size: 20MB (Telegram limit)
4️⃣ Do not upload malicious or illegal content
5️⃣ Respect other users and the community

⚠️ <b>Warning:</b> Violating these rules may result in a ban.
"""

FORCE_JOIN_MESSAGE = """
⚠️ <b>Access Denied!</b>

You must join our official channel to use this bot.

👇 Click the button below to join, then click "I've Joined" to continue.
"""

async def check_and_notify_new_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    is_new, total_users = register_user(user)
    
    if is_new and ADMIN_ID:
        try:
            notification = get_user_info_text(user, total_users)
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=notification,
                parse_mode="HTML"
            )
        except Exception as e:
            print(f"Failed to notify admin: {e}")

async def check_membership_decorator(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id == ADMIN_ID:
        return True
    
    is_member = await is_user_member(context.bot, user_id)
    
    if not is_member:
        await update.message.reply_text(
            FORCE_JOIN_MESSAGE,
            parse_mode="HTML",
            reply_markup=get_join_channel_keyboard()
        )
        return False
    
    return True

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await check_and_notify_new_user(update, context)
    
    if not await check_membership_decorator(update, context):
        return
    
    await update.message.reply_text(
        WELCOME_MESSAGE,
        parse_mode="HTML",
        reply_markup=get_main_keyboard()
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_membership_decorator(update, context):
        return
    
    await update.message.reply_text(
        HELP_MESSAGE,
        parse_mode="HTML",
        reply_markup=get_main_keyboard()
    )

async def users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id != ADMIN_ID:
        await update.message.reply_text("⛔ This command is for admins only.")
        return
    
    total = get_total_users()
    await update.message.reply_text(
        f"📊 <b>User Statistics</b>\n\n"
        f"👥 Total Registered Users: <b>{total}</b>",
        parse_mode="HTML"
    )

async def get_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id != ADMIN_ID:
        await update.message.reply_text("⛔ This command is for admins only.")
        return
    
    await update.message.reply_text("📦 Creating full bot backup... Please wait.")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"/tmp/bot_backup_{timestamp}.zip"
    
    base_dir = "/home/runner/workspace"
    
    items_to_backup = [
        os.path.join(base_dir, "bot.py"),
        os.path.join(base_dir, "config.py"),
        os.path.join(base_dir, "requirements.txt"),
        os.path.join(base_dir, ".env.example"),
        os.path.join(base_dir, "README.md"),
        os.path.join(base_dir, "handlers"),
        os.path.join(base_dir, "utils"),
        os.path.join(base_dir, "data"),
    ]
    
    success, result = create_backup_zip(items_to_backup, backup_path, base_dir)
    
    if success:
        try:
            with open(result, 'rb') as backup_file:
                await update.message.reply_document(
                    document=backup_file,
                    filename=f"bot_backup_{timestamp}.zip",
                    caption="📁 Here's your complete bot backup!\n\nIncludes: source code, handlers, utils, and data"
                )
            os.remove(result)
        except Exception as e:
            await update.message.reply_text(f"❌ Failed to send backup: {e}")
    else:
        await update.message.reply_text(f"❌ Backup failed: {result}")
