import asyncio
import logging
from telegram import Update
from telegram.ext import CallbackContext
from config import EXCEPTION_USER_IDS, DEVELOPERS
from downloader.song import download_song
from utils.acrcloud import get_song_info
from utils.send_file import sendsong
from utils.cleardata import delete_cache, delete_files
from database.db_manager import DBManager
from decorator.rate_limiter import RateLimiter
from decorator.membership import membership_check_decorator
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup

# Initialize the database manager
db = DBManager()

# Initialize the rate limiter (1 request per 60 seconds)
rate_limiter = RateLimiter(limit=1, interval=60, exception_user_ids=EXCEPTION_USER_IDS)

@membership_check_decorator()
@rate_limiter.rate_limit_decorator(user_id_arg_name="user_id")
async def search_command(update: Update, context: CallbackContext):
    try:
        user_id = update.message.from_user.id
        user_name = update.message.from_user.full_name
        user_input = update.message.text
        chat_type = update.message.chat.type

        # Ignore messages from groups, supergroups, and channels
        if chat_type in ["group", "supergroup", "channel"]:
            return

        # Add the user to the database if they don't exist
        if not db.user_exists(user_id):
            db.add_user(user_id, user_name)

        # Log the user's input
        db.log_input(user_id, user_input)

        # Check for empty arguments
        if len(context.args) == 0:
            await update.message.reply_text(
                "🎵 Wanna find a song?\n\n Use: /search <song title> or /search <song title> - <artist name> 🔍✨"
            )
            return

        # Process user input
        full_input = ' '.join(context.args)
        if '-' in full_input:
            title, artists = map(str.strip, full_input.split('-', 1))
        else:
            title = full_input
            artists = ''

        try:
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
            logging.error(f"Something went wrong while searching for the song: {e}")
            await downloading_message.edit_text(f"⚠️ Something went wrong while searching for the song: {str(e)}")
            return

        try:
            song_title = song_data.get('title')
            song_artist = song_data.get('artists')
            song_album = song_data.get('album', 'Unknown')
            song_release_date = song_data.get('release_date', 'Unknown')
            youtube_link = song_data.get('youtube_link')
            spotify_link = song_data.get('spotify_link')

            await downloading_message.edit_text(
                "⬇️ <b>Getting your jam...</b> 🎶🚀",
                parse_mode='HTML',
            )
            song_path = await asyncio.to_thread(download_song, song_title, song_artist)

            response_message = (
                f"🎶 <b>Found the track: {song_title}</b>\n\n"
                f"✨ <b>Artists:</b> {song_artist}\n"
                f"🎧 <b>Album:</b> {song_album}\n"
                f"📅 <b>Release Date:</b> {song_release_date}\n\n"
                "<a href='https://t.me/ProjectON3'>ProjectON3</a>"
            )

            keyboard = [
                [InlineKeyboardButton("YouTube", url=youtube_link), InlineKeyboardButton("Spotify", url=spotify_link)],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            if song_path:
                await sendsong(update, downloading_message, response_message, youtube_link, spotify_link, song_path)
            else:
                await downloading_message.delete()
                await update.message.reply_text(
                        text=(  # Error message when the file exceeds the limit
                            "🚫 <b>Song file not found.</b> I found the song but couldn't fetch the file 🥲\n\n"
                            "But no worries, here’s all the details and the play buttons! 🎧🎶\n\n" + response_message
                        ),
                        reply_markup=reply_markup,
                        parse_mode='HTML',
                        reply_to_message_id=update.message.message_id
                    )
        except Exception as e:
            logging.error(f"Something went wrong while sending the song: {e}")
    except Exception as e:
        logging.error(f"Error processing search command: {e}")
    finally:
        try:
            delete_cache()
            delete_files(song_path)
        except Exception as e:
            logging.error(f"Error deleting: {e}")