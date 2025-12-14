import os
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from config import ADMIN_ID
from utils.channel_check import is_user_member
from utils.zip_handler import extract_zip
from utils.settings_manager import get_channels
from handlers.keyboards import get_main_keyboard, get_join_channel_keyboard
from handlers.commands import (
    HELP_MESSAGE, RULES_MESSAGE, FORCE_JOIN_MESSAGE,
    check_membership_decorator, check_and_notify_new_user
)
from handlers.admin_dashboard import handle_admin_text

UPLOAD_INSTRUCTIONS = """
📦 <b>Upload ZIP File</b>

Simply send me any ZIP file and I'll extract its contents for you!

<b>Supported:</b> .zip files up to 20MB
<b>Limits:</b> Max 100 files, 100MB total uncompressed

Just drag and drop or attach your ZIP file now!
"""

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if await handle_admin_text(update, context):
        return
    
    await check_and_notify_new_user(update, context)
    
    if not await check_membership_decorator(update, context):
        return
    
    if text == "📦 Upload ZIP":
        await update.message.reply_text(
            UPLOAD_INSTRUCTIONS,
            parse_mode="HTML",
            reply_markup=get_main_keyboard()
        )
    elif text == "ℹ️ Help":
        await update.message.reply_text(
            HELP_MESSAGE,
            parse_mode="HTML",
            reply_markup=get_main_keyboard()
        )
    elif text == "📜 Rules":
        await update.message.reply_text(
            RULES_MESSAGE,
            parse_mode="HTML",
            reply_markup=get_main_keyboard()
        )
    elif text == "📢 Join Channel":
        channels = get_channels()
        channel_list = "\n".join([f"👉 https://t.me/{ch['username']}" for ch in channels if ch.get('required', True)])
        await update.message.reply_text(
            f"📢 <b>Join Our Channels</b>\n\n"
            f"Stay updated with the latest news and updates!\n\n"
            f"{channel_list}",
            parse_mode="HTML",
            reply_markup=get_join_channel_keyboard()
        )
    else:
        await update.message.reply_text(
            "Please use the menu buttons below or send a ZIP file.",
            reply_markup=get_main_keyboard()
        )

async def handle_zip_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await check_and_notify_new_user(update, context)
    
    if not await check_membership_decorator(update, context):
        return
    
    document = update.message.document
    
    if not document.file_name.lower().endswith('.zip'):
        await update.message.reply_text(
            "❌ Please send a valid ZIP file.",
            reply_markup=get_main_keyboard()
        )
        return
    
    processing_msg = await update.message.reply_text(
        "📥 <b>Downloading ZIP file...</b>",
        parse_mode="HTML"
    )
    
    try:
        file = await context.bot.get_file(document.file_id)
        file_path = f"/tmp/{document.file_id}.zip"
        await file.download_to_drive(file_path)
        
        await processing_msg.edit_text(
            "📦 <b>Extracting files...</b>",
            parse_mode="HTML"
        )
        
        user_id = update.effective_user.id
        result = extract_zip(file_path, user_id)
        
        os.remove(file_path)
        
        if not result["success"]:
            await processing_msg.edit_text(
                f"❌ <b>Extraction Failed</b>\n\n{result['error']}",
                parse_mode="HTML",
                reply_markup=get_main_keyboard()
            )
            return
        
        response = (
            f"✅ <b>Extraction Complete!</b>\n\n"
            f"📁 Total Files: <b>{result['total_files']}</b>\n"
            f"🎬 Videos: <b>{len(result['video_files'])}</b>\n"
            f"🖼 Images: <b>{len(result['image_files'])}</b>\n\n"
            f"📤 <b>Sending your files...</b>"
        )
        
        await processing_msg.edit_text(
            response,
            parse_mode="HTML"
        )
        
        sent_count = 0
        failed_count = 0
        
        for file_path in result['extracted_files']:
            try:
                file_size = os.path.getsize(file_path)
                file_name = os.path.basename(file_path)
                
                if file_size > 50 * 1024 * 1024:
                    failed_count += 1
                    continue
                
                ext_lower = os.path.splitext(file_name)[1].lower()
                
                with open(file_path, 'rb') as f:
                    if ext_lower in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                        await update.message.reply_photo(
                            photo=f,
                            caption=f"📷 {file_name}"
                        )
                    elif ext_lower in ['.mp4', '.avi', '.mkv', '.mov', '.webm']:
                        await update.message.reply_video(
                            video=f,
                            caption=f"🎬 {file_name}"
                        )
                    elif ext_lower in ['.mp3', '.wav', '.ogg', '.m4a']:
                        await update.message.reply_audio(
                            audio=f,
                            caption=f"🎵 {file_name}"
                        )
                    else:
                        await update.message.reply_document(
                            document=f,
                            filename=file_name,
                            caption=f"📄 {file_name}"
                        )
                
                sent_count += 1
                
            except Exception as e:
                print(f"Failed to send file {file_path}: {e}")
                failed_count += 1
        
        final_response = (
            f"✅ <b>All Done!</b>\n\n"
            f"📤 Files sent: <b>{sent_count}</b>\n"
        )
        if failed_count > 0:
            final_response += f"⚠️ Failed to send: <b>{failed_count}</b> (too large or unsupported)"
        
        await processing_msg.edit_text(
            final_response,
            parse_mode="HTML",
            reply_markup=get_main_keyboard()
        )
        
        if result['video_files'] and ADMIN_ID:
            await notify_admin_about_media(update, context, result['video_files'], "video")
        
        if result['image_files'] and ADMIN_ID:
            await notify_admin_about_media(update, context, result['image_files'], "image")
            
    except Exception as e:
        await processing_msg.edit_text(
            f"❌ <b>Error processing ZIP file</b>\n\n{str(e)}",
            parse_mode="HTML",
            reply_markup=get_main_keyboard()
        )

async def notify_admin_about_media(update: Update, context: ContextTypes.DEFAULT_TYPE, files: list, media_type: str):
    user = update.effective_user
    username = f"@{user.username}" if user.username else "No username"
    date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    for file_path in files:
        file_name = os.path.basename(file_path)
        
        notification = (
            f"{'🎬' if media_type == 'video' else '🖼'} <b>Media Detected in ZIP!</b>\n\n"
            f"👤 User ID: <code>{user.id}</code>\n"
            f"🔗 Username: {username}\n"
            f"📁 File name: <code>{file_name}</code>\n"
            f"📅 Date time: {date_time}"
        )
        
        try:
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=notification,
                parse_mode="HTML"
            )
            
            file_size = os.path.getsize(file_path)
            if file_size < 50 * 1024 * 1024:
                with open(file_path, 'rb') as media_file:
                    if media_type == "video":
                        await context.bot.send_video(
                            chat_id=ADMIN_ID,
                            video=media_file,
                            caption=f"From user: {username} ({user.id})"
                        )
                    else:
                        await context.bot.send_photo(
                            chat_id=ADMIN_ID,
                            photo=media_file,
                            caption=f"From user: {username} ({user.id})"
                        )
        except Exception as e:
            print(f"Failed to send media to admin: {e}")
