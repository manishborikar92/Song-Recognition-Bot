import os
import shutil
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext
from utils.instagram import scrape_instagram_post
from utils.audio_processing import download_video, extract_audio
from utils.acrcloud_handler import recognize_song
from utils.downloader import download_and_convert_song

# Function to delete all files in the 'data/downloads' folder
def delete_files_in_downloads():
    downloads_folder = 'data/downloads'
    for filename in os.listdir(downloads_folder):
        file_path = os.path.join(downloads_folder, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)  # Delete the file
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)  # Delete the directory
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")


async def start(update: Update, context):
    await update.message.reply_text(
        "Hi! I’m your music bot. Send me an Instagram reel or post link, and I'll process it for you!"
    )

async def handle_message(update: Update, context):
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
                acr_host = "https://identify-ap-southeast-1.acrcloud.com"
                acr_access_key = "5ecba6932829064922d9959931839b14"
                acr_access_secret = "A8mVX6LNivrhuDwu9n0iER2xq7sZ5RZFIFlg1lO5"
                # Send the song's MP3 file (extracted audio) with song details
                song_info = recognize_song(audio_path, acr_host, acr_access_key, acr_access_secret)

                # Send the song details back to the user
                if song_info and 'metadata' in song_info:
                    song = song_info['metadata']['music'][0]  # Get the first song from the list
                    title = song.get('title', 'Unknown Title')
                    artists = ', '.join(artist['name'] for artist in song.get('artists', []))
                    album = song.get('album', {}).get('name', 'Unknown Album')
                    genres = ', '.join(genre['name'] for genre in song.get('genres', []))
                    release_date = song.get('release_date', 'Unknown Release Date')

                    # youtube_link and spotify_link
                    youtube_track_id = song.get('external_metadata', {}).get('youtube', {}).get('vid', '')
                    youtube_link = f"https://www.youtube.com/watch?v={youtube_track_id}" if youtube_track_id else f"https://www.youtube.com/results?search_query={title}"

                    spotify_track_id = song.get('external_metadata', {}).get('spotify', {}).get('track', {}).get('id', '')
                    spotify_link = f"https://open.spotify.com/track/{spotify_track_id}" if spotify_track_id else f"https://open.spotify.com/search/{title}"

                    # Call the download_song function to get the song file path
                    song_path = download_and_convert_song(title, artists)


                    # Create the inline keyboard for YouTube and Spotify links
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

                    # Reply with video, audio, and song info
                    await update.message.reply_video(video=open(video_path, "rb"), caption=caption)
                    await downloading_message.delete()
                    await update.message.reply_audio(audio=open(song_path, "rb"), caption=response_message, reply_markup=reply_markup, parse_mode="Markdown")

                    # Delete all files in the 'data/downloads' folder after sending the files
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
    BOT_TOKEN = "8122146498:AAGyAp7DHZDR4LPKt4XtHcvK4_xLJn97ZGI"
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
