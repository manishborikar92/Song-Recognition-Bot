import os
import logging
from yt_dlp import YoutubeDL

def get_first_sentence(caption: str) -> str:
    """Get the first non-empty line from the caption."""
    return next((line.strip() for line in caption.splitlines() if line.strip()), "No description available")

def download_youtube_video(url, max_filesize_mb=100):
    """
    Downloads a YouTube video at 360p, extracts its description, and retrieves the first sentence.
    
    Args:
        url (str): The YouTube video URL.
        max_filesize_mb (int): Maximum allowed filesize in MB.

    Returns:
        tuple: (str, str) Video file path and the first sentence of the description, or error message.
    """
    try:
        # Directory for downloaded videos
        save_dir = "data/videos"
        os.makedirs(save_dir, exist_ok=True)

        # yt-dlp options
        ydl_opts = {
            'format': 'bestvideo[height<=360]+bestaudio/best[height<=360]',
            'outtmpl': f"{save_dir}/%(id)s.%(ext)s",
            'noplaylist': True,
            'merge_output_format': 'mp4',
            'postprocessors': [
                {'key': 'EmbedThumbnail'},
                {'key': 'FFmpegMetadata'}
            ],
            'writethumbnail': True,
            'cookiefile': 'cookies.txt',
        }

        with YoutubeDL(ydl_opts) as ydl:
            # Extract video information without downloading
            info_dict = ydl.extract_info(url, download=False)

            # Retrieve video ID and construct file path
            video_id = info_dict.get('id')
            if not video_id:
                logging.error("Failed to retrieve video ID.")
                return None, "Failed to retrieve video ID."

            video_path = os.path.join(save_dir, f"{video_id}.mp4")
            if os.path.exists(video_path):
                logging.info(f"Video already exists at: {video_path}")
                return video_path, "Video already exists."

            # Check video size
            filesize_bytes = info_dict.get('filesize') or info_dict.get('filesize_approx', 0)
            if filesize_bytes > max_filesize_mb * 1024 * 1024:
                logging.warning(f"Video size exceeds {max_filesize_mb}MB. Skipping download.")
                return None, "size exceeds"

            # Download the video
            logging.info("Downloading video...")
            info_dict = ydl.extract_info(url, download=True)

            # Ensure the file has the correct extension
            video_path = ydl.prepare_filename(info_dict).rsplit('.', 1)[0] + '.mp4'

            # Get the description and extract the first sentence
            caption = info_dict.get('description', '')
            first_sentence = get_first_sentence(caption)

        logging.info("YouTube video downloaded successfully.")
        return video_path, first_sentence

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return None, str(e)

# # Example usage
# test_url = "https://youtu.be/Q-FzRg6V-b4"
# video_path, description = download_youtube_video(test_url)
# logging.info(f"Downloaded video path: {video_path}\nDescription: {description}")
