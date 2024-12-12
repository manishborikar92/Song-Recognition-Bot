import os
import shutil
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
GROUP_ID = os.getenv("GROUP_ID")  # Replace with your group ID
CHANNEL_ID = os.getenv("CHANNEL_ID")  # Replace with your channel ID

delete_files_in_downloads()

async def start(update: Update, context):
    await update.message.reply_text(
        "Hi! I’m your music bot. Send me an Instagram reel or post link, and I'll process it for you!"
    )

async def check_membership(user_id: int, bot_token: str):
    application = ApplicationBuilder().token(bot_token).build()
    # Check group membership
    group_status = await application.bot.get_chat_member(chat_id=GROUP_ID, user_id=user_id)
    channel_status = await application.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)

    is_member_of_group = group_status.status in ["member", "administrator", "creator"]
    is_member_of_channel = channel_status.status in ["member", "administrator", "creator"]

    return is_member_of_group and is_member_of_channel

async def handle_message(update: Update, context):
    user_id = update.message.from_user.id
    bot_token = context.bot.token

    # Check if the user has joined the group and channel
    is_member = await check_membership(user_id, bot_token)

    if not is_member:
        # Send a message with inline buttons for joining group and channel
        buttons = [
            [InlineKeyboardButton("Join Group", url=f"https://t.me/TheOdinProjectGroup")],
            [InlineKeyboardButton("Join Channel", url=f"https://t.me/The0dinProject")]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await update.message.reply_text(
            "You must join our group and channel to use this bot. Please join using the buttons below and try again.",
            reply_markup=reply_markup
        )
        return

    # Proceed with the original process if the user has joined
    url = update.message.text
    if "instagram.com" not in url:
        await update.message.reply_text("Please send a valid Instagram reel or post link.")
        return

    caption, video_url = scrape_instagram_post(url)

    if caption and video_url:
        downloading_message = await update.message.reply_text("Downloading video...")

        video_path = download_video(video_url)
        if video_path:
            await downloading_message.edit_text("Video downloaded! Extracting audio...")

            audio_path = extract_audio(video_path)
            if audio_path:
                await downloading_message.edit_text("Audio extracted successfully! Recognizing song...")

                # Song recognition
                acr_host = os.getenv("ACR_HOST")
                acr_access_key = os.getenv("ACR_ACCESS_KEY")
                acr_access_secret = os.getenv("ACR_ACCESS_SECRET")
                song_info = recognize_song(audio_path, acr_host, acr_access_key, acr_access_secret)

                if song_info and 'metadata' in song_info:
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
                        [
                            InlineKeyboardButton("YouTube", url=youtube_link),
                            InlineKeyboardButton("Spotify", url=spotify_link)
                        ]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)

                    response_message = (
                        f"🎶 **Song Found: {title}**\n\n"
                        f"- Artists: {artists}\n"
                        f"- Album: {album}\n"
                        f"- Genres: {genres}\n"
                        f"- Release Date: {release_date}\n"
                    )

                    await update.message.reply_video(video=open(video_path, "rb"), caption=caption)
                    await downloading_message.delete()
                    await update.message.reply_audio(audio=open(song_path, "rb"), caption=response_message, reply_markup=reply_markup, parse_mode="Markdown")

                    delete_files_in_downloads()
                else:
                    await update.message.reply_text("Sorry, I couldn't recognize the song.")
            else:
                await update.message.reply_text("Failed to extract audio.")
        else:
            await update.message.reply_text("Failed to download the video.")
    else:
        await update.message.reply_text("Failed to fetch the Instagram post. Please try again.")

def main():
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()