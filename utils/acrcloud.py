import os
import time
import json
import hmac
import base64
import logging
import hashlib
import requests
from pydub import AudioSegment
from config import ACR_HOST, ACR_ACCESS_KEY, ACR_ACCESS_SECRET, ACR_BEARER_TOKEN, ACR_ENDPOINT_URL

# Create a session for faster repeated requests
session = requests.Session()

def recognize_song(audio_path):
    """
    Recognize a song using ACRCloud.

    Args:
        audio_path (str): The path to the audio file.
        host (str): The ACRCloud host URL.
        access_key (str): Your ACRCloud access key.
        access_secret (str): Your ACRCloud access secret.

    Returns:
        dict: The song recognition result.
    """
    host = ACR_HOST
    access_key = ACR_ACCESS_KEY
    access_secret = ACR_ACCESS_SECRET

    try:
        # Prepare request data
        http_method = "POST"
        http_uri = "/v1/identify"
        data_type = "audio"
        signature_version = "1"
        timestamp = str(int(time.time()))

        string_to_sign = (
            f"{http_method}\n{http_uri}\n{access_key}\n{data_type}\n{signature_version}\n{timestamp}"
        )

        # Generate the signature
        signature = base64.b64encode(
            hmac.new(
                access_secret.encode(),
                string_to_sign.encode(),
                hashlib.sha1
            ).digest()
        ).decode()

        # Open the audio file
        with open(audio_path, 'rb') as audio_file:
            file_size = os.path.getsize(audio_path)
            files = {
                'sample': ('sample.mp3', audio_file)
            }
            data = {
                'access_key': access_key,
                'data_type': data_type,
                'signature_version': signature_version,
                'signature': signature,
                'sample_bytes': file_size,
                'timestamp': timestamp
            }

            # Make the POST request
            response = session.post(
                f"{host}{http_uri}",
                data=data,
                files=files,
                timeout=10
            )

        response_data = response.json()

        # Handle errors
        if response_data.get("status", {}).get("code") != 0:
            raise Exception(f"ACRCloud Error: {response_data.get('status', {}).get('msg')}")

        # Extract metadata
        if "metadata" in response_data and "music" in response_data["metadata"]:
            song_info = response_data
            song = song_info["metadata"]["music"][0]
            title = song.get("title", "Unknown Title")
            artists = ", ".join(artist["name"] for artist in song.get("artists", []))
            logging.info(f"Title: {title}\nArtists: {artists}")
        else:
            logging.error("No match found in ACRCloud database.")
            return response_data

        return response_data
    except Exception as e:
        raise Exception(f"Error recognizing song: {e}")
    

def get_song_info(title: str, artist: str):
    """
    Searches for the original song name and artist using the ACRCloud API.
    """
    API_URL = ACR_ENDPOINT_URL
    API_KEY = ACR_BEARER_TOKEN
    
    headers = {
        'Authorization': f'Bearer {API_KEY}'
    }
    params = {
        'query': json.dumps({"track": title, "artists": artist}),
        'format': 'json'
    }

    try:
        response = requests.get(API_URL, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        if data.get("data"):
            # Extract song data
            song = data["data"][0]
            title = song.get("name", "Unknown Title")
            artists = ", ".join(artist["name"] for artist in song.get("artists", []))
            album = song.get("album", {}).get("name", "Unknown Album")
            release_date = song.get("album", {}).get("release_date", "Unknown Release Date")
            
            # Extract YouTube and Spotify links
            youtube_links = [
                yt.get("link") 
                for yt in song.get("external_metadata", {}).get("youtube", [])
                if yt.get("link")
            ]
            spotify_links = [
                sp.get("link") 
                for sp in song.get("external_metadata", {}).get("spotify", [])
                if sp.get("link")
            ]
            
            # Use the first link or a default search link
            youtube_link = youtube_links[0] if youtube_links else f'https://www.youtube.com/results?search_query={title}'
            spotify_link = spotify_links[0] if spotify_links else f'https://open.spotify.com/search/{title}'
            
            # logging.info results
            logging.info(f"Title: {title}")
            logging.info(f"Artists: {artists}")
            logging.info(f"Album: {album}")
            logging.info(f"Release Date: {release_date}")
            logging.info(f"YouTube Link: {youtube_link}")
            logging.info(f"Spotify Link: {spotify_link}")
            
            return {
                "title": title,
                "artists": artists,
                "album": album,
                "release_date": release_date,
                "youtube_link": youtube_link,
                "spotify_link": spotify_link,
            }

        logging.error("No results found.")
        return None

    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching song info: {e}")
        return None



# # Example usage
# if __name__ == "__main__":
#     # Paths
#     input_audio_path = r'data/audios/The Weeknd - Blinding Lights (Official Video).mp3'

#     # ACRCloud credentials from .env
#     acr_host = os.getenv("ACR_HOST")
#     acr_access_key = os.getenv("ACR_ACCESS_KEY")
#     acr_access_secret = os.getenv("ACR_ACCESS_SECRET")

#     if not acr_host or not acr_access_key or not acr_access_secret:
#         raise ValueError("Missing required environment variables: ACR_HOST, ACR_ACCESS_KEY, ACR_ACCESS_SECRET")

#     # Recognize song
#     recognize_song(input_audio_path, acr_host, acr_access_key, acr_access_secret)


# # Example usage
# if __name__ == "__main__":
#     # Paths
#     input_audio_path = r'data/audios/The Weeknd - Blinding Lights (Official Video).mp3'

#     # ACRCloud credentials from .env
#     acr_host = os.getenv("ACR_HOST")
#     acr_access_key = os.getenv("ACR_ACCESS_KEY")
#     acr_access_secret = os.getenv("ACR_ACCESS_SECRET")

#     if not acr_host or not acr_access_key or not acr_access_secret:
#         raise ValueError("Missing required environment variables: ACR_HOST, ACR_ACCESS_KEY, ACR_ACCESS_SECRET")

#     # Recognize song
#     recognize_song(input_audio_path, acr_host, acr_access_key, acr_access_secret)
