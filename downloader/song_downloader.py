import os
import re
from yt_dlp import YoutubeDL
import eyed3

def download_song(title, artist):
    """
    Downloads a song as an MP3 based on the title and artist and tags it with artist info.

    Args:
        title (str): The title of the song.
        artist (str): The artist of the song.

    Returns:
        str: The file path of the downloaded MP3.
    """
    # Ensure the output directory exists
    output_dir = "temp/audios"
    os.makedirs(output_dir, exist_ok=True)

    # Construct the search query
    query = f"{title} {artist} audio"

    # Configure yt-dlp options
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'quiet': True,
        'noplaylist': True,
    }

    print("Downloading audio...")
    with YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(f"ytsearch:{query}", download=True)

    # If multiple entries, get the first one
    if 'entries' in result:
        result = result['entries'][0]

    # Dynamically detect the downloaded file's name
    downloaded_files = os.listdir(output_dir)
    print("Downloaded files in directory:", downloaded_files)

    # Match the expected MP3 file in the directory
    downloaded_file = None
    for file in downloaded_files:
        if file.endswith(".mp3") and title in file:
            downloaded_file = os.path.join(output_dir, file)
            break

    if not downloaded_file:
        raise FileNotFoundError(f"The MP3 file was not created: {output_dir}")

    print(f"Detected downloaded file: {downloaded_file}")

    # Add artist name as a tag using eyed3
    audiofile = eyed3.load(downloaded_file)
    if audiofile is None:
        raise ValueError("The file is not a valid MP3 or could not be processed.")

    audiofile.tag.artist = artist
    audiofile.tag.save()

    # Test if the file can be opened
    with open(downloaded_file, "rb") as song_file:
        song_file.read(1)  # Read the first byte to ensure the file is valid

    return downloaded_file

# # Example usage
# if __name__ == "__main__":
#     try:
#         song_path = download_song("Ishq Hai", "Mismatched - Cast/Anurag Saikia/Romy/Amarabha Banerjee/Varun Jain/Madhubanti Bagchi/Raj Shekhar")
#         print(f"Song downloaded to: {song_path}")
#     except Exception as e:
#         print(f"Error: {e}")
