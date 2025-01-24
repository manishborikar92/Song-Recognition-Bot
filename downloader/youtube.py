import os
import logging
from yt_dlp import YoutubeDL

def get_first_sentence(caption: str) -> str:
    """Get the first non-empty line from the caption."""
    return next((line.strip() for line in caption.splitlines() if line.strip()), "No description available")

def download_youtube_video(url, max_filesize_mb=100):
    """
    Downloads YouTube video with robust format handling and PO token workaround.
    
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
            'format': 'bestvideo[height<=360]+bestaudio/best',
            'outtmpl': f"{save_dir}/%(id)s.%(ext)s",
            'http_headers': {
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://www.youtube.com/',
            },
            'compat_opts': ['youtube-unavailable-videos'],
            'throttled_rate': '1M',
            'force_ip': '4',
            'concurrent_fragment_downloads': 8,
            'retries': 15,
            'fragment_retries': 25,
            'skip_unavailable_fragments': True,
            'nocheckcertificate': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            'extractor_args': {
                'youtube': {
                    'player_client': 'web',
                    'skip': ['hls', 'dash'],
                }
            },
            'postprocessors': [
                {
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                    'when': 'post_process'
                },
                {
                    'key': 'FFmpegVideoRemuxer',
                    'preferedformat': 'mp4',
                },
                {'key': 'EmbedThumbnail'},
                {'key': 'FFmpegMetadata'}
            ],
            'format_sort': ['res:360', 'ext:mp4', 'vcodec:h264'],
            'check_formats': 'selected',
        }

        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            video_id = info_dict['id']
            video_path = os.path.join(save_dir, f"{video_id}.mp4")

            if os.path.exists(video_path):
                logging.info(f"Video exists: {video_path}")
                return video_path, "Video exists"

            # Check for any available formats
            if not info_dict.get('formats'):
                logging.warning("No downloadable formats available")
                return None, "no formats"

            caption = info_dict.get('description', '')
            first_sentence = get_first_sentence(caption)

            filesize = info_dict.get('filesize') or info_dict.get('filesize_approx', 0)
            if filesize > max_filesize_mb * 1024 * 1024:
                logging.warning(f"Video exceeds {max_filesize_mb}MB")
                return None, "size exceeds"

            ydl.download([url])

            # Handle possible different extensions
            temp_path = ydl.prepare_filename(info_dict)
            if os.path.exists(temp_path):
                if not temp_path.endswith('.mp4'):
                    os.rename(temp_path, video_path)
            elif not os.path.exists(video_path):
                raise FileNotFoundError("Downloaded file not found")

        return video_path, first_sentence

    except Exception as e:
        logging.error(f"Download failed: {e}")
        return None, str(e)