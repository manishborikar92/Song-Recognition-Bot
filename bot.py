import os
import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from handlers.command import start, help
from handlers.message import handle_message

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Get a logger instance
logger = logging.getLogger(__name__)

# Suppress unnecessary logs from the Telegram API and its dependencies
logging.getLogger("telegram").setLevel(logging.WARNING)  # For the main telegram logger
logging.getLogger("telegram.bot").setLevel(logging.WARNING)  # For bot-specific logs
logging.getLogger("telegram.request").setLevel(logging.WARNING)  # For request-related logs
logging.getLogger("telegram.vendor.ptb_urllib3").setLevel(logging.WARNING)  # For telegram's urllib3 logs
logging.getLogger("httpx").setLevel(logging.WARNING)  # For httpx logs (since telegram internally uses httpx)
logging.getLogger("urllib3").setLevel(logging.WARNING)  # For general HTTP requests
        
# Main function
def main():
    BOT_TOKEN = os.getenv("BOT_TOKEN")

    if not BOT_TOKEN:
        logger.error("❌ Missing BOT_TOKEN. Check your .env file.")
        return

    application = ApplicationBuilder().token(BOT_TOKEN).concurrent_updates(True).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.VIDEO | filters.AUDIO | filters.VOICE, handle_message))

    logging.info("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
