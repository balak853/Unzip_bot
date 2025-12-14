from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import ADMIN_ID
from utils.settings_manager import (
    get_channels, add_channel, remove_channel, toggle_channel,
    get_setting, set_setting, toggle_maintenance, is_maintenance_mode
)
from utils.user_manager import get_total_users, load_users

def get_admin_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("📢 Channel Management", callback_data="admin_channels")],
        [InlineKeyboardButton("👥 User Management", callback_data="admin_users")],
        [InlineKeyboardButton("⚙️ Bot Settings", callback_data="admin_settings")],
        [InlineKeyboardButton("📊 Statistics", callback_data="admin_stats")],
        [InlineKeyboardButton("❌ Close", callback_data="admin_close")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_channel_management_keyboard():
    channels = get_channels()
    keyboard = []
    
    for ch in channels:
        status = "✅" if ch.get("required", True) else "❌"
        keyboard.append([
            InlineKeyboardButton(f"{status} @{ch['username']}", callback_data=f"ch_toggle_{ch['username']}"),
            InlineKeyboardButton("🗑", callback_data=f"ch_remove_{ch['username']}")
        ])
    
    keyboard.append([InlineKeyboardButton("➕ Add Channel", callback_data="ch_add")])
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="admin_back")])
    
    return InlineKeyboardMarkup(keyboard)

def get_user_management_keyboard():
    keyboard = [
        [InlineKeyboardButton("📋 View All Users", callback_data="users_list")],
        [InlineKeyboardButton("📢 Broadcast Message", callback_data="users_broadcast")],
        [InlineKeyboardButton("📊 User Stats", callback_data="users_stats")],
        [InlineKeyboardButton("🔙 Back", callback_data="admin_back")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_settings_keyboard():
    maintenance = is_maintenance_mode()
    maint_text = "🔴 Disable Maintenance" if maintenance else "🟢 Enable Maintenance"
    
    keyboard = [
        [InlineKeyboardButton(maint_text, callback_data="settings_maintenance")],
        [InlineKeyboardButton("📦 ZIP Limits", callback_data="settings_zip")],
        [InlineKeyboardButton("🔙 Back", callback_data="admin_back")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="admin_back")]])

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id != ADMIN_ID:
        await update.message.reply_text("⛔ This command is for admins only.")
        return
    
    channels = get_channels()
    total_users = get_total_users()
    maintenance = "🔴 ON" if is_maintenance_mode() else "🟢 OFF"
    
    text = (
        "🔧 <b>Admin Dashboard</b>\n\n"
        f"👥 Total Users: <b>{total_users}</b>\n"
        f"📢 Active Channels: <b>{len([c for c in channels if c.get('required', True)])}</b>\n"
        f"🛠 Maintenance: {maintenance}\n\n"
        "Select an option below:"
    )
    
    await update.message.reply_text(
        text,
        parse_mode="HTML",
        reply_markup=get_admin_main_keyboard()
    )

