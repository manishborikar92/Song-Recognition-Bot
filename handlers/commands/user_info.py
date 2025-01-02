import os
from telegram import Update
from telegram.ext import CallbackContext
from config import EXCEPTION_USER_IDS, DEVELOPERS
from utils.pdf_generator import create_pdf
from database.db_manager import DBManager

# Initialize the database manager
db = DBManager()

async def getusers_command(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if int(user_id) in EXCEPTION_USER_IDS:
        users = db.get_all_users()
        if not users:
            await update.message.reply_text("❌ No users found.")
            return

        # Directory to save videos
        save_dir = 'data/pdf'
        os.makedirs(save_dir, exist_ok=True)
            
        content = [(u[0], u[1] or None) for u in users]  # Extract User ID and Name
        headers = ["User ID", "Name"]
        pdf_path = f"{save_dir}/registered_users.pdf"
        create_pdf(pdf_path, "Registered Users", headers, content)

        await update.message.reply_document(
            document=open(pdf_path, 'rb'),
            filename=pdf_path,
            caption="📄 Registered Users"
        )
        os.remove(pdf_path)
    else:
        await update.message.reply_text("❌ You do not have permission to use this command.")


async def getinfo_command(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if int(user_id) in DEVELOPERS:
        if not context.args:
            await update.message.reply_text("❌ Please provide a user ID.")
            return

        target_user_id = int(context.args[0])
        history = db.get_user_history(target_user_id)
        if not history:
            await update.message.reply_text("❌ No history found for the specified user.")
            return

        # Directory to save videos
        save_dir = 'data/pdf'
        os.makedirs(save_dir, exist_ok=True)

        content = [(h[0], h[1]) for h in history]
        headers = ["Input", "Date and Time"]
        pdf_path = f"{save_dir}/user_history_{target_user_id}.pdf"
        create_pdf(pdf_path, "User History", headers, content)

        await update.message.reply_document(
            document=open(pdf_path, 'rb'),
            filename=pdf_path,
            caption="📄 User History"
        )
        os.remove(pdf_path)
    else:
        await update.message.reply_text("❌ You do not have permission to use this command.")

async def history_command(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if int(user_id) in EXCEPTION_USER_IDS:
        history = db.get_user_history(user_id)
        if not history:
            await update.message.reply_text("❌ You have no history recorded.")
            return

        # Directory to save videos
        save_dir = 'data/pdf'
        os.makedirs(save_dir, exist_ok=True)

        content = [(h[0], h[1]) for h in history]
        headers = ["Input", "Date and Time"]
        pdf_path = f"{save_dir}/your_history_{user_id}.pdf"
        create_pdf(pdf_path, "Your History", headers, content)

        await update.message.reply_document(
            document=open(pdf_path, 'rb'),
            filename=pdf_path,
            caption="📄 Your History"
        )
        os.remove(pdf_path)
    else:
        await update.message.reply_text("❌ You do not have permission to use this command.")