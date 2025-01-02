import os
from telegram import Update
from telegram.ext import CallbackContext
from config import EXCEPTION_USER_IDS
from database.db_manager import DBManager

# Initialize the database manager
db = DBManager()

# Start command handler
async def start_command(update: Update, context: CallbackContext):
    chat_type = update.message.chat.type

    # Ignore messages from groups, supergroups, and channels
    if chat_type in ["group", "supergroup", "channel"]:
        return
    
    user_id = update.message.from_user.id
    user_name = update.message.from_user.full_name
    db.add_user(user_id, user_name)

    await update.message.reply_text(
        "🎵 <b>Hello there!</b> I’m <b>@TuneDetectBot</b>, your personal music detective powered by <a href='https://t.me/ProjectON3'>ProjectON3</a>. 🎶\n\n"
        "✨ Simply send me a <b>URL</b>, upload a <b>file</b>, or send a <b>voice message</b>, and I'll work my magic to identify the song for you! 🚀",
        parse_mode='HTML'
    )


async def help_command(update: Update, context: CallbackContext):
    chat_type = update.message.chat.type

    # Ignore messages from groups, supergroups, and channels
    if chat_type in ["group", "supergroup", "channel"]:
        return
    
    user_id = update.message.from_user.id
    user_name = update.message.from_user.full_name

    if not db.user_exists(user_id):
        db.add_user(user_id, user_name)
        
    if int(user_id) in EXCEPTION_USER_IDS:
        help_text = (
            "<b>🔊 Song Recognition Bot Help</b>\n\n"
            "Here are the available commands and their usage:\n\n"
            "- <b>/start</b> - Start the bot and get a welcome message. 🤖✨\n"
            "- <b>/help</b> - Display this help message. ❓📖\n"
            "- <b>/search</b> - Search for a song by name or artist (e.g., 'song name - artist name'). 🔍🎶\n"
            "- 📹 Share a video, audio, or voice message - The bot will recognize the song and provide details. 🎧🎵\n"
            "- 🌐 Send a YouTube or Instagram link - The bot will download the video, analyze it, and identify the song. 🎥🎶\n"
            "- <b>/history</b> - View your own message history (Admin only). 📜\n"
            "- <b>/broadcast</b> - Send a message to all users (Admin only). 📢\n"
            "- <b>/getusers</b> - Retrieve all user IDs and names (Admin only). 🧾\n"
            "- <b>/getinfo</b> - Fetch user history (Developer only). 📄\n"
            "- <b>/deluser</b> - Clear specific or all user data (Developer only). 🗑\n"
            "- <b>/delfiles</b> - Clear all media files and cache. (Developer only). 📁🗑\n\n"
            "<a href='https://t.me/ProjectON3'>ProjectON3</a>"
        )
        await update.message.reply_text(help_text, parse_mode="HTML")

    else:
        help_text = (
            "<b>🔊 Song Recognition Bot Help</b>\n\n"
            "Here are the available commands and their usage:\n\n"
            "- <b>/start</b> - Start the bot and get a welcome message. 🤖✨\n"
            "- <b>/help</b> - Display this help message. ❓📖\n"
            "- <b>/search</b> - Search for a song by name or artist (e.g., 'song name - artist name'). 🔍🎶\n"
            "- 📹 Share a video, audio, or voice message - The bot will recognize the song and provide details. 🎧🎵\n"
            "- 🌐 Send a YouTube or Instagram link - The bot will download the video, analyze it, and identify the song. 🎥🎶\n\n"
            "For support or issues, feel free to contact the developer! 😊\n"
            "<a href='https://t.me/ProjectON3'>ProjectON3</a>"
        )
        
        # Send the help text as a message to the user
        await update.message.reply_text(help_text, parse_mode="HTML")