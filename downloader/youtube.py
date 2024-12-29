import os
import yt_dlp
import re
import asyncio

def get_first_sentence(caption: str) -> str:
    """Get the first non-empty line from the caption."""
    lines = caption.split('\n')
    first_line = next((line for line in lines if line.strip()), "")
    return first_line

def download_youtube_video(url):
    try:
        # Set up yt-dlp options
        ydl_opts = {
            'format': 'bestvideo[height<=360]+bestaudio/best[height<=360]',  # Download video at 360p quality
            'outtmpl': 'temp/videos/%(id)s.%(ext)s',  # Save with the video id as filename
            'noplaylist': True,  # Avoid downloading entire playlists
            'merge_output_format': 'mp4',  # Merge audio and video into mp4 if needed
            'postprocessors': [
                {
                    'key': 'EmbedThumbnail',  # Embed thumbnail into video
                },
                {
                    'key': 'FFmpegMetadata',  # Add metadata to video
                }
            ],
            'writethumbnail': True,  # Download thumbnail
            'cookiefile': 'youtube_cookies.txt',  # Use cookies if needed
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)  # Extract info first without downloading

            # Check video size before downloading
            filesize = info_dict.get('filesize', None) or info_dict.get('filesize_approx', 0)
            if filesize and filesize > 100 * 1024 * 1024:  # Check if size is above 100MB
                return None, "Video size exceeds 100MB. Skipping download."

            # Proceed to download
            info_dict = ydl.extract_info(url, download=True)

            # Get the video path after download
            video_path = ydl.prepare_filename(info_dict)

            # Replace the file extension with .mp4
            video_path = video_path.rsplit('.', 1)[0] + '.mp4'

            # Get the video description (caption)
            caption = info_dict.get('description', 'No description')

            # Get the first non-empty line of the description
            first_sentence = get_first_sentence(caption)

        print('YouTube Video Downloaded')
        return video_path, first_sentence

    except Exception as e:
        return None, str(e)

# Example usage
# url = "https://youtu.be/PXGycbkbtW0?si=NqaNyI0kWmWFan7N"
# video_path, description = download_youtube_video(url)
# print(f"Downloaded video path: {video_path}\nDescription: {description}")
