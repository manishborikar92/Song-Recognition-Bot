import os
import logging
from pydub import AudioSegment

def convert_video_to_mp3(video_path, max_duration_minutes=1):
    """
    Converts a video file to an MP3 audio file, trimming it to the specified duration if necessary.

    Args:
        video_path (str): Path to the video file.
        max_duration_minutes (int): Maximum allowed duration of the audio in minutes.

    Returns:
        str: Path to the extracted audio file, or an error message.
    """
    try:
        # Define the directory to save audio files
        save_dir = 'data/audios'
        os.makedirs(save_dir, exist_ok=True)  # Ensure directory exists

        # Extract filename and define audio path
        video_name = os.path.splitext(os.path.basename(video_path))[0]
        audio_path = os.path.join(save_dir, f"{video_name}.mp3")
        
        # Skip conversion if the audio already exists
        if os.path.exists(audio_path):
            logging.info(f"Audio already exists at: {audio_path}")
            return audio_path

        # Convert video to audio using ffmpeg (via pydub)
        logging.info(f"Processing video: {video_path}")
        audio = AudioSegment.from_file(video_path)  # Automatically detects format

        # Check and trim audio if it's longer than the maximum allowed duration
        max_duration_ms = max_duration_minutes * 60 * 1000  # Convert minutes to milliseconds
        if len(audio) > max_duration_ms:
            logging.info(f"Audio duration exceeds {max_duration_minutes} minutes. Trimming...")
            audio = audio[:max_duration_ms]

        # Export the audio as mp3
        audio.export(audio_path, format='mp3')
        logging.info(f"Audio extracted at: {audio_path}")
        return audio_path

    except FileNotFoundError:
        error_msg = f"File not found: {video_path}"
        logging.error(error_msg)
        return None
    except Exception as e:
        error_msg = f"An error occurred: {e}"
        logging.error(error_msg)
        return None

def trim_audio(audio_path, max_duration_minutes=1):
    try:
        # Define the directory to save audio files
        save_dir = 'data/audios'
        os.makedirs(save_dir, exist_ok=True)  # Ensure directory exists

        # Load the audio file
        audio = AudioSegment.from_file(audio_path)

        # Check and trim audio if it's longer than the maximum allowed duration
        max_duration_ms = max_duration_minutes * 60 * 1000  # Convert minutes to milliseconds
        if len(audio) > max_duration_ms:
            logging.info(f"Audio duration exceeds {max_duration_minutes} minutes. Trimming...")
            audio = audio[:max_duration_ms]  # Trim the audio

        # Create the output path
        output_path = os.path.join(save_dir, os.path.basename(audio_path))

        # Export the trimmed audio as mp3
        audio.export(output_path, format='mp3')
        logging.info(f"Trimmed audio saved at: {output_path}")
        return output_path

    except Exception as e:
        error_msg = f"An error occurred while trimming audio: {e}"
        logging.error(error_msg)
        return None
