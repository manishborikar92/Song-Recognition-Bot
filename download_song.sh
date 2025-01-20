#!/bin/bash
# Define video URL and cookies file path
VIDEO_URL=$1
COOKIES_FILE="cookies.txt"
VIDEO_URL="https://youtu.be/9h30Bx4Klxg?si=4xmcvK97iBYCyoOs"

# Check if cookies file exists
if [ ! -f "$COOKIES_FILE" ]; then
  echo "Cookies file not found! Please make sure the cookies file is in the current directory."
  exit 1
fi

# Run yt-dlp to simulate the download (this updates cookies but doesn't actually download the video)
yt-dlp --cookies "$COOKIES_FILE" --simulate "$VIDEO_URL"