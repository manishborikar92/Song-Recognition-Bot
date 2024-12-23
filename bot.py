import os
import time
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext
from utils.instagram import scrape_instagram_post
from utils.audio_processing import download_video, extract_audio
from utils.acrcloud_handler import recognize_song
from utils.downloader import download_and_convert_song
from utils.cleardata import delete_files_in_downloads

# Load environment variables from .env file
load_dotenv()

# Validate required environment variables
required_env_vars = ["GROUP_ID", "CHANNEL_ID", "EXCEPTION_USER_ID", "BOT_TOKEN", "ACR_HOST", "ACR_ACCESS_KEY", "ACR_ACCESS_SECRET"]
for var in required_env_vars:
    if not os.getenv(var):
        raise EnvironmentError(f"Missing required environment variable: {var}")

# Group and Channel IDs
GROUP_ID = os.getenv("GROUP_ID")
CHANNEL_ID = os.getenv("CHANNEL_ID")
EXCEPTION_USER_ID = int(os.getenv("EXCEPTION_USER_ID"))
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Rate limit settings
USER_RATE_LIMIT = 60  # Allow 1 request per minute per user
last_request_time = {}

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Hi! I’m your music bot. Send me an Instagram reel link, and I'll process it for you!"
    )

async def check_membership(user_id: int, bot_token: str):
    application = ApplicationBuilder().token(bot_token).build()
    try:
        group_status = await application.bot.get_chat_member(chat_id=GROUP_ID, user_id=user_id)
        channel_status = await application.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return (
            group_status.status in ["member", "administrator", "creator"] and
            channel_status.status in ["member", "administrator", "creator"]
        )
    except Exception as e:
        print(f"[Error] Membership check failed: {e}")
        return False

def get_first_sentence(caption: str) -> str:
    return next((line.strip() for line in caption.splitlines() if line.strip()), "No caption available")

async def handle_message(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    chat_type = update.message.chat.type

    if chat_type in ["group", "supergroup", "channel"]:
        return

    current_time = time.time()
    if user_id in last_request_time and current_time - last_request_time[user_id] < USER_RATE_LIMIT:
        remaining_time = USER_RATE_LIMIT - (current_time - last_request_time[user_id])
        await update.message.reply_text(f"⏳ Please wait {remaining_time:.0f} seconds before making another request.")
        return

    last_request_time[user_id] = current_time

    try:
        is_member = await check_membership(user_id, BOT_TOKEN)
        if not is_member:
            buttons = [
                [InlineKeyboardButton("Join Group", url="https://t.me/+b4-OKLiKbMoyODY1")],
                [InlineKeyboardButton("Join Channel", url="https://t.me/ProjectON3")]
            ]
            await update.message.reply_text(
                "🚫 You must join our group and channel to use this bot. Please join using the buttons below and try again.",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            return

        url = update.message.text
        if "instagram.com" not in url:
            await update.message.reply_text("❌ Please send a valid Instagram reel or post link.")
            return

        caption, video_url = scrape_instagram_post(url)
        if not caption or not video_url:
            await update.message.reply_text("❌ Failed to fetch the Instagram post content. Please try again.")
            return

        caption = get_first_sentence(caption)
        downloading_message = await update.message.reply_text("⬇️ Downloading video...")
        video_path = download_video(video_url)

        if not video_path:
            raise Exception("Video download failed.")

        await downloading_message.edit_text("🎧 Video downloaded! Extracting audio...")
        audio_path = extract_audio(video_path)

        if not audio_path:
            raise Exception("Audio extraction failed.")

        await downloading_message.edit_text("🔍 Recognizing song...")
        song_info = recognize_song(audio_path, os.getenv("ACR_HOST"), os.getenv("ACR_ACCESS_KEY"), os.getenv("ACR_ACCESS_SECRET"))

        if not song_info or 'metadata' not in song_info:
            raise Exception("Song recognition failed.")

        song = song_info['metadata']['music'][0]
        title = song.get('title', 'Unknown Title')
        artists = ', '.join(artist['name'] for artist in song.get('artists', []))
        album = song.get('album', {}).get('name', 'Unknown Album')
        genres = ', '.join(genre['name'] for genre in song.get('genres', []))
        release_date = song.get('release_date', 'Unknown Release Date')

        youtube_link = song.get('external_metadata', {}).get('youtube', {}).get('vid', '')
        spotify_link = song.get('external_metadata', {}).get('spotify', {}).get('track', {}).get('id', '')

        keyboard = [
            [InlineKeyboardButton("YouTube", url=f"https://www.youtube.com/watch?v={youtube_link}" if youtube_link else f"https://www.youtube.com/results?search_query={title}")],
            [InlineKeyboardButton("Spotify", url=f"https://open.spotify.com/track/{spotify_link}" if spotify_link else f"https://open.spotify.com/search/{title}")]
        ]

        song_path = download_and_convert_song(title, artists)

        response_message = (
            f"🎶 **Song Found: {title}**\n\n"
            f"- Artists: {artists}\n"
            f"- Album: {album}\n"
            f"- Genres: {genres}\n"
            f"- Release Date: {release_date}\n"
        )

        with open(video_path, "rb") as video, open(song_path, "rb") as song_file:
            await update.message.reply_video(video=video, caption=caption)
            await downloading_message.delete()
            await update.message.reply_audio(audio=song_file, caption=response_message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    except Exception as e:
        print(f"[Error] {e}")
        await update.message.reply_text("❌ An error occurred. Please try again.")
    finally:
        delete_files_in_downloads()

def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
