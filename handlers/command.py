from telegram import Update
from telegram.ext import CallbackContext

# Start command handler
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "🎵 <b>Hello there!</b> I’m <b>@TuneDetectBot</b>, your personal music detective powered by <a href='https://t.me/ProjectON3'>ProjectON3</a>. 🎶\n\n"
        "✨ Simply send me a <b>URL</b>, upload a <b>file</b>, or send a <b>voice message</b>, and I'll work my magic to identify the song for you! 🚀",
        parse_mode='HTML'
    )

from telegram import Update
from telegram.ext import CallbackContext, CommandHandler

def help(update: Update, context: CallbackContext):
    help_text = (
        "\U0001F50A **Song Recognition Bot Help**\n\n"
        "Here are the available commands and their usage:\n\n"
        "- **/start** - Start the bot and get a welcome message.\n"
        "- **/help** - Display this help message.\n"
        "- **/search <song name, artist name>** - Search for a song by name or artist.\n"
        "- Share a video, audio, or voice message - The bot will recognize the song and provide details.\n"
        "- Send a YouTube or Instagram link - The bot will download the video, analyze it, and identify the song.\n\n"
        "If you encounter any issues, feel free to contact the developer."
    )
    
    # Send the help text as a message to the user
    update.message.reply_text(help_text, parse_mode="Markdown")
