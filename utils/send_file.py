import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup

async def sendsong(update, downloading_message, response_message, youtube_link, spotify_link, song_path):
    try:
        keyboard = [
            [InlineKeyboardButton("YouTube", url=youtube_link), InlineKeyboardButton("Spotify", url=spotify_link)],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        file_size_mb = os.path.getsize(song_path) / (1024 * 1024)  # Convert bytes to MB
        logging.info(f"File size: {file_size_mb:.2f} MB")  # Debugging log

        if file_size_mb < 50:  # File size is within the limit
            try:
                with open(song_path, "rb") as song_file:
                    logging.info(f"Sending file: {song_path}")  # Debugging log
                    await update.message.reply_audio(
                        audio=song_file,
                        caption=response_message,
                        reply_markup=reply_markup,
                        parse_mode="HTML"
                    )
                logging.info("Song sent successfully.")  # Debugging log
            except Exception as e:
                logging.error(f"Error sending audio: {e}")
                await update.message.reply_text("⚠️ Oops! Something went wrong while sending the song.")
        else:
            try:
                logging.warning("File exceeds 50MB limit.")
                await update.message.reply_text(
                    text=(  # Error message when the file exceeds the limit
                        "<b>🚫 Uh-oh!</b> I can't send the song because it's too big (>50MB). 📉\n\n"
                        "But no worries, here’s all the details and the play buttons! 🎧🎶\n\n" + response_message
                    ),
                    reply_markup=reply_markup,
                    parse_mode='HTML',
                    reply_to_message_id=update.message.message_id
                )
            except Exception as e:
                logging.error(f"Error sending audio: {e}")
    except Exception as e:
        logging.error(f"Error: {e}")
    finally:
        await downloading_message.delete()
