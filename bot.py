import os
import time
import asyncio
import logging
import re
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
logging.basicConfig(level=logging.CRITICAL, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Start command handler
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "🎵 <b>Hello there!</b> I’m <b>@TuneDetectBot</b>, your personal music detective powered by <a href='https://t.me/ProjectON3'>ProjectON3</a>. 🎶\n\n"
        "✨ Simply send me a <b>URL</b>, upload a <b>file</b>, or send a <b>voice message</b>, and I'll work my magic to identify the song for you! 🚀",
        parse_mode='HTML'
    )



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
            await update.message.reply_text(
                f"⏳ <b>Please wait {remaining_time:.0f} seconds</b> before making another request.",
                parse_mode='HTML'
            )
            return

        # Update the last request time for the user
        last_request_time[user_id] = current_time      

    bot_token = context.bot.token

    try:
        is_member = await check_membership(user_id, bot_token)
    except Exception as e:
        print(f"Error checking membership: {e}")
        await update.message.reply_text(
            "<b>Oops!</b> 😔 I’m unable to verify your membership at the moment. <i>Please try again later.</i> ⏳",
            parse_mode='HTML',  # Use HTML formatting
            reply_to_message_id=update.message.message_id
        )
        return

    if not is_member:
        buttons = [
            [InlineKeyboardButton("Join Group", url=GROUP_URL)],
            [InlineKeyboardButton("Join Channel", url=CHANNEL_URL)],
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await update.message.reply_text(
            "🚫 <b>You must join our group and channel to use this bot.</b> Please join using the buttons below and try again. 🙏",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        return

    try:
        # Use TemporaryDirectory for temporary file storage
        with TemporaryDirectory() as temp_dir:

            # Determine input type
            if update.message.text:  # URL input
                url = update.message.text
                if re.match(r"^https?://(www\.)?instagram\.com/.*$", url):
                    downloading_message = await update.message.reply_text(
                        "<b>⬇️ Downloading Instagram Reel...</b> <i>Hang tight! This won't take long. 🚀</i>",
                        parse_mode='HTML',  # Use HTML formatting
                        reply_to_message_id=update.message.message_id
                    )
                    video_path, caption = await asyncio.to_thread(download_instagram_reel, url)

                    if not video_path or not caption:
                        await downloading_message.edit_text(
                        "❌ <b>Invalid URL!</b> Please provide a valid <b>Instagram</b> link. 🌐🔗",
                        parse_mode='HTML'
                        )
                        raise Exception("Failed to fetch Instagram video.")

                    with open(video_path, "rb") as video:
                        await update.message.reply_video(video=video, caption=caption)

                elif re.match(r"^https?://(www\.)?(youtube\.com|youtu\.be)/.*$", url):
                    if "/shorts" in url:
                        downloading_message = await update.message.reply_text(
                            "<b>⬇️ Downloading YouTube Short...</b> <i>Hang tight! This won't take long. 🚀</i>",
                            parse_mode='HTML',
                            reply_to_message_id=update.message.message_id
                        )
                    else:
                        downloading_message = await update.message.reply_text(
                            "<b>⬇️ Downloading YouTube Video...</b> <i>Hang tight! This won't take long. 🚀</i>",
                            parse_mode='HTML',
                            reply_to_message_id=update.message.message_id
                        )
                        
                    video_path, caption = await asyncio.to_thread(download_youtube_video, url)

                    if not video_path or not caption:
                        await downloading_message.edit_text(
                        "❌ <b>Invalid URL!</b> Please provide a valid <b>Youtube</b> link. 🌐🔗",
                        parse_mode='HTML'
                        )
                        raise Exception("Failed to fetch YouTube video.")

                    # Check file size
                    file_size_mb = os.path.getsize(video_path) / (1024 * 1024)  # Convert bytes to MB
                    if file_size_mb > 50:  # File size exceeds 50MB
                       await update.message.reply_text(
                            "<b>🚫 Oops!</b> I can't send video because Telegram Bot has a <b>50MB limit</b>. 📉 "
                            "But don't worry, I'm here to help with <b>other formats</b>! 🎵",
                            parse_mode='HTML',
                            reply_to_message_id=update.message.message_id
                        )
                    else:
                        # Send the video if it's within the limit
                        with open(video_path, "rb") as video:
                            await update.message.reply_video(video=video, caption=caption)   
                
                elif re.match(r"^https?://(www\.)?([\w.-]+)(/.*)?$", url):
                    await update.message.reply_text(
                        "❌ <b>Invalid URL!</b> Please provide a valid <b>Instagram</b> or <b>YouTube</b> link. 🌐🔗",
                        parse_mode='HTML',
                        reply_to_message_id=update.message.message_id
                    )
                    return
                
                else:
                    await update.message.reply_text(
                        "🚫 <b>Hey!</b> Please don't send me text messages. Instead, send me a <b>link</b>, <b>video</b>, <b>audio</b>, or <b>voice message</b> 🎶📹🎤, and I'll process it for you!",
                        parse_mode='HTML',
                        reply_to_message_id=update.message.message_id
                    )
                    return

            elif update.message.video:  # Video file input
                downloading_message = await update.message.reply_text(
                    "🎬 <b>Processing your uploaded video...</b> <i>Please wait while I work my magic!</i> ✨",
                    parse_mode='HTML',
                    reply_to_message_id=update.message.message_id
                )
                video = update.message.video
                file = await context.bot.get_file(video.file_id)
                video_path = os.path.join(temp_dir, f"{video.file_id}.mp4")
                await file.download_to_drive(custom_path=video_path)
                caption = None

            elif update.message.audio or update.message.voice:  # Audio file input
                downloading_message = await update.message.reply_text(
                    "🎶 <b>Processing your uploaded audio...</b> <i>Please hold on while I analyze the sound!</i> 🎧✨",
                    parse_mode='HTML',
                    reply_to_message_id=update.message.message_id
                )
                audio = update.message.audio or update.message.voice
                file = await context.bot.get_file(audio.file_id)
                audio_path = os.path.join(temp_dir, f"{audio.file_id}.mp3")
                await file.download_to_drive(custom_path=audio_path)

            else:
                await update.message.reply_text(
                    "❌ <b>Unsupported input type</b>. Please send a valid <b>URL</b>, <b>video</b>, or <b>audio</b> 🎶📹🔗 so I can assist you! 💡",
                    parse_mode='HTML',
                    reply_to_message_id=update.message.message_id
                )
                return

            # Extract audio if video was provided
            if "video_path" in locals():
                await downloading_message.edit_text(
                    "🎧 <b>Video downloaded!</b> Now <i>extracting audio...</i> 🎶🔊",
                    parse_mode='HTML'
                )
                audio_path = await asyncio.to_thread(convert_video_to_mp3, video_path)

            # Recognize song
            await downloading_message.edit_text(
                "🔍 <b>Recognizing song...</b> 🎶🎧",
                parse_mode='HTML'
            )
            song_info = await asyncio.to_thread(recognize_song, audio_path, acr_host, acr_access_key, acr_access_secret)

            if not song_info or "metadata" not in song_info or not song_info["metadata"].get("music"):
                await downloading_message.edit_text(
                    "❌ <b>Failed to recognize the song.</b> Please try again later. 🎶😞",
                    parse_mode='HTML'
                )

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
            await downloading_message.edit_text(
                "⬇️ <b>Downloading song...</b> 🎶🚀",
                parse_mode='HTML'
            )
            song_path = await asyncio.to_thread(download_song, title, artists)

            if not song_path:
                await update.message.reply_text(
                    "🚫 <b>Song file not found.</b> This could happen when song recognized but file not found on web 🥲",
                    parse_mode='HTML'
                )

            # Send response
            keyboard = [
                [InlineKeyboardButton("YouTube", url=youtube_link), InlineKeyboardButton("Spotify", url=spotify_link)],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            response_message = (
                f"🎶 <b>Song Found: {title}</b>\n\n"
                f"✨ <b>Artists:</b> {artists}\n"
                f"🎧 <b>Album:</b> {album}\n"
                f"🎶 <b>Genres:</b> {genres}\n"
                f"📅 <b>Release Date:</b> {release_date}\n\n"
                "👇 Listen and enjoy the song below!  🎶"
            )

            # Check file size
            file_size_mb = os.path.getsize(song_path) / (1024 * 1024)  # Convert bytes to MB
            if file_size_mb > 50:  # File size exceeds 50MB
                await downloading_message.delete()
                await update.message.reply_text(
                    text=(
                        "<b>🚫 Oops!</b> I can't send the song because Telegram Bot has a <b>50MB limit</b>. 📉\n\n"
                        "But don't worry, here is the song info and play buttons! 🎵\n\n" + response_message
                    ),
                    reply_markup=reply_markup,
                    parse_mode='HTML',
                    reply_to_message_id=update.message.message_id
                )
            else:
                # Send the audio if it's within the limit
                with open(song_path, "rb") as song_file:
                    await downloading_message.delete()
                    await update.message.reply_audio(
                        audio=song_file,
                        caption=response_message,
                        reply_markup=reply_markup,
                        parse_mode="HTML"
                    )

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
