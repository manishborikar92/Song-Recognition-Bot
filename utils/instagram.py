import instaloader

def scrape_instagram_post(url):
    """
    Fetches the caption and video URL from an Instagram post or reel.

    Args:
        url (str): The Instagram link.

    Returns:
        tuple: Caption (str), Video URL (str)
    """
    try:
        # Extract the shortcode from the URL
        shortcode = url.split("/")[-2]
        
        # Initialize Instaloader
        loader = instaloader.Instaloader()
        
        # Get post details
        post = instaloader.Post.from_shortcode(loader.context, shortcode)
        
        # Return caption and video URL
        return post.caption, post.video_url
    except Exception as e:
        print(f"Error fetching Instagram post: {e}")
        return None, None
