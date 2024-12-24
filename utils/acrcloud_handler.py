import requests
import base64
import hmac
import hashlib
import time

# Create a session for faster repeated requests
session = requests.Session()

def recognize_song(audio_path, host, access_key, access_secret):
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

        # Stream the audio file directly to avoid loading the entire file into memory
        with open(audio_path, 'rb') as audio_file:
            files = {
                'sample': ('sample.mp3', audio_file)
            }
            data = {
                'access_key': access_key,
                'data_type': data_type,
                'signature_version': signature_version,
                'signature': signature,
                'sample_bytes': audio_file.seek(0, 2),  # Get file size without reading all data
                'timestamp': timestamp
            }
            audio_file.seek(0)  # Reset file pointer

            # Make the POST request
            response = session.post(
                f"{host}{http_uri}",
                data=data,
                files=files,
                timeout=10  # Set a reasonable timeout
            )
            
        # Return the parsed JSON response
        return response.json()
    except Exception as e:
        raise Exception(f"Error recognizing song: {e}")