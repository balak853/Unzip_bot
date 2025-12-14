import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "BALAKXWEBS")
CHANNEL_LINK = f"https://t.me/{CHANNEL_USERNAME}"

DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
EXTRACTED_DIR = os.path.join(DATA_DIR, "extracted")
LOGS_DIR = os.path.join(DATA_DIR, "logs")

VIDEO_EXTENSIONS = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.3gp']
IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.svg']

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(EXTRACTED_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)
