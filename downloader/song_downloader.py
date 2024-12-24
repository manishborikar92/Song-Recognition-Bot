import os
import yt_dlp

def download_song(title, artist):
    try:
        # Ensure the 'temp/audio' directory exists
        save_dir = 'temp/audios'
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        # Search query for the song on YouTube
        search_query = f"{title} {artist}"
        
        # Set up yt-dlp options
        ydl_opts = {
            'format': 'bestaudio/best',  # Get the best audio format available
            'outtmpl': f'{save_dir}/%(title)s.%(ext)s',  # Save audio with the title as filename
            'noplaylist': True,  # Avoid downloading playlists
            'postprocessors': [{  # Convert the audio to mp3
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,  # Suppress yt-dlp output
        }

        # Search and download the song
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_results = ydl.extract_info(f"ytsearch:{search_query}", download=True)['entries'][0]
            audio_path = os.path.join(save_dir, f"{search_results['title']}.mp3")

        return audio_path
    except Exception as e:
        return str(e)

# # Example usage
# title = "Blinding Lights"
# artist = "The Weeknd"
# audio_path = download_song(title, artist)
# print(f"Downloaded audio path: {audio_path}")
