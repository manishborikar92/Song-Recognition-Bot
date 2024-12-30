import os
import eyed3
import logging
from yt_dlp import YoutubeDL

def download_song(title, artist):
    """
    Downloads a song as an MP3 based on the title and artist and tags it with artist info.

    Args:
        title (str): The title of the song.
        artist (str): The artist of the song.

    Returns:
        str: The file path of the downloaded MP3.
    """
    try:
        # Ensure the output directory exists
        output_dir = "data/music"
        os.makedirs(output_dir, exist_ok=True)

        # Generate a sanitized filename (avoid invalid characters for different OS)
        sanitized_title = title.replace('/', '').replace('\\', '').replace(':', '')
        file_path = os.path.join(output_dir, f"{sanitized_title}.mp3")

        # If the song already exists, return the file path
        if os.path.exists(file_path):
            logging.info(f"Song already exists: {file_path}")
            return file_path

        # Construct the search query
        query = f"{title} {artist} audio"

        # Configure yt-dlp options for faster downloads
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(output_dir, f'{sanitized_title}.%(ext)s'),
            'quiet': True,  # Reduce console output
            'noplaylist': True,
            'extractaudio': True,  # Avoid downloading video
            'cookiefile': 'cookies.txt',
        }

        # Download the song
        with YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(f"ytsearch:{query}", download=True)

        # Ensure the file exists and is not corrupt
        if not os.path.isfile(file_path):
            raise FileNotFoundError("The MP3 file was not downloaded correctly.")

        # Add artist name as tag using eyed3
        audiofile = eyed3.load(file_path)
        audiofile.tag.artist = artist  # Set artist tag
        audiofile.tag.save()  # Save changes

        # Test if the file can be opened
        with open(file_path, "rb") as song_file:
            song_file.read(1)  # Read the first byte to ensure the file is valid

        logging.info('Song Downloaded')
        return file_path
    
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return None


# # Example usage
# if __name__ == "__main__":
#     logging.basicConfig(level=logging.INFO)
#     try:
#         song_path = download_song("Ishq Hai", "Mismatched - Cast/Anurag Saikia/Romy/Amarabha Banerjee/Varun Jain/Madhubanti Bagchi/Raj Shekhar")
#         logging.info(f"Song downloaded to: {song_path}")
#     except Exception as e:
#         logging.info(f"Error: {e}")
