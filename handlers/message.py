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
from handlers.check_membership import check_membership
from utils.acrcloud import recognize_song
from utils.audio_extractor import convert_video_to_mp3
from utils.cleardata import delete_all
from tempfile import TemporaryDirectory

# Handle user messages
async def handle_message(update: Update, context: CallbackContext):
    downloading_message = None

    user_id = update.message.from_user.id
    chat_type = update.message.chat.type

    # Ignore messages from groups, supergroups, and channels
    if chat_type in ["group", "supergroup", "channel"]:
        return

    # Check if user is in the exception list
    if int(user_id) in EXCEPTION_USER_IDS:
        logging.info('Developer')  # Log admin behavior
    else:
        # Rate-limiting for other users
        current_time = time.time()
        if user_id in last_request_time and current_time - last_request_time[user_id] < USER_RATE_LIMIT:
            remaining_time = USER_RATE_LIMIT - (current_time - last_request_time[user_id])
            await update.message.reply_text(
                f"\u23f3 <b>Hold up!</b> Please wait <b>{remaining_time:.0f} seconds</b> before making your next request. ⏳",
                parse_mode='HTML'
            )
            return

        # Update last request time
        last_request_time[user_id] = current_time

    bot_token = context.bot.token

    try:
        is_member = await check_membership(user_id, bot_token)
    except Exception as e:
        await update.message.reply_text(
            "<b>Oops!</b> 😔 I'm having trouble checking your membership. Try again later! ⏳",
            parse_mode='HTML',  # HTML formatting
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
            "🚫 <b>You gotta join our group and channel to use this bot!</b> Hit those buttons below to join. 🙏",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        return

    try:
        # Use TemporaryDirectory for temporary file storage
        with TemporaryDirectory() as temp_dir:

            # URL input
            if update.message.text:
                url = update.message.text
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

                    with open(video_path, "rb") as video:
                        await update.message.reply_video(video=video, caption=caption + "\n\n<a href='https://t.me/ProjectON3'>ProjectON3</a>", parse_mode='HTML')

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
                        if caption == "Video size exceeds 100MB. Skipping download.":
                            await downloading_message.edit_text(
                                "❌ <b>Whoa! Video exceeds 100MB!</b> Please upload a smaller one. 📁",
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
                        # Send the video if within the size limit
                        with open(video_path, "rb") as video:
                            await update.message.reply_video(video=video, caption=caption + "\n\n<a href='https://t.me/ProjectON3'>ProjectON3</a>", parse_mode='HTML')

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
                        "If you're looking to identify a song, you can also try the <b>/search</b> command! Just type it with the song title and artist to get started. 🎶🔍",
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
                video_path = os.path.join(temp_dir, f"{video.file_id}.mp4")
                await file.download_to_drive(custom_path=video_path)
                caption = None

            # Process uploaded audio
            elif update.message.audio or update.message.voice:
                downloading_message = await update.message.reply_text(
                    "🎶 <b>Processing your audio...</b> <i>Hang tight while I check the beats!</i> 🎧✨",
                    parse_mode='HTML',
                    reply_to_message_id=update.message.message_id
                )
                audio = update.message.audio or update.message.voice
                file = await context.bot.get_file(audio.file_id)
                audio_path = os.path.join(temp_dir, f"{audio.file_id}.mp3")
                await file.download_to_drive(custom_path=audio_path)

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

            # Recognize the song
            await downloading_message.edit_text(
                "🔍 <b>Recognizing song...</b> 🎶🎧",
                parse_mode='HTML'
            )
            song_info = await asyncio.to_thread(recognize_song, audio_path)

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

            if not song_path:
                await update.message.reply_text(
                    "🚫 <b>Song file not found.</b> I found the song but couldn't fetch the file 🥲",
                    parse_mode='HTML'
                )

            # Send response
            keyboard = [
                [InlineKeyboardButton("YouTube", url=youtube_link), InlineKeyboardButton("Spotify", url=spotify_link)],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            response_message = (
                f"🎶 <b>Song: {title}</b>\n\n"
                f"✨ <b>Artists:</b> {artists}\n"
                f"🎧 <b>Album:</b> {album}\n"
                f"🎶 <b>Genres:</b> {genres}\n"
                f"📅 <b>Release Date:</b> {release_date}\n\n"
                "<a href='https://t.me/ProjectON3'>ProjectON3</a>"
            )

            # Check file size
            file_size_mb = os.path.getsize(song_path) / (1024 * 1024)  # Convert bytes to MB
            if file_size_mb > 50:  # Exceeds Telegram's 50MB limit
                await downloading_message.delete()
                await update.message.reply_text(
                    text=(
                        "<b>🚫 Oops!</b> This file exceeds Telegram's <b>50MB limit</b>. 📉 Here’s the song info and play links! 🎵\n\n" + response_message
                    ),
                    reply_markup=reply_markup,
                    parse_mode='HTML',
                    reply_to_message_id=update.message.message_id
                )
            else:
                # Send audio if under the limit
                with open(song_path, "rb") as song_file:
                    await downloading_message.delete()
                    await update.message.reply_audio(
                        audio=song_file,
                        caption=response_message,
                        reply_markup=reply_markup,
                        parse_mode="HTML"
                    )

    except Exception as e:
        logging.error(f"Error processing message: {e}")
        if downloading_message:
            await downloading_message.edit_text("❌ <b>Something went wrong!</b> Please try again later. 😔",
                                                parse_mode='HTML')

    finally:
        delete_all()