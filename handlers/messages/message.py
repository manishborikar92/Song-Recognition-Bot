import os
import time
import asyncio
import logging
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from config import GROUP_URL, CHANNEL_URL, EXCEPTION_USER_IDS, USER_RATE_LIMIT, last_request_time
from downloader.instagram import download_instagram_reel
from downloader.song import download_song
from downloader.youtube import download_youtube_video
from decorator.membership import membership_check_decorator
from utils.acrcloud import recognize_song
from utils.send_file import sendsong
from utils.audio_processor import convert_video_to_mp3, trim_audio
from utils.cleardata import delete_cache, delete_files, delete_all
from database.db_manager import DBManager
from decorator.rate_limiter import RateLimiter

# Initialize the database manager
db = DBManager()

# Initialize the rate limiter (1 request per 60 seconds)
rate_limiter = RateLimiter(limit=1, interval=60, exception_user_ids=EXCEPTION_USER_IDS)

@membership_check_decorator()
@rate_limiter.rate_limit_decorator(user_id_arg_name="user_id")
async def handle_message(update: Update, context: CallbackContext):
    downloading_message = None
    user_id = update.message.from_user.id
    user_name = update.message.from_user.full_name
    chat_type = update.message.chat.type

    # # Ignore messages from groups, supergroups, and channels
    # if chat_type in ["group", "supergroup", "channel"]:
    #     return

    if not db.user_exists(user_id):
        db.add_user(user_id, user_name)

    try:
        # URL input
        if update.message.text:
            user_id = update.message.from_user.id
            url = update.message.text

            db.log_input(user_id, url)
            
            if re.match(r"^https?://(www\.)?instagram\.com/.*$", url):
                downloading_message = await update.message.reply_text(
                    "<b>⬇️ Fetching Instagram Reel...</b> <i>Hang tight! 🚀</i>",
                    parse_mode='HTML',  # HTML formatting
                    reply_to_message_id=update.message.message_id
                )
                video_path, caption = await asyncio.to_thread(download_instagram_reel, url)

                if not video_path or not caption:
                    await downloading_message.edit_text(
                    "❌ <b>Oops!</b> Invalid Instagram URL. Try again! 🌐🔗",
                    parse_mode='HTML'
                    )
                    raise Exception("Failed to fetch Instagram video.")
                try:
                    with open(video_path, "rb") as video:
                        await update.message.reply_video(video=video, caption=caption + "\n\n<a href='https://t.me/ProjectON3'>ProjectON3</a>", parse_mode='HTML')
                    logging.info("Instagram reel sent successfully.") 
                except Exception as e:
                    logging.error(f"Error sending video: {e}")
                    await update.message.reply_text("⚠️ Oops! Something went wrong while sending the video.")

            elif re.match(r"^https?://(www\.)?(youtube\.com|youtu\.be)/.*$", url):
                if "/shorts" in url:
                    downloading_message = await update.message.reply_text(
                        "<b>⬇️ Downloading YouTube Short...</b> <i>Hang tight! 🚀</i>",
                        parse_mode='HTML',
                        reply_to_message_id=update.message.message_id
                    )
                else:
                    downloading_message = await update.message.reply_text(
                        "<b>⬇️ Downloading YouTube Video...</b> <i>Hang tight! 🚀</i>",
                        parse_mode='HTML',
                        reply_to_message_id=update.message.message_id
                    )
                    
                video_path, caption = await asyncio.to_thread(download_youtube_video, url)

                if not video_path:
                    if caption == "size exceeds":
                        await downloading_message.edit_text(
                            "❌ <b>Whoa! Video exceeds 100MB!</b> 📁",
                            parse_mode='HTML'
                        )
                    else:
                        await downloading_message.edit_text(
                            "❌ <b>Invalid URL!</b> Provide a valid <b>YouTube</b> link. 🌐🔗",
                            parse_mode='HTML'
                        )
                    raise Exception("Failed to fetch YouTube video.")

                # Check file size
                file_size_mb = os.path.getsize(video_path) / (1024 * 1024)  # Convert bytes to MB
                if file_size_mb > 50:
                    await update.message.reply_text(
                        "<b>🚫 Oops!</b> Telegram's <b>50MB limit</b> blocks this video. 📉 Don't worry though, I’ve got your back with <b>other formats</b>! 🎵",
                        parse_mode='HTML',
                        reply_to_message_id=update.message.message_id
                    )
                else:
                    try:
                        with open(video_path, "rb") as video:
                            await update.message.reply_video(video=video, caption=caption + "\n\n<a href='https://t.me/ProjectON3'>ProjectON3</a>", parse_mode='HTML')
                        logging.info("YouTube video sent successfully.") 
                    except Exception as e:
                        logging.error(f"Error sending video: {e}")
                        await update.message.reply_text("⚠️ Oops! Something went wrong while sending the video.")

            elif re.match(r"^https?://(www\.)?([\w.-]+)(/.*)?$", url):
                await update.message.reply_text(
                    "❌ <b>Invalid URL!</b> Please send a valid <b>Instagram</b> or <b>YouTube</b> link. 🌐🔗",
                    parse_mode='HTML',
                    reply_to_message_id=update.message.message_id
                )
                return
            
            else:
                await update.message.reply_text(
                    "🚫 <b>Hey!</b> Don’t send me text messages! Drop a <b>link</b>, <b>video</b>, or <b>audio</b> 🎶📹🎤, and I'll handle the rest!\n\n"
                    "If you're looking to identify a song, you can also try the <b>/search</b> command! Just type it with the song - title and artist to get started. 🎶🔍",
                    parse_mode='HTML',
                    reply_to_message_id=update.message.message_id
                )
                return

        # Process uploaded video
        elif update.message.video:
            downloading_message = await update.message.reply_text(
                "🎬 <b>Processing your uploaded video...</b> <i>Almost there!</i> ✨",
                parse_mode='HTML',
                reply_to_message_id=update.message.message_id
            )
            video = update.message.video
            file = await context.bot.get_file(video.file_id)
            save_dir = 'data/videos'
            os.makedirs(save_dir, exist_ok=True)
            video_path = os.path.join(save_dir, f"{video.file_id}.mp4")
            
            # Skip download if the video already exists
            if os.path.exists(video_path):
                logging.info(f"Video already exists at: {video_path}")
            else:
                try:
                    await file.download_to_drive(custom_path=video_path)
                    logging.info(f"Video downloaded to: {video_path}")
                except Exception as e:
                    logging.error(f"Failed to download video: {e}")
                    await downloading_message.edit_text("❌ Failed to process the video. Please try again.")
                    return

        # Process uploaded audio
        elif update.message.audio or update.message.voice:
            downloading_message = await update.message.reply_text(
                "🎶 <b>Processing your audio...</b> <i>Hang tight while I check the beats!</i> 🎧✨",
                parse_mode='HTML',
                reply_to_message_id=update.message.message_id
            )
            audio = update.message.audio or update.message.voice
            file = await context.bot.get_file(audio.file_id)
            save_dir = 'data/audios'
            os.makedirs(save_dir, exist_ok=True)
            received_audio_path = os.path.join(save_dir, f"{audio.file_id}.mp3")
            
            # Skip download if the audio already exists
            if os.path.exists(received_audio_path):
                logging.info(f"Audio already exists at: {received_audio_path}")
            else:
                try:
                    await file.download_to_drive(custom_path=received_audio_path)
                    logging.info(f"Audio downloaded to: {received_audio_path}")
                    audio_path = await asyncio.to_thread(trim_audio, received_audio_path)
                except Exception as e:
                    logging.error(f"Failed to download audio: {e}")
                    await downloading_message.edit_text("❌ Failed to process the audio. Please try again.")
                    return

        else:
            await update.message.reply_text(
                "❌ <b>Unsupported input type</b>. Send a <b>link</b>, <b>video</b>, or <b>audio</b> 🎶📹🔗 so I can help you out! 💡",
                parse_mode='HTML',
                reply_to_message_id=update.message.message_id
            )
            return

        # Extract audio if video was uploaded
        if "video_path" in locals():
            await downloading_message.edit_text(
                "🎧 <b>Video downloaded!</b> Now <i>extracting audio...</i> 🎶🔊",
                parse_mode='HTML'
            )
            audio_path = await asyncio.to_thread(convert_video_to_mp3, video_path)

        if "audio_path" in locals():
            # Recognize the song
            await downloading_message.edit_text(
                "🔍 <b>Recognizing song...</b> 🎶🎧",
                parse_mode='HTML'
            )
            song_info = await asyncio.to_thread(recognize_song, audio_path)
        else:
            await downloading_message.edit_text(
                "❌ <b>Can't process audio! Either corrupted or long.</b> Try again later. 🎶😞",
                parse_mode='HTML'
            )

        if not song_info or "metadata" not in song_info or not song_info["metadata"].get("music"):
            await downloading_message.edit_text(
                "❌ <b>Failed to recognize the song.</b> Try again later. 🎶😞",
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

        # Download the song
        await downloading_message.edit_text(
            "⬇️ <b>Downloading the song...</b> 🎶🚀",
            parse_mode='HTML'
        )
        song_path = await asyncio.to_thread(download_song, title, artists)

        if song_path:
            await sendsong(update, downloading_message, title, artists, album, release_date, youtube_link, spotify_link, song_path)
        else:
            await update.message.reply_text(
                "🚫 <b>Song file not found.</b> I found the song but couldn't fetch the file 🥲",
                parse_mode='HTML'
            )
        
    except Exception as e:
        logging.error(f"Error processing message: {e}")

    finally:
        # Define paths with a fallback to None if not defined
        paths = ["song_path", "audio_path", "video_path"]
        paths_to_delete = []

        for path_name in paths:
            try:
                path_value = eval(path_name) if eval(path_name) else None
            except NameError:
                path_value = None
            if path_value:
                paths_to_delete.append(path_value)

        # If there are any valid paths, delete the files
        if paths_to_delete:
            delete_files(*paths_to_delete)  # Unpack the list of paths into the function

        # Always delete the cache
        delete_cache()
