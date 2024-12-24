import os
import yt_dlp

def get_first_sentence(caption: str) -> str:
    # Split the caption by line breaks and get the first non-empty line
    lines = caption.split('\n')
    first_line = next((line for line in lines if line.strip()), "")  # Find the first non-empty line
    return first_line

def download_youtube_video(url):
    try:
        # Set up yt-dlp options
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',  # Get the best video and audio streams
            'outtmpl': 'temp/videos/%(title)s.%(ext)s',  # Save with the title as filename
            'noplaylist': True,  # Avoid downloading entire playlists
            'merge_output_format': 'mp4',  # Merge audio and video into mp4 if needed
            'postprocessors': [{  # Force conversion to mp4
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
        }

        # Download the video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            
            # Get the video path after download
            video_path = ydl.prepare_filename(info_dict)
            
            # Replace the file extension with .mp4
            video_path = video_path.rsplit('.', 1)[0] + '.mp4'
            
            # Get the video description (caption)
            caption = info_dict.get('description', 'No description')
            
            # Get the first non-empty line of the description
            first_sentence = get_first_sentence(caption)
        
        return video_path, first_sentence
    except Exception as e:
        return str(e), None

# # Example usage
# url = "https://youtube.com/shorts/2_zGMxCPk-Y?si=b12iFJoCuLR-DIQr"  # Replace with an actual YouTube video URL
# video_path, description = download_youtube_video(url)
# print(f"Downloaded video path: {video_path}\nDescription: {description}")
