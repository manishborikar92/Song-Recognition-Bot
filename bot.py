from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from utils.instagram import scrape_instagram_post
from utils.audio_processing import download_video, extract_audio

async def start(update: Update, context):
    await update.message.reply_text(
        "Hi! I’m your music bot. Send me an Instagram reel or post link, and I'll process it for you!"
    )

async def handle_message(update: Update, context):
    url = update.message.text

    # Check if it's an Instagram link
    if "instagram.com" not in url:
        await update.message.reply_text("Please send a valid Instagram reel or post link.")
        return

    # Scrape Instagram post
    caption, video_url = scrape_instagram_post(url)

    if caption and video_url:
        await update.message.reply_text("Downloading video...")

        # Step 1: Download the video
        video_path = download_video(video_url)

        if video_path:
            await update.message.reply_text("Video downloaded! Extracting audio...")

            # Step 2: Extract audio
            audio_path = extract_audio(video_path)

            if audio_path:
                await update.message.reply_text("Audio extracted successfully!")
                # Reply with the video file
                await update.message.reply_video(video=open(video_path, "rb"), caption=caption)

                # Reply with the audio file
                await update.message.reply_audio(audio=open(audio_path, "rb"))
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
