import asyncio
import logging
from telegram.ext import ApplicationBuilder
from config import GROUP_ID, CHANNEL_ID


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
        logging.info(f"Error during membership check: {e}")
        return False  # Assume not a member if an error occurs