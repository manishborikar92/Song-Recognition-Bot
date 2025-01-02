import os
from telegram import Update
from telegram.ext import CallbackContext
from config import EXCEPTION_USER_IDS, DEVELOPERS
from utils.cleardata import delete_all
from utils.pdf_generator import create_pdf
from database.db_manager import DBManager

# Initialize the database manager
db = DBManager()

async def deluser_command(update: Update, context: CallbackContext):
    chat_type = update.message.chat.type
    id_del = None
    
    if context.args:
        id_del = ' '.join(context.args)

    # Ignore messages from groups, supergroups, and channels
    if chat_type in ["group", "supergroup", "channel"]:
        return
    
    user_id = update.message.from_user.id
    
    if int(user_id) in DEVELOPERS:
        if id_del:
            # Deleting specific user's data
            db.delete_user_data(id_del)
            await update.message.reply_text(f"✅ User data has been deleted for {id_del}.")
        else:
            # # Deleting all user data
            # db.delete_user_data()  # Assuming this deletes all data when no ID is provided
            await update.message.reply_text("❌ Please provide a user ID.")
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

        # save_dir = 'data/pdf'
        # os.makedirs(save_dir, exist_ok=True)

        # content = [(key, value) for key, value in results.items()]
        # headers = ["Folder", "Status"]
        # pdf_path = f"{save_dir}/deletion_summary.pdf"
        # create_pdf(pdf_path, "Deletion Summary", headers, content)

        # await update.message.reply_document(
        #     document=open(pdf_path, 'rb'),
        #     filename=pdf_path,
        #     caption="📄 Deletion Summary"
        # )
        # os.remove(pdf_path)

        message = "<b>Deletion Summary:</b>\n\n"
        for folder, status in results.items():
            message += f"• {folder}: {status.capitalize()}\n\n"
        await update.message.reply_text(message, parse_mode='HTML')
        await update.message.reply_text("✅ All storage data has been deleted.")
    else:
        await update.message.reply_text("❌")
        await update.message.reply_text(
            "<b>You are not the Developer. Permission denied.</b>",
            parse_mode='HTML'
        )