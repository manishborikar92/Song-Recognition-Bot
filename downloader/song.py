import os
import re
import logging
from mutagen.easyid3 import EasyID3
from mutagen import MutagenError
from mutagen.id3 import ID3NoHeaderError
from yt_dlp import YoutubeDL

def download_song(title, artist, quality=192):
    """
    Enhanced audio downloader with PO token workaround and better format handling.
    
    Args:
        title (str): Song title
        artist (str): Song artist
        quality (int): Audio quality (96-320 kbps)

    Returns:
        str: Path to downloaded MP3 or None
    """
    try:
        output_dir = "data/music"
        os.makedirs(output_dir, exist_ok=True)
        sanitized_title = re.sub(r'[^\w\s()-.,]', '', title)[:100].strip()
        file_path = os.path.join(output_dir, f"{sanitized_title}.mp3")

        if os.path.exists(file_path):
            logging.info(f"Song exists: {file_path}")
            return file_path

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(output_dir, f'{sanitized_title}.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': str(quality),
            }],
            'http_headers': {
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://www.youtube.com/',
            },
            'force_ip': '4',
            'concurrent_fragment_downloads': 8,
            'retries': 10,
            'fragment_retries': 15,
            'skip_unavailable_fragments': True,
            'nocheckcertificate': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            'extractor_args': {
                'youtube': {
                    'player_client': 'web',
                    'skip': ['hls', 'dash'],
                }
            },
            'format_sort': ['ext', 'acodec:mp3'],
            'check_formats': 'selected',
        }

        with YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(f"ytsearch:{title} {artist}", download=False)
            if not result or 'entries' not in result:
                raise ValueError("No search results found")
            
            # Verify audio formats are available
            entry = result['entries'][0]
            if not entry.get('formats'):
                raise ValueError("No downloadable formats available")

            ydl.download([f"ytsearch:{title} {artist}"])

        # Handle possible different extensions
        temp_path = ydl.prepare_filename(entry).replace('.webm', '.mp3')
        if os.path.exists(temp_path) and temp_path != file_path:
            os.rename(temp_path, file_path)

        # Metadata handling
        try:
            audio = EasyID3(file_path)
        except ID3NoHeaderError:
            audio = EasyID3()
            audio.save(file_path)
            audio = EasyID3(file_path)
        
        audio['artist'] = artist
        audio['title'] = title
        audio.save()

        return file_path

    except Exception as e:
        logging.error(f"Download failed: {e}")
        return None