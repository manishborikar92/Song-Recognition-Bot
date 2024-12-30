import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Rate limit settings
USER_RATE_LIMIT = 60  # Allow 1 request per minute per user
last_request_time = {}

#BOT TOKEN
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ACRCLOUD
ACR_HOST = os.getenv("ACR_HOST")
ACR_ACCESS_KEY = os.getenv("ACR_ACCESS_KEY")
ACR_ACCESS_SECRET = os.getenv("ACR_ACCESS_SECRET")
ACR_BEARER_TOKEN = os.getenv("ACR_BEARER_TOKEN")
ACR_ENDPOINT_URL = os.getenv("ACR_ENDPOINT_URL")

# Group and Channel IDs
GROUP_ID = os.getenv("GROUP_ID")
CHANNEL_ID = os.getenv("CHANNEL_ID")
EXCEPTION_USER_IDS = set(map(int, os.getenv("EXCEPTION_USER_IDS", "").split(",")))
GROUP_URL = "https://t.me/+b4-OKLiKbMoyODY1"
CHANNEL_URL = "https://t.me/ProjectON3"

# Set the webhook URL (replace with your own public URL when deployed)
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Set this in your environment variables