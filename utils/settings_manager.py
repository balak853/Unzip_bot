import json
import os
from config import DATA_DIR

SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")

DEFAULT_SETTINGS = {
    "channels": [
        {"username": "BALAKXWEBS", "title": "Main Channel", "required": True}
    ],
    "bot_enabled": True,
    "max_zip_size_mb": 20,
    "max_files_per_zip": 100,
    "welcome_message": "",
    "maintenance_mode": False
}

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                for key, value in DEFAULT_SETTINGS.items():
                    if key not in settings:
                        settings[key] = value
                return settings
        except (json.JSONDecodeError, FileNotFoundError):
            return DEFAULT_SETTINGS.copy()
    return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)

def get_channels():
    settings = load_settings()
    return settings.get("channels", [])

def add_channel(username, title=""):
    username = username.replace("@", "").replace("https://t.me/", "").strip()
    if not username:
        return False, "Invalid channel username"
    
    settings = load_settings()
    channels = settings.get("channels", [])
    
    for ch in channels:
        if ch["username"].lower() == username.lower():
            return False, "Channel already exists"
    
    channels.append({
        "username": username,
        "title": title or username,
        "required": True
    })
    
    settings["channels"] = channels
    save_settings(settings)
    return True, f"Channel @{username} added successfully"

def remove_channel(username):
    username = username.replace("@", "").strip()
    settings = load_settings()
    channels = settings.get("channels", [])
    
    original_count = len(channels)
    channels = [ch for ch in channels if ch["username"].lower() != username.lower()]
    
    if len(channels) == original_count:
        return False, "Channel not found"
    
    settings["channels"] = channels
    save_settings(settings)
    return True, f"Channel @{username} removed"

def toggle_channel(username):
    username = username.replace("@", "").strip()
    settings = load_settings()
    channels = settings.get("channels", [])
    
    for ch in channels:
        if ch["username"].lower() == username.lower():
            ch["required"] = not ch["required"]
            settings["channels"] = channels
            save_settings(settings)
            status = "enabled" if ch["required"] else "disabled"
            return True, f"Channel @{username} {status}"
    
    return False, "Channel not found"

def get_setting(key):
    settings = load_settings()
    return settings.get(key, DEFAULT_SETTINGS.get(key))

def set_setting(key, value):
    settings = load_settings()
    settings[key] = value
    save_settings(settings)
    return True

def toggle_maintenance():
    settings = load_settings()
    settings["maintenance_mode"] = not settings.get("maintenance_mode", False)
    save_settings(settings)
    return settings["maintenance_mode"]

def is_maintenance_mode():
    return get_setting("maintenance_mode")
