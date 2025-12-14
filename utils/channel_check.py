from telegram import ChatMember
from utils.settings_manager import get_channels

async def is_user_member(bot, user_id):
    channels = get_channels()
    required_channels = [ch for ch in channels if ch.get("required", True)]
    
    if not required_channels:
        return True
    
    for channel in required_channels:
        try:
            member = await bot.get_chat_member(
                chat_id=f"@{channel['username']}", 
                user_id=user_id
            )
            if member.status not in [
                ChatMember.MEMBER,
                ChatMember.ADMINISTRATOR,
                ChatMember.OWNER
            ]:
                return False
        except Exception:
            continue
    
    return True

async def get_missing_channels(bot, user_id):
    channels = get_channels()
    required_channels = [ch for ch in channels if ch.get("required", True)]
    missing = []
    
    for channel in required_channels:
        try:
            member = await bot.get_chat_member(
                chat_id=f"@{channel['username']}", 
                user_id=user_id
            )
            if member.status not in [
                ChatMember.MEMBER,
                ChatMember.ADMINISTRATOR,
                ChatMember.OWNER
            ]:
                missing.append(channel)
        except Exception:
            missing.append(channel)
    
    return missing
