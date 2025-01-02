import os
import logging
import requests
import instaloader

def get_first_sentence(caption: str) -> str:
    """Get the first non-empty line from the caption."""
    return next((line.strip() for line in caption.splitlines() if line.strip()), "No caption available")

def download_instagram_reel(url):
    """
    Downloads an Instagram reel and extracts the first sentence of its caption.

    Args:
        url (str): Instagram reel URL.

    Returns:
        tuple: (str, str) Video file path and the first sentence of the caption, or an error message.
    """
    # Initialize Instaloader
    L = instaloader.Instaloader()

    # Directory to save videos
    save_dir = 'data/videos'
    os.makedirs(save_dir, exist_ok=True)

    # Extract the shortcode from the URL
    try:
        shortcode = url.split("/")[-2]
        if not shortcode:
            raise ValueError("Invalid Instagram URL. Could not extract shortcode.")
    except (IndexError, ValueError) as e:
        logging.error(e)
        return None, "Invalid URL format."

    # Define the file path for the video
    video_path = os.path.join(save_dir, f"{shortcode}.mp4")

    # Skip download if the video already exists
    if os.path.exists(video_path):
        logging.info(f"Instagram video already exists at: {video_path}")
        return video_path, "Video already exists."

    try:
        # Fetch the post using the shortcode
        post = instaloader.Post.from_shortcode(L.context, shortcode)

        # Verify if it's a video post
        if not post.is_video:
            logging.warning("The provided URL does not point to a reel (video).")
            return None, "The provided URL does not point to a reel (video)."

        # Get the video URL and caption
        video_url = post.video_url
        caption = post.caption or "No caption available"

        # Extract the first sentence of the caption
        first_sentence = get_first_sentence(caption)

        # Download the video
        logging.info("Downloading Instagram reel...")
        with requests.get(video_url, stream=True) as response:
            response.raise_for_status()  # Raise an exception for HTTP errors
            with open(video_path, 'wb') as video_file:
                for chunk in response.iter_content(chunk_size=64 * 1024):  # 64 KB chunks
                    video_file.write(chunk)

        logging.info("Instagram reel downloaded successfully.")
        return video_path, first_sentence

    except requests.exceptions.RequestException as e:
        logging.error(f"Request error: {e}")
        return None, f"Request error: {e}"
    except instaloader.exceptions.InstaloaderException as e:
        logging.error(f"Instaloader error: {e}")
        return None, f"Instaloader error: {e}"
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return None, f"Unexpected error: {e}"