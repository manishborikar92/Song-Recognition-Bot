import os
import shutil
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

# Group and Channel IDs
GROUP_ID = os.getenv("GROUP_ID")
CHANNEL_ID = os.getenv("CHANNEL_ID")

# Rate limit settings
USER_RATE_LIMIT = 60  # Allow 1 request per minute per user
last_request_time = {}

async def start(update: Update, context):
    await update.message.reply_text(
        "Hi! I’m your music bot. Send me an Instagram reel link, and I'll process it for you!"
    )

async def check_membership(user_id: int, bot_token: str):
    application = ApplicationBuilder().token(bot_token).build()
    try:
        # Check group and channel membership
        group_status = await application.bot.get_chat_member(chat_id=GROUP_ID, user_id=user_id)
        channel_status = await application.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)

        is_member_of_group = group_status.status in ["member", "administrator", "creator"]
        is_member_of_channel = channel_status.status in ["member", "administrator", "creator"]
        
        return is_member_of_group and is_member_of_channel
    except Exception as e:
        print(f"Error during membership check: {e}")
        return False  # Assume not a member if an error occurs

GROUP_URL = "https://t.me/+b4-OKLiKbMoyODY1"
CHANNEL_URL = "https://t.me/ProjectON3"

def get_first_sentence(caption: str) -> str:
    # Split the caption by line breaks and get the first non-empty line
    lines = caption.split('\n')
    first_line = next((line for line in lines if line.strip()), "")  # Find the first non-empty line
    return first_line

async def handle_message(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    chat_type = update.message.chat.type

    # Ignore messages from groups, supergroups, and channels
    if chat_type in ["group", "supergroup", "channel"]:
        return

    # Handle rate-limiting per user
    current_time = time.time()
    if user_id in last_request_time and current_time - last_request_time[user_id] < USER_RATE_LIMIT:
        remaining_time = USER_RATE_LIMIT - (current_time - last_request_time[user_id])
        await update.message.reply_text(f"⏳ Please wait {remaining_time:.0f} seconds before making another request.")
        return
    
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

    url = update.message.text
    if "instagram.com" not in url:
        await update.message.reply_text("❌ Please send a valid Instagram reel or post link.")
        return

    try:
        caption, video_url = scrape_instagram_post(url)
    except Exception as e:
        print(f"Error scraping Instagram post: {e}")
        await update.message.reply_text("❌ Failed to fetch the Instagram post. Please try again later.")
        return

    if not caption or not video_url:
        await update.message.reply_text("❌ Failed to fetch the Instagram post content. Please try again.")
        return

    # Get only the first sentence of the caption
    caption = get_first_sentence(caption)

    downloading_message = await update.message.reply_text("⬇️ Downloading video...")
    try:
        video_path = download_video(video_url)
        if not video_path:
            raise Exception("Failed to download video.")
        
        await downloading_message.edit_text("🎧 Video downloaded! Extracting audio...")
        audio_path = extract_audio(video_path)
        if not audio_path:
            raise Exception("Failed to extract audio.")

        await downloading_message.edit_text("🔍 Recognizing song...")
        acr_host = os.getenv("ACR_HOST")
        acr_access_key = os.getenv("ACR_ACCESS_KEY")
        acr_access_secret = os.getenv("ACR_ACCESS_SECRET")
        
        song_info = recognize_song(audio_path, acr_host, acr_access_key, acr_access_secret)

        if not song_info or 'metadata' not in song_info:
            raise Exception("Failed to recognize the song.")

        song = song_info['metadata']['music'][0]
        title = song.get('title', 'Unknown Title')
        artists = ', '.join(artist['name'] for artist in song.get('artists', []))
        album = song.get('album', {}).get('name', 'Unknown Album')
        genres = ', '.join(genre['name'] for genre in song.get('genres', []))
        release_date = song.get('release_date', 'Unknown Release Date')

        youtube_track_id = song.get('external_metadata', {}).get('youtube', {}).get('vid', '')
        youtube_link = f"https://www.youtube.com/watch?v={youtube_track_id}" if youtube_track_id else f"https://www.youtube.com/results?search_query={title}"

        spotify_track_id = song.get('external_metadata', {}).get('spotify', {}).get('track', {}).get('id', '')
        spotify_link = f"https://open.spotify.com/track/{spotify_track_id}" if spotify_track_id else f"https://open.spotify.com/search/{title}"

        song_path = download_and_convert_song(title, artists)

        keyboard = [
            [InlineKeyboardButton("YouTube", url=youtube_link),
             InlineKeyboardButton("Spotify", url=spotify_link)],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        response_message = (
            f"🎶 **Song Found: {title}**\n\n"
            f"- Artists: {artists}\n"
            f"- Album: {album}\n"
            f"- Genres: {genres}\n"
            f"- Release Date: {release_date}\n"
        )

        with open(video_path, "rb") as video, open(song_path, "rb") as song_file:
            await update.message.reply_video(video=video, caption=caption)  # Only the first sentence of caption
            await downloading_message.delete()
            await update.message.reply_audio(audio=song_file, caption=response_message, reply_markup=reply_markup, parse_mode="Markdown")

    except Exception as e:
        print(f"Error during process: {e}")
        await update.message.reply_text(f"❌ Error: {e}")

    finally:
        delete_files_in_downloads()

def main():
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
