import asyncio
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from config import BOT_TOKEN
from handlers.commands import (
    start_command,
    help_command,
    users_command,
    get_command,
)
from handlers.messages import handle_text_message, handle_zip_file
from handlers.callbacks import handle_callback
from handlers.admin_dashboard import admin_command, handle_admin_callback

# ================== LOGGING ==================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ================== KOYEB DUMMY HTTP SERVER ==================
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"OK")

def start_health_server():
    server = HTTPServer(("0.0.0.0", 8000), HealthHandler)
    server.serve_forever()

# Start HTTP server in background thread
threading.Thread(target=start_health_server, daemon=True).start()

# ================== MAIN BOT ==================
async def main():
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE" or not BOT_TOKEN:
        print("=" * 50)
        print("❌ ERROR: Bot token not configured!")
        print("Set BOT_TOKEN in .env or config.py")
        print("=" * 50)
        return

    application = Application.builder().token(BOT_TOKEN).build()

    # -------- Commands --------
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("users", users_command))
    application.add_handler(CommandHandler("get", get_command))
    application.add_handler(CommandHandler("admin", admin_command))

    # -------- ZIP file handler --------
    application.add_handler(
        MessageHandler(
            filters.Document.MimeType("application/zip")
            | filters.Document.FileExtension("zip"),
            handle_zip_file,
        )
    )

    # -------- Normal text messages --------
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message)
    )

    # -------- Callbacks --------
    application.add_handler(
        CallbackQueryHandler(
            handle_admin_callback,
            pattern="^(admin_|ch_|users_|settings_)",
        )
    )
    application.add_handler(CallbackQueryHandler(handle_callback))

    print("=" * 50)
    print("🤖 Bot is starting...")
    print("📡 Using long polling mode (no webhook)")
    print("🌐 Dummy HTTP server running on port 8000 (Koyeb fix)")
    print("=" * 50)

    async with application:
        await application.start()
        await application.updater.start_polling(drop_pending_updates=True)

        # Keep bot alive forever
        await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
