import requests
import ffmpeg
import os

def download_video(video_url, output_path="data/downloads/video.mp4"):
    """
    Downloads a video from the given URL.

    Args:
        video_url (str): The URL of the video.
        output_path (str): Path to save the downloaded video.

    Returns:
        str: Path to the downloaded video.
    """
    try:
        response = requests.get(video_url, stream=True)
        response.raise_for_status()

        # Save video in chunks
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)

        return output_path
    except Exception as e:
        print(f"Error downloading video: {e}")
        return None

def extract_audio(video_path, output_path="data/downloads/audio.mp3"):
    """
    Extracts audio from a video and saves it as an MP3 file.

    Args:
        video_path (str): Path to the video file.
        output_path (str): Path to save the extracted audio.

    Returns:
        str: Path to the extracted audio file.
    """
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        ffmpeg.input(video_path).output(output_path, format="mp3").run(overwrite_output=True)
        return output_path
    except Exception as e:
        print(f"Error extracting audio: {e}")
        return None
