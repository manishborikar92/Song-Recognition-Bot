import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CallbackContext
from config import EXCEPTION_USER_IDS
from downloader.song import download_song
from utils.acrcloud import get_song_info
from utils.cleardata import delete_all


# Start command handler
async def start_command(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "🎵 <b>Hello there!</b> I’m <b>@TuneDetectBot</b>, your personal music detective powered by <a href='https://t.me/ProjectON3'>ProjectON3</a>. 🎶\n\n"
        "✨ Simply send me a <b>URL</b>, upload a <b>file</b>, or send a <b>voice message</b>, and I'll work my magic to identify the song for you! 🚀",
        parse_mode='HTML'
    )

async def help_command(update: Update, context: CallbackContext):
    help_text = (
        "<b>🔊 Song Recognition Bot Help</b>\n\n"
        "Here are the available commands and their usage:\n\n"
        "- <b>/start</b> - Start the bot and get a welcome message. 🤖✨\n"
        "- <b>/help</b> - Display this help message. ❓📖\n"
        "- <b>/search</b> - Search for a song by name or artist (e.g., 'song name artist name'). 🔍🎶\n"
        "- 📹 Share a video, audio, or voice message - The bot will recognize the song and provide details. 🎧🎵\n"
        "- 🌐 Send a YouTube or Instagram link - The bot will download the video, analyze it, and identify the song. 🎥🎶\n\n"
        "For support or issues, feel free to contact the developer! 😊\n\n"
        "<a href='https://t.me/ProjectON3'>ProjectON3</a>"
    )
    
    # Send the help text as a message to the user
    await update.message.reply_text(help_text, parse_mode="HTML")

async def search_command(update: Update, context: CallbackContext):
    """
    Handles the /search command to find and return matching songs from AcrCloud and download it.
    """
    downloading_message = None
    if len(context.args) == 0:
        await update.message.reply_text("🎵 Wanna find a song?\n\n Use: /search <song title> or /search <song title> <artist name> 🔍✨")
        return

    # Combine arguments and separate the title and artists by comma
    full_input = ' '.join(context.args)  # Join args in case there are multiple words in the title or artist
    if ',' in full_input:
        title, artists = map(str.strip, full_input.split(',', 1))  # Split on the first comma
    else:
        title = full_input
        artists = ''  # If no artists provided, leave it empty

    # Search the song on AcrCloud
    try:
        # Recognize song
        downloading_message = await update.message.reply_text(
            "🔍 <b>Hunting for the track...</b> 🎶🎧",
            parse_mode='HTML',
            reply_to_message_id=update.message.message_id
        )
        song_data = await asyncio.to_thread(get_song_info, title, artists)
        if not song_data:
            await downloading_message.edit_text("❌ Oops! No matching song found.")
            return
    except Exception as e:
        await downloading_message.edit_text(f"⚠️ Something went wrong while searching for the song: {str(e)}")
        print(f"Error searching for the song: {str(e)}")
        return

    # Song details
    song_title = song_data.get('title')
    song_artist = song_data.get('artists')
    song_album = song_data.get('album', 'Unknown')
    song_release_date = song_data.get('release_date', 'Unknown')
    youtube_link = song_data.get('youtube_link')
    spotify_link = song_data.get('spotify_link')

    # Download song
    await downloading_message.edit_text(
        "⬇️ <b>Getting your jam...</b> 🎶🚀",
        parse_mode='HTML',
    )
    song_path = await asyncio.to_thread(download_song, song_title, song_artist)

    if not song_path:
        await update.message.reply_text(
            "🚫 <b>Song file not found.</b> I found the song but couldn't fetch the file 🥲",
            parse_mode='HTML'
        )
        return

    # Prepare the message with the song details and links
    response_message = (
        f"🎶 <b>Found the track: {song_title}</b>\n\n"
        f"✨ <b>Artists:</b> {song_artist}\n"
        f"🎧 <b>Album:</b> {song_album}\n"
        f"📅 <b>Release Date:</b> {song_release_date}\n\n"
        "<a href='https://t.me/ProjectON3'>ProjectON3</a>"
    )

    print(f"YouTube Link: {youtube_link}")
    print(f"Spotify Link: {spotify_link}")

    keyboard = [
        [InlineKeyboardButton("YouTube", url=youtube_link), InlineKeyboardButton("Spotify", url=spotify_link)],
    ]


    reply_markup = InlineKeyboardMarkup(keyboard)

    # Check file size
    file_size_mb = os.path.getsize(song_path) / (1024 * 1024)  # Convert bytes to MB
    print(f"File size: {file_size_mb:.2f} MB")  # Debugging log

    if file_size_mb < 50:  # File size is within the limit
        try:
            with open(song_path, "rb") as song_file:
                print(f"Sending file: {song_path}")  # Debugging log
                await downloading_message.delete()
                await update.message.reply_audio(
                    audio=song_file,
                    caption=response_message,
                    reply_markup=reply_markup,
                    parse_mode="HTML"
                )
            print("Song sent successfully.")  # Debugging log
        except Exception as e:
            print(f"Error sending audio: {e}")
            await update.message.reply_text("⚠️ Oops! Something went wrong while sending the song.")
    else:
        try:
            print("File exceeds 50MB limit.")
            await downloading_message.delete()
            await update.message.reply_text(
                text=(  # Error message when the file exceeds the limit
                    "<b>🚫 Uh-oh!</b> I can't send the song because it's too big (>50MB). 📉\n\n"
                    "But no worries, here’s all the details and the play buttons! 🎧🎶\n\n" + response_message
                ),
                reply_markup=reply_markup,
                parse_mode='HTML',
                reply_to_message_id=update.message.message_id
            )
        except Exception as e:
            print(f"Error sending audio: {e}")
    
        finally:
            delete_all()

async def delete_command(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if int(user_id) in EXCEPTION_USER_IDS:
        if delete_all():
            await update.message.reply_text(
                "<b>Data Deleted</b> 🗑",
                parse_mode='HTML'
            )
    else:
        await update.message.reply_text("❌")
        await update.message.reply_text("<b>You are not the owner. Permission denied.</b>", parse_mode='HTML')