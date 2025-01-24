import os
import re
import logging
from mutagen.easyid3 import EasyID3
from mutagen import MutagenError
from mutagen.id3 import ID3NoHeaderError
from yt_dlp import YoutubeDL

def download_song(title, artist):
    """
    Downloads a song as MP3 based on title and artist with optimized performance,
    and tags it with metadata using mutagen.

    Args:
        title (str): Song title
        artist (str): Song artist

    Returns:
        str: File path of downloaded MP3 or None if failed
    """
    try:
        output_dir = "data/music"
        os.makedirs(output_dir, exist_ok=True)

        sanitized_title = re.sub(r'[^a-zA-Z0-9 ()\-.,]', '', title)
        file_path = os.path.join(output_dir, f"{sanitized_title}.mp3")

        if os.path.exists(file_path):
            logging.info(f"Song already exists: {file_path}")
            return file_path

        ydl_opts = {
            'format': 'bestaudio',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(output_dir, f'{sanitized_title}.%(ext)s'),
            'quiet': False,
            'noplaylist': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'concurrent_fragment_downloads': 5,  # Parallel downloads for DASH
            'socket_timeout': 10,  # Faster timeout
            'nocheckcertificate': True,  # Bypass SSL verification for speed
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([f"ytsearch:{title} {artist} audio"])

        if not os.path.isfile(file_path):
            raise FileNotFoundError("MP3 file not downloaded correctly")

        # Add metadata with mutagen
        try:
            audio = EasyID3(file_path)
        except ID3NoHeaderError:
            audio = EasyID3()
            audio.save(file_path)
            audio = EasyID3(file_path)
        
        audio['artist'] = artist
        audio['title'] = title
        audio.save()

        logging.info('Song downloaded successfully')
        return file_path

    except Exception as e:
        logging.error(f"Download failed: {e}")
        return None
