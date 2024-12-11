import os
import yt_dlp
import subprocess

def download_and_convert_song(song_title, artist_name):
    # Create the download folder if it doesn't exist
    download_folder = 'data/downloads'
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    # Delete any existing file with the song title, regardless of format
    for ext in ['mp3', 'm4a', 'flac', 'ogg', 'wav']:  # Add more formats as needed
        file_path = f"data/downloads/{song_title}.{ext}"
        if os.path.exists(file_path):
            os.remove(file_path)

    # Search query for the song
    query = f"{song_title} {artist_name}"

    # Options for yt-dlp to download the best available audio
    ydl_opts = {
        'format': 'bestaudio/best',  # Download the best audio format available
        'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s'),  # Save to download folder
        'noplaylist': True,  # Avoid downloading playlists
        'quiet': False,  # Show download progress
    }

    # Use yt-dlp to download the audio
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.download([f"ytsearch:{query}"])

    # After downloading, check the folder for the downloaded file
    if result == 0:
        # Get the downloaded file by looking for files with the song title
        files_in_download_folder = os.listdir(download_folder)
        
        # Look for the most likely match (could use more complex matching if needed)
        downloaded_file = None
        for file in files_in_download_folder:
            if song_title.lower() in file.lower():  # Match case-insensitive
                downloaded_file = file
                break
        
        if downloaded_file is None:
            print("No matching file found for the song.")
            return None
        
        downloaded_file_path = os.path.join(download_folder, downloaded_file)
        
        # Define the output MP3 path
        mp3_output_path = os.path.join(download_folder, f"{song_title}.mp3")

        # Use FFmpeg to convert the audio to MP3 at 320kbps
        command = [
            'ffmpeg', 
            '-i', downloaded_file_path,  # Input file
            '-vn',  # Disable video
            '-ar', '44100',  # Set audio sample rate to 44.1kHz
            '-ac', '2',  # Stereo output
            '-b:a', '320k',  # Set bitrate to 320kbps
            mp3_output_path  # Output file path
        ]
        try:
            subprocess.run(command, check=True)
            # Remove the original file after conversion
            os.remove(downloaded_file_path)
            return mp3_output_path
        except subprocess.CalledProcessError as e:
            print(f"Error during FFmpeg conversion: {e}")
            return None
    else:
        print("Error downloading the song.")
        return None

# Example usage
# song_title = "Shape of You"
# artist_name = "Ed Sheeran"
# file_path = download_and_convert_song(song_title, artist_name)

# if file_path:
#     print(f"Song downloaded and converted successfully: {file_path}")
# else:
#     print("Error downloading or converting the song.")
