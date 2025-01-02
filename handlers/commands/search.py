import asyncio
import logging
from telegram import Update
from telegram.ext import CallbackContext
from config import EXCEPTION_USER_IDS, DEVELOPERS
from downloader.song import download_song
from utils.acrcloud import get_song_info
from utils.send_file import sendsong
from utils.cleardata import delete_cache, delete_file
from database.db_manager import DBManager


# Initialize the database manager
db = DBManager()

async def search_command(update: Update, context: CallbackContext):
    try:
        user_id = update.message.from_user.id
        user_name = update.message.from_user.full_name
        user_input = update.message.text

        if not db.user_exists(user_id):
            db.add_user(user_id, user_name)

        db.log_input(user_id, user_input)

        if len(context.args) == 0:
            await update.message.reply_text("🎵 Wanna find a song?\n\n Use: /search <song title> or /search <song title> - <artist name> 🔍✨")
            return

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

            if not song_path:
                await update.message.reply_text(
                    "🚫 <b>Song file not found.</b> I found the song but couldn't fetch the file 🥲",
                    parse_mode='HTML'
                )
                return

            await sendsong(update, downloading_message, song_title, song_artist, song_album, song_release_date, youtube_link, spotify_link, song_path)
        except Exception as e:
            logging.error(f"Something went wrong while sending the song: {e}")
    except Exception as e:
        logging.error(f"Error processing message: {e}")
    finally:
        delete_file(song_path)
        delete_cache()