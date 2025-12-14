import json
import os
from datetime import datetime
from config import USERS_FILE, DATA_DIR

os.makedirs(DATA_DIR, exist_ok=True)

def load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    return {}

def save_users(users):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

def is_new_user(user_id):
    users = load_users()
    return str(user_id) not in users

def register_user(user):
    users = load_users()
    user_id = str(user.id)
    
    if user_id in users:
        return False, len(users)
    
    users[user_id] = {
        "id": user.id,
        "first_name": user.first_name or "",
        "last_name": user.last_name or "",
        "username": user.username or "",
        "registered_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    save_users(users)
    return True, len(users)

def get_total_users():
    users = load_users()
    return len(users)

def get_user_info_text(user, total_users):
    full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
    username = f"@{user.username}" if user.username else "No username"
    profile_link = f"tg://user?id={user.id}"
    date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return (
        f"🆕 <b>New User Alert!</b>\n\n"
        f"📊 Total Users - <b>{total_users}</b>\n"
        f"👤 FULL name - <b>{full_name}</b>\n"
        f"🔗 Username - <b>{username}</b>\n"
        f"🔗 Profile link - <a href='{profile_link}'>{full_name}</a>\n"
        f"📅 Date time - <b>{date_time}</b>"
    )
