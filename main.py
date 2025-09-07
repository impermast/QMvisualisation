from bot.telegram_listener import TelegramListener
from bot.tg_bot import load_telegram_config
import os

if __name__ == "__main__":
    print("Starting Telegram Bot...")
    
    # Ensure environment variables are set for Render deployment
    # Render will provide these as environment variables
    # For local testing, you might still use config.json or set them manually
    token, chat_id = load_telegram_config() # This will try to load from config.json first

    if not token:
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not token:
            print("Error: TELEGRAM_BOT_TOKEN environment variable not set.")
            exit(1)
    
    if not chat_id:
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        if not chat_id:
            print("Error: TELEGRAM_CHAT_ID environment variable not set.")
            exit(1)

    # Instantiate and run the bot
    listener = TelegramListener()
    application = listener.run() # This now returns the Application instance
    application.run_polling()