import requests
import base64
import hmac
import hashlib
import time

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
        # Read audio file
        with open(audio_path, 'rb') as audio_file:
            audio_data = audio_file.read()

        # Prepare request data
        http_method = "POST"
        http_uri = "/v1/identify"
        data_type = "audio"
        signature_version = "1"
        timestamp = str(int(time.time()))
        
        string_to_sign = (
            f"{http_method}\n{http_uri}\n{access_key}\n{data_type}\n{signature_version}\n{timestamp}"
        )
        
        # Use hmac to generate the signature
        signature = base64.b64encode(
            hmac.new(
                access_secret.encode('utf-8'),
                string_to_sign.encode('utf-8'),
                hashlib.sha1
            ).digest()
        ).decode('utf-8')

        # Make request using multipart/form-data
        files = {
            'sample': ('sample.mp3', audio_data)
        }

        data = {
            'access_key': access_key,
            'data_type': data_type,
            'signature_version': signature_version,
            'signature': signature,
            'sample_bytes': len(audio_data),
            'timestamp': timestamp
        }

        response = requests.post(
            f"{host}{http_uri}",
            data=data,
            files=files
        )

        return response.json()
    except Exception as e:
        raise Exception(f"Error recognizing song: {e}")