import logging
from functools import wraps
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CallbackContext
from config import GROUP_ID, CHANNEL_ID, GROUP_URL, CHANNEL_URL, BOT_TOKEN  # Import BOT_TOKEN from config

# Membership Check Function
async def check_membership(user_id: int, bot_token: str):
    application = ApplicationBuilder().token(bot_token).build()
    try:
        group_status = await application.bot.get_chat_member(chat_id=GROUP_ID, user_id=user_id)
        channel_status = await application.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)

        return group_status.status in ["member", "administrator", "creator"] and \
               channel_status.status in ["member", "administrator", "creator"]

    except Exception as e:
        logging.error(f"Error during membership check: {e}")
        return False

# Membership Check Decorator
def membership_check_decorator():
    def decorator(func):
        @wraps(func)
        async def wrapper(update: Update, context: CallbackContext, *args, **kwargs):
            user_id = update.message.from_user.id
            chat_type = update.message.chat.type
            # Ignore messages from groups, supergroups, and channels
            if chat_type in ["group", "supergroup", "channel"]:
                return
                

            try:
                is_member = await check_membership(user_id, BOT_TOKEN)  # Use BOT_TOKEN from config

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

            except Exception as e:
                logging.error(f"Error during membership check: {e}")
                await update.message.reply_text(
                    "<b>Oops!</b> 😔 I'm having trouble checking your membership. Try again later! ⏳",
                    parse_mode='HTML',
                    reply_to_message_id=update.message.message_id
                )
                return

            return await func(update, context, *args, **kwargs)

        return wrapper
    return decorator
