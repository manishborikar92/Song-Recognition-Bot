import os
import logging
from yt_dlp import YoutubeDL

def get_first_sentence(caption: str) -> str:
    """Get the first non-empty line from the caption."""
    return next((line.strip() for line in caption.splitlines() if line.strip()), "No description available")

def download_youtube_video(url, max_filesize_mb=100):
    """
    Downloads YouTube video at 360p with optimized performance and metadata handling.
    
    Args:
        url (str): YouTube video URL
        max_filesize_mb (int): Maximum allowed filesize in MB

    Returns:
        tuple: (str, str) Video path and first sentence of description or error
    """
    try:
        save_dir = "data/videos"
        os.makedirs(save_dir, exist_ok=True)

        ydl_opts = {
            'format': 'bestvideo[height<=360][ext=mp4]+bestaudio/best[height<=360][ext=mp4]',
            'outtmpl': f"{save_dir}/%(id)s.%(ext)s",
            'noplaylist': True,
            'merge_output_format': 'mp4',
            'postprocessors': [
                {'key': 'EmbedThumbnail'},
                {'key': 'FFmpegMetadata'}
            ],
            'writethumbnail': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'concurrent_fragment_downloads': 5,
            'socket_timeout': 10,
            'nocheckcertificate': True,
            'noprogress': True,
            'retries': 3,
        }

        with YoutubeDL(ydl_opts) as ydl:
            # Single info extraction with metadata
            info_dict = ydl.extract_info(url, download=False)
            video_id = info_dict['id']
            video_path = os.path.join(save_dir, f"{video_id}.mp4")

            if os.path.exists(video_path):
                logging.info(f"Video exists: {video_path}")
                return video_path, "Video exists"

            # Get description early
            caption = info_dict.get('description', '')
            first_sentence = get_first_sentence(caption)

            # Size check before download
            filesize = info_dict.get('filesize') or info_dict.get('filesize_approx', 0)
            if filesize > max_filesize_mb * 1024 * 1024:
                logging.warning(f"Video exceeds {max_filesize_mb}MB")
                return None, "size exceeds"

            # Download using cached info_dict
            ydl.process_ie_result(info_dict, download=True)

        logging.info("Download successful")
        return video_path, first_sentence

    except Exception as e:
        logging.error(f"Download failed: {e}")
        return None, str(e)