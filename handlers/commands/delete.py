from telegram import Update
from telegram.ext import CallbackContext
from config import EXCEPTION_USER_IDS, DEVELOPERS
from utils.cleardata import delete_all
from database.db_manager import DBManager

# Initialize the database manager
db = DBManager()

async def deluser_command(update: Update, context: CallbackContext):
    chat_type = update.message.chat.type
    id_del = None
    id_del = ' '.join(context.args)

    # Ignore messages from groups, supergroups, and channels
    if chat_type in ["group", "supergroup", "channel"]:
        return
    
    user_id = update.message.from_user.id
    if int(user_id) in DEVELOPERS:
        db.delete_user_data(id_del)
        if id_del:
            await update.message.reply_text(f"✅ User data has been deleted for this {id_del} id.")
        else:
            await update.message.reply_text("✅ All user data has been deleted.")
    else:
        await update.message.reply_text("❌")
        await update.message.reply_text(
            "<b>You are not the Developer. Permission denied.</b>",
            parse_mode='HTML'
        )

async def delfiles_command(update: Update, context: CallbackContext):
    chat_type = update.message.chat.type

    # Ignore messages from groups, supergroups, and channels
    if chat_type in ["group", "supergroup", "channel"]:
        return
    
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