async def handle_admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    
    if user_id != ADMIN_ID:
        await query.answer("⛔ Admin only!", show_alert=True)
        return
    
    await query.answer()
    data = query.data
    
    if data == "admin_back":
        channels = get_channels()
        total_users = get_total_users()
        maintenance = "🔴 ON" if is_maintenance_mode() else "🟢 OFF"
        
        text = (
            "🔧 <b>Admin Dashboard</b>\n\n"
            f"👥 Total Users: <b>{total_users}</b>\n"
            f"📢 Active Channels: <b>{len([c for c in channels if c.get('required', True)])}</b>\n"
            f"🛠 Maintenance: {maintenance}\n\n"
            "Select an option below:"
        )
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=get_admin_main_keyboard())
    
    elif data == "admin_channels":
        channels = get_channels()
        text = (
            "📢 <b>Channel Management</b>\n\n"
            f"Total channels: {len(channels)}\n"
            f"Active: {len([c for c in channels if c.get('required', True)])}\n\n"
            "✅ = Required | ❌ = Disabled\n"
            "Tap channel to toggle, 🗑 to remove"
        )
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=get_channel_management_keyboard())
    
    elif data == "admin_users":
        text = (
            "👥 <b>User Management</b>\n\n"
            f"Total registered users: <b>{get_total_users()}</b>\n\n"
            "Select an option:"
        )
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=get_user_management_keyboard())
    
    elif data == "admin_settings":
        text = (
            "⚙️ <b>Bot Settings</b>\n\n"
            f"Maintenance Mode: {'🔴 ON' if is_maintenance_mode() else '🟢 OFF'}\n"
            f"Max ZIP Size: {get_setting('max_zip_size_mb')}MB\n"
            f"Max Files per ZIP: {get_setting('max_files_per_zip')}\n\n"
            "Select an option:"
        )
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=get_settings_keyboard())
    
    elif data == "admin_stats":
        users = load_users()
        total = len(users)
        with_username = len([u for u in users.values() if u.get("username")])
        
        text = (
            "📊 <b>Bot Statistics</b>\n\n"
            f"👥 Total Users: <b>{total}</b>\n"
            f"📛 With Username: <b>{with_username}</b>\n"
            f"👤 Without Username: <b>{total - with_username}</b>\n"
            f"📢 Channels: <b>{len(get_channels())}</b>\n"
        )
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=get_back_keyboard())
    
    elif data == "admin_close":
        await query.delete_message()
    
    elif data.startswith("ch_toggle_"):
        username = data.replace("ch_toggle_", "")
        success, message = toggle_channel(username)
        await query.answer(message, show_alert=True)
        
        channels = get_channels()
        text = (
            "📢 <b>Channel Management</b>\n\n"
            f"Total channels: {len(channels)}\n"
            f"Active: {len([c for c in channels if c.get('required', True)])}\n\n"
            "✅ = Required | ❌ = Disabled"
        )
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=get_channel_management_keyboard())
    
    elif data.startswith("ch_remove_"):
        username = data.replace("ch_remove_", "")
        success, message = remove_channel(username)
        await query.answer(message, show_alert=True)
        
        channels = get_channels()
        text = (
            "📢 <b>Channel Management</b>\n\n"
            f"Total channels: {len(channels)}\n"
            f"Active: {len([c for c in channels if c.get('required', True)])}\n\n"
            "✅ = Required | ❌ = Disabled"
        )
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=get_channel_management_keyboard())
    
    elif data == "ch_add":
        context.user_data["awaiting_channel"] = True
        text = (
            "📢 <b>Add New Channel</b>\n\n"
            "Send the channel username (with or without @)\n\n"
            "Example: @MyChannel or MyChannel\n\n"
            "Send /cancel to cancel"
        )
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=get_back_keyboard())
    
    elif data == "users_list":
        users = load_users()
        if not users:
            text = "👥 <b>No users registered yet</b>"
        else:
            user_list = list(users.values())[:20]
            text = "👥 <b>Recent Users</b> (showing last 20)\n\n"
            for i, u in enumerate(user_list, 1):
                name = f"{u.get('first_name', '')} {u.get('last_name', '')}".strip() or "Unknown"
                username = f"@{u.get('username')}" if u.get('username') else "No username"
                text += f"{i}. {name} ({username})\n"
        
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=get_back_keyboard())
    
    elif data == "users_broadcast":
        context.user_data["awaiting_broadcast"] = True
        text = (
            "📢 <b>Broadcast Message</b>\n\n"
            "Send the message you want to broadcast to all users.\n\n"
            "Send /cancel to cancel"
        )
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=get_back_keyboard())
    
    elif data == "users_stats":
        users = load_users()
        total = len(users)
        text = f"📊 <b>User Statistics</b>\n\n👥 Total: <b>{total}</b>"
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=get_back_keyboard())
    
    elif data == "settings_maintenance":
        new_status = toggle_maintenance()
        status_text = "enabled" if new_status else "disabled"
        await query.answer(f"Maintenance mode {status_text}", show_alert=True)
        
        text = (
            "⚙️ <b>Bot Settings</b>\n\n"
            f"Maintenance Mode: {'🔴 ON' if is_maintenance_mode() else '🟢 OFF'}\n"
            f"Max ZIP Size: {get_setting('max_zip_size_mb')}MB\n"
            f"Max Files per ZIP: {get_setting('max_files_per_zip')}\n\n"
            "Select an option:"
        )
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=get_settings_keyboard())
    
    elif data == "settings_zip":
        text = (
            "📦 <b>ZIP Settings</b>\n\n"
            f"Max ZIP Size: {get_setting('max_zip_size_mb')}MB\n"
            f"Max Files: {get_setting('max_files_per_zip')}\n\n"
            "These limits protect against large file attacks."
        )
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=get_back_keyboard())

async def handle_admin_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id != ADMIN_ID:
        return False
    
    text = update.message.text
    
    if text == "/cancel":
        context.user_data.pop("awaiting_channel", None)
        context.user_data.pop("awaiting_broadcast", None)
        await update.message.reply_text("❌ Cancelled", reply_markup=get_admin_main_keyboard())
        return True
    
    if context.user_data.get("awaiting_channel"):
        context.user_data.pop("awaiting_channel", None)
        success, message = add_channel(text)
        await update.message.reply_text(
            f"{'✅' if success else '❌'} {message}",
            reply_markup=get_channel_management_keyboard()
        )
        return True
    
    if context.user_data.get("awaiting_broadcast"):
        context.user_data.pop("awaiting_broadcast", None)
        users = load_users()
        success_count = 0
        fail_count = 0
        
        await update.message.reply_text("📢 Broadcasting message...")
        
        for user_id_str, user_data in users.items():
            try:
                await context.bot.send_message(
                    chat_id=int(user_id_str),
                    text=text
                )
                success_count += 1
            except Exception:
                fail_count += 1
        
        await update.message.reply_text(
            f"✅ Broadcast complete!\n\n"
            f"📤 Sent: {success_count}\n"
            f"❌ Failed: {fail_count}",
            reply_markup=get_admin_main_keyboard()
        )
        return True
    
    return False
