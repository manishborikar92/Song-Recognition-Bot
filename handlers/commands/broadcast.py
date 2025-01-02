import asyncio
import logging
from telegram import Update
from telegram.error import TelegramError
from telegram.ext import CallbackContext
from config import EXCEPTION_USER_IDS, DEVELOPERS
from database.db_manager import DBManager

# Initialize the database manager
db = DBManager()

async def send_media_to_user(context, user_id, message_type, media, caption=None):
    """Helper function to send media with caption."""
    try:
        if message_type == 'text':
            await context.bot.send_message(chat_id=user_id, text=media)
        elif message_type == 'video':
            await context.bot.send_video(chat_id=user_id, video=media, caption=caption)
        elif message_type == 'document':
            await context.bot.send_document(chat_id=user_id, document=media, caption=caption)
        elif message_type == 'photo':
            await context.bot.send_photo(chat_id=user_id, photo=media, caption=caption)
        elif message_type == 'audio':
            await context.bot.send_audio(chat_id=user_id, audio=media, caption=caption)
        return True  # Success
    except TelegramError as e:
        # Catch Telegram-specific errors like user restrictions, file size issues, etc.
        logging.error(f"Telegram error while sending message to {user_id}: {e}")
        await context.bot.send_message(chat_id=user_id, text=f"❌ Telegram error: {e}")
        return False  # Failure
    except Exception as e:
        # Catch any general errors
        logging.error(f"Error while sending message to {user_id}: {e}")
        await context.bot.send_message(chat_id=user_id, text=f"❌ Error: {e}")
        return False  # Failure

async def broadcast_command(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if int(user_id) in EXCEPTION_USER_IDS:
        if not update.message.reply_to_message and not context.args and not update.message.text:
            await update.message.reply_text("❌ Please provide a message or reply to a message to broadcast.")
            return
        
        # Process the content type (direct message or reply)
        if update.message.reply_to_message:
            reply_message = update.message.reply_to_message
            # Determine the message type based on available attributes
            if reply_message.text:
                message_type = 'text'
            elif reply_message.video:
                message_type = 'video'
            elif reply_message.document:
                message_type = 'document'
            elif reply_message.photo:
                message_type = 'photo'
            elif reply_message.audio:
                message_type = 'audio'
            else:
                message_type = 'unknown'  # Default to unknown if no valid type found
        else:
            message_type = 'text'
            message = ' '.join(context.args)

        users = db.get_all_users()

        # Prepare a list of tasks to be run concurrently (send messages to users)
        tasks = []

        # Prepare media and caption to send
        media = None
        caption = None
        if message_type == 'text':
            media = message if not update.message.reply_to_message else reply_message.text
        elif message_type == 'video':
            media = reply_message.video.file_id if reply_message.video else None
            caption = reply_message.caption if reply_message.caption else None
        elif message_type == 'document':
            media = reply_message.document.file_id if reply_message.document else None
            caption = reply_message.caption if reply_message.caption else None
        elif message_type == 'photo':
            media = reply_message.photo[-1].file_id if reply_message.photo else None
            caption = reply_message.caption if reply_message.caption else None
        elif message_type == 'audio':
            media = reply_message.audio.file_id if reply_message.audio else None
            caption = reply_message.caption if reply_message.caption else None

        # If the message type is unknown, handle accordingly
        if message_type == 'unknown':
            await update.message.reply_text("❌ Unsupported message type. Cannot broadcast.")
            return

        # Add tasks to the list for each user
        for user in users:
            tasks.append(send_media_to_user(context, user[0], message_type, media, caption))

        # Use asyncio to run tasks concurrently (improving efficiency for large user bases)
        try:
            # Wait for all tasks to complete
            sent_results = await asyncio.gather(*tasks)

            # Check if all messages were successfully sent
            if all(sent_results):
                await update.message.reply_text("✅ Message broadcasted to all users.")
            else:
                await update.message.reply_text("❌ Some users failed to receive the broadcast.")
        
        except Exception as e:
            logging.error(f"Error during broadcast operation: {e}")
            await update.message.reply_text("❌ An error occurred while broadcasting the message.")
        
    else:
        await update.message.reply_text("❌ You do not have permission to use this command.")
