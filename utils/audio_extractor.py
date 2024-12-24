import os
from pydub import AudioSegment

def convert_video_to_mp3(video_path):
    try:
        # Ensure the 'temp/audios' directory exists
        save_dir = 'temp/audios'
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        # Get the video filename without extension
        video_filename = os.path.basename(video_path)
        audio_filename = os.path.splitext(video_filename)[0] + '.mp3'  # Change extension to .mp3
        audio_path = os.path.join(save_dir, audio_filename)
        
        # Convert video to audio using ffmpeg (via pydub)
        # Load the video file (pydub supports mp4 if ffmpeg is correctly installed)
        audio = AudioSegment.from_file(video_path, format='mp4')  # 'mp4' is the video format
        
        # Export the audio as mp3
        audio.export(audio_path, format='mp3')
        
        print('Audio Extracted')
        return audio_path
    except Exception as e:
        return str(e)

# # Example usage
# video_path = 'temp/videos\AliGatieItsYouOfficialLyricsVideo.mp4'
# audio_path = convert_video_to_mp3(video_path)
# print(f"Converted audio path: {audio_path}")
