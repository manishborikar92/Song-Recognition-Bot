from telegram import Update
from telegram.ext import CallbackContext
from config import EXCEPTION_USER_IDS, DEVELOPERS
from utils.cleardata import delete_all
from database.db_manager import DBManager

# Initialize the database manager
db = DBManager()

async def deluser_command(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if int(user_id) in DEVELOPERS:
        db.delete_user_data()
        await update.message.reply_text("✅ All user data has been deleted.")
    else:
        await update.message.reply_text("❌")
        await update.message.reply_text(
            "<b>You are not the Developer. Permission denied.</b>",
            parse_mode='HTML'
        )

async def delfiles_command(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if int(user_id) in DEVELOPERS:
        results = delete_all()
        message = "<b>Deletion Summary:</b>\n\n"
        for folder, status in results.items():
            message += f"• {folder}: {status.capitalize()}\n\n"
        await update.message.reply_text(message, parse_mode='HTML')
        await update.message.reply_text("✅ All user data has been deleted.")
    else:
        await update.message.reply_text("❌")
        await update.message.reply_text(
            "<b>You are not the Developer. Permission denied.</b>",
            parse_mode='HTML'
        )