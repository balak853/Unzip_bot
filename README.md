# ZIP Extractor Telegram Bot

A production-ready Telegram bot that extracts ZIP files, manages users, and includes admin features.

## Features

- **Force Channel Join**: Users must join the specified channel before using the bot
- **ZIP File Extraction**: Automatically extracts uploaded ZIP files
- **Media Detection**: Detects videos and images in ZIP files, notifies admin
- **User Management**: Tracks users with JSON storage, notifies admin of new users
- **Admin Commands**: `/users` and `/get` for administrative functions
- **Professional UI**: Inline and reply keyboards for easy navigation

## Quick Setup

### 1. Get Your Bot Token

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` and follow the instructions
3. Copy your bot token

### 2. Get Your Admin ID

1. Open Telegram and search for `@userinfobot`
2. Start the bot to get your user ID

### 3. Configure the Bot

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Edit `.env`:

```
BOT_TOKEN=your_bot_token_here
ADMIN_ID=your_user_id_here
CHANNEL_USERNAME=BALAKXWEBS
```

### 4. Run the Bot

```bash
python bot.py
```

## Bot Commands

### User Commands
- `/start` - Start the bot and see the main menu
- `/help` - Show help information

### Admin Commands (Admin Only)
- `/users` - Show total registered users
- `/get` - Download bot data as ZIP file

## Menu Buttons

- **Upload ZIP** - Instructions for uploading ZIP files
- **Help** - Show help information
- **Rules** - Display bot usage rules
- **Join Channel** - Link to the required channel

## Project Structure

```
.
├── bot.py              # Main entry point
├── config.py           # Configuration settings
├── .env.example        # Environment template
├── handlers/
│   ├── __init__.py
│   ├── commands.py     # Command handlers
│   ├── messages.py     # Message handlers
│   ├── callbacks.py    # Callback query handlers
│   └── keyboards.py    # Keyboard definitions
├── utils/
│   ├── __init__.py
│   ├── user_manager.py # User management functions
│   ├── zip_handler.py  # ZIP file processing
│   └── channel_check.py# Channel membership verification
└── data/               # Created automatically
    ├── users.json      # User database
    ├── extracted/      # Extracted files
    └── logs/           # Log files
```

## Requirements

- Python 3.8+
- python-telegram-bot
- python-dotenv

Install dependencies:

```bash
pip install python-telegram-bot python-dotenv
```

## Channel Setup

For the force-join feature to work, your bot must be an administrator in the channel:

1. Add your bot to the channel as an administrator
2. Grant the bot "See members" permission

## Deployment Options

### Shared Hosting / VPS
1. Upload all files to your server
2. Install Python 3.8+
3. Install dependencies: `pip install -r requirements.txt`
4. Configure `.env` file
5. Run: `python bot.py`

### Keep Running (Linux)
Use `screen` or `tmux`:

```bash
screen -S bot
python bot.py
# Press Ctrl+A, then D to detach
```

Or create a systemd service for production.

## Security Notes

- Never share your bot token
- Keep `.env` file secure and out of version control
- Admin commands are protected by user ID verification
- Extracted files are stored in isolated user directories

## License

This project is provided as-is for educational and personal use.
