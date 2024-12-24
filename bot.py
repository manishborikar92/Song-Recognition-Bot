import os
import time
import asyncio
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext
from downloader.instagram import download_instagram_reel
from downloader.song_downloader import download_song
from downloader.youtube import download_youtube_video
from utils.acrcloud_handler import recognize_song
from utils.audio_extractor import convert_video_to_mp3
from utils.clear_data import delete_all
from tempfile import TemporaryDirectory

# Load environment variables from .env file
load_dotenv()

# Group and Channel IDs
GROUP_ID = os.getenv("GROUP_ID")
CHANNEL_ID = os.getenv("CHANNEL_ID")
EXCEPTION_USER_ID = os.getenv("EXCEPTION_USER_ID")
GROUP_URL = "https://t.me/+b4-OKLiKbMoyODY1"
CHANNEL_URL = "https://t.me/ProjectON3"

# Rate limit settings
USER_RATE_LIMIT = 60  # Allow 1 request per minute per user
last_request_time = {}

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Start command handler
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Hi! I’m your music bot. Send me a URL or upload a file, and I'll process it for you!")

async def check_membership(user_id: int, bot_token: str):
    application = ApplicationBuilder().token(bot_token).build()
    try:
        # Run group and channel checks concurrently
        group_check = application.bot.get_chat_member(chat_id=GROUP_ID, user_id=user_id)
        channel_check = application.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        
        group_status, channel_status = await asyncio.gather(group_check, channel_check)

        # Check if the user is a member in both group and channel
        is_member_of_group = group_status.status in ["member", "administrator", "creator"]
        is_member_of_channel = channel_status.status in ["member", "administrator", "creator"]
        
        return is_member_of_group and is_member_of_channel
    except Exception as e:
        print(f"Error during membership check: {e}")
        return False  # Assume not a member if an error occurs
    
