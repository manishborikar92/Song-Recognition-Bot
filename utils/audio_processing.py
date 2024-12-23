import requests
import ffmpeg
import os
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def download_video(video_url, output_path="data/downloads/video.mp4"):
    """
    Downloads a video from the given URL more efficiently.

    Args:
        video_url (str): The URL of the video.
        output_path (str): Path to save the downloaded video.

    Returns:
        str: Path to the downloaded video.
    """
    try:
        # Create session with retry logic
        session = requests.Session()
        retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
        session.mount("http://", HTTPAdapter(max_retries=retries))
        session.mount("https://", HTTPAdapter(max_retries=retries))

        response = session.get(video_url, stream=True)
        response.raise_for_status()

        # Create parent directory if not exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Save video in larger chunks
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=10240):  # Larger chunk size for faster writes
                if chunk:  # Filter out keep-alive chunks
                    f.write(chunk)

        return output_path
    except Exception as e:
        print(f"Error downloading video: {e}")
        return None

def extract_audio(video_path, output_path="data/downloads/audio.mp3"):
    """
    Extracts audio from a video and saves it as an MP3 file efficiently.

    Args:
        video_path (str): Path to the video file.
        output_path (str): Path to save the extracted audio.

    Returns:
        str: Path to the extracted audio file.
    """
    try:
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Use FFmpeg for audio extraction with optimized options
        ffmpeg.input(video_path).output(
            output_path, 
            format="mp3", 
            acodec="libmp3lame",  # Use libmp3lame for better MP3 performance
            audio_bitrate="192k"  # Set audio bitrate
        ).run(quiet=True, overwrite_output=True)

        return output_path
    except Exception as e:
        print(f"Error extracting audio: {e}")
        return None
