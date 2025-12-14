from telegram import Update
from telegram.ext import ContextTypes
from utils.channel_check import is_user_member
from handlers.keyboards import get_main_keyboard, get_join_channel_keyboard
from handlers.commands import WELCOME_MESSAGE

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "check_membership":
        user_id = update.effective_user.id
        is_member = await is_user_member(context.bot, user_id)
        
        if is_member:
            await query.edit_message_text(
                "✅ <b>Membership Verified!</b>\n\nYou can now use all bot features.",
                parse_mode="HTML"
            )
            await context.bot.send_message(
                chat_id=user_id,
                text=WELCOME_MESSAGE,
                parse_mode="HTML",
                reply_markup=get_main_keyboard()
            )
        else:
            await query.edit_message_text(
                "❌ <b>You haven't joined yet!</b>\n\n"
                "Please join our channel first, then click 'I've Joined'.",
                parse_mode="HTML",
                reply_markup=get_join_channel_keyboard()
            )
    
    elif data == "back_to_menu":
        await query.edit_message_text(
            WELCOME_MESSAGE,
            parse_mode="HTML"
        )
