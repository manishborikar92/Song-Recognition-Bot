import os
import yt_dlp
import subprocess
from concurrent.futures import ThreadPoolExecutor

def download_and_convert_song(song_title, artist_name):
    """
    Download and convert a song to MP3 format.
    
    Args:
        song_title (str): Title of the song.
        artist_name (str): Name of the artist.
    
    Returns:
        str: Path to the converted MP3 file, or None if an error occurred.
    """
    # Create the download folder if it doesn't exist
    download_folder = 'data/downloads'
    os.makedirs(download_folder, exist_ok=True)

    # Delete any existing file with the song title
    existing_files = [
        os.path.join(download_folder, f) 
        for f in os.listdir(download_folder) 
        if song_title.lower() in f.lower() and f.endswith(('.mp3', '.m4a', '.flac', '.ogg', '.wav'))
    ]
    for file_path in existing_files:
        os.remove(file_path)

    # Search query for the song
    query = f"{song_title} {artist_name}"

    # Options for yt-dlp
    ydl_opts = {
        'format': 'bestaudio/best',  # Download only audio
        'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s'),  # Save to download folder
        'noplaylist': True,  # Avoid playlists
        'quiet': True,  # Suppress verbose output
        'postprocessors': [
            {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '320'},
        ],
    }

    # Download the audio using yt-dlp
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.download([f"ytsearch:{query}"])

        if result == 0:
            # Find the downloaded MP3 file
            files_in_download_folder = os.listdir(download_folder)
            for file in files_in_download_folder:
                if song_title.lower() in file.lower() and file.endswith('.mp3'):
                    return os.path.join(download_folder, file)

        print("No matching MP3 file found.")
        return None
    except Exception as e:
        print(f"Error downloading or converting the song: {e}")
        return None


# Example usage
# song_title = "Shape of You"
# artist_name = "Ed Sheeran"
# file_path = download_and_convert_song(song_title, artist_name)

# if file_path:
#     print(f"Song downloaded and converted successfully: {file_path}")
# else:
#     print("Error downloading or converting the song.")