# Handle user messages
async def handle_message(update: Update, context: CallbackContext):
    acr_host = os.getenv("ACR_HOST")
    acr_access_key = os.getenv("ACR_ACCESS_KEY")
    acr_access_secret = os.getenv("ACR_ACCESS_SECRET")
    downloading_message = None

    user_id = update.message.from_user.id
    chat_type = update.message.chat.type

    # Ignore messages from groups, supergroups, and channels
    if chat_type in ["group", "supergroup", "channel"]:
        return

    # Check if the user is the exception user
    if int(user_id) == int(EXCEPTION_USER_ID):
        print('Admin')  # Log admin behavior
    else:
        # Rate-limiting logic for other users
        current_time = time.time()
        if user_id in last_request_time and current_time - last_request_time[user_id] < USER_RATE_LIMIT:
            remaining_time = USER_RATE_LIMIT - (current_time - last_request_time[user_id])
            await update.message.reply_text(f"⏳ Please wait {remaining_time:.0f} seconds before making another request.")
            return

        # Update the last request time for the user
        last_request_time[user_id] = current_time      

    bot_token = context.bot.token

    try:
        is_member = await check_membership(user_id, bot_token)
    except Exception as e:
        print(f"Error checking membership: {e}")
        await update.message.reply_text("Unable to verify membership at the moment. Please try again later.")
        return

    if not is_member:
        buttons = [
            [InlineKeyboardButton("Join Group", url=GROUP_URL)],
            [InlineKeyboardButton("Join Channel", url=CHANNEL_URL)],
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await update.message.reply_text(
            "🚫 You must join our group and channel to use this bot. Please join using the buttons below and try again.",
            reply_markup=reply_markup,
        )
        return

    try:
        # Use TemporaryDirectory for temporary file storage
        with TemporaryDirectory() as temp_dir:

            # Determine input type
            if update.message.text:  # URL input
                url = update.message.text
                if "instagram.com" in url:
                    downloading_message = await update.message.reply_text("⬇️ Downloading Instagram video...")
                    video_path, caption = await asyncio.to_thread(download_instagram_reel, url)

                    if not video_path or not caption:
                        raise Exception("Failed to fetch Instagram video.")

                    with open(video_path, "rb") as video:
                        await update.message.reply_video(video=video, caption=caption)

                elif "youtube.com" in url or "youtu.be" in url:
                    downloading_message = await update.message.reply_text("⬇️ Downloading YouTube video...")
                    video_path, caption = await asyncio.to_thread(download_youtube_video, url)

                    if not video_path or not caption:
                        raise Exception("Failed to fetch YouTube video.")

                    with open(video_path, "rb") as video:
                        await update.message.reply_video(video=video, caption=caption)
                else:
                    await update.message.reply_text("❌ Invalid URL. Please provide a valid Instagram or YouTube link.")
                    return

            elif update.message.video:  # Video file input
                downloading_message = await update.message.reply_text("⬇️ Processing uploaded video...")
                video = update.message.video
                file = await context.bot.get_file(video.file_id)
                video_path = os.path.join(temp_dir, f"{video.file_id}.mp4")
                await file.download_to_drive(custom_path=video_path)
                caption = None

            elif update.message.audio or update.message.voice:  # Audio file input
                downloading_message = await update.message.reply_text("⬇️ Processing uploaded audio...")
                audio = update.message.audio or update.message.voice
                file = await context.bot.get_file(audio.file_id)
                audio_path = os.path.join(temp_dir, f"{audio.file_id}.mp3")
                await file.download_to_drive(custom_path=audio_path)

            else:
                await update.message.reply_text("❌ Unsupported input type. Please send a valid URL, video, or audio.")
                return

            # Extract audio if video was provided
            if "video_path" in locals():
                await downloading_message.edit_text("🎧 Video downloaded! Extracting audio...")
                audio_path = await asyncio.to_thread(convert_video_to_mp3, video_path)

            # Recognize song
            await downloading_message.edit_text("🔍 Recognizing song...")
            song_info = await asyncio.to_thread(recognize_song, audio_path, acr_host, acr_access_key, acr_access_secret)

            if not song_info or "metadata" not in song_info or not song_info["metadata"].get("music"):
                raise Exception("Failed to recognize the song.")

            # Extract song metadata
            song = song_info["metadata"]["music"][0]
            title = song.get("title", "Unknown Title")
            artists = ", ".join(artist["name"] for artist in song.get("artists", []))
            album = song.get("album", {}).get("name", "Unknown Album")
            genres = ", ".join(genre["name"] for genre in song.get("genres", []))
            release_date = song.get("release_date", "Unknown Release Date")

            youtube_track_id = song.get("external_metadata", {}).get("youtube", {}).get("vid", "")
            youtube_link = f"https://www.youtube.com/watch?v={youtube_track_id}" if youtube_track_id else f"https://www.youtube.com/results?search_query={title}"

            spotify_track_id = song.get("external_metadata", {}).get("spotify", {}).get("track", {}).get("id", "")
            spotify_link = f"https://open.spotify.com/track/{spotify_track_id}" if spotify_track_id else f"https://open.spotify.com/search/{title}"

            # Download song
            await downloading_message.edit_text("⬇️ Downloading song...")
            song_path = await asyncio.to_thread(download_song, title, artists)

            # Send response
            keyboard = [
                [InlineKeyboardButton("YouTube", url=youtube_link), InlineKeyboardButton("Spotify", url=spotify_link)],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            response_message = (
                f"🎶 **Song Found: {title}**\n\n"
                f"- Artists: {artists}\n"
                f"- Album: {album}\n"
                f"- Genres: {genres}\n"
                f"- Release Date: {release_date}\n"
            )

            with open(song_path, "rb") as song_file:
                await downloading_message.delete()
                await update.message.reply_audio(audio=song_file, caption=response_message, reply_markup=reply_markup, parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Error: {e}")

    finally:
        delete_all()
        
# Main function
def main():
    BOT_TOKEN = os.getenv("BOT_TOKEN")

    if not BOT_TOKEN:
        logger.error("❌ Missing BOT_TOKEN. Check your .env file.")
        return

    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.VIDEO | filters.AUDIO | filters.VOICE, handle_message))

    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
