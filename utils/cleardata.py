import os
import shutil
import logging

def clear_folder(folder):
    """Helper function to delete all contents of a folder."""
    try:
        if os.path.exists(folder):
            # Check if the folder is empty
            if not os.listdir(folder):  # Folder is empty
                logging.info(f"Folder '{folder}' is already empty.")
                return "already deleted"
            
            # Folder is not empty, proceed with clearing contents
            for item in os.listdir(folder):
                item_path = os.path.join(folder, item)
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)
            logging.info(f"Contents of '{folder}' deleted successfully.")
            return "deleted"
        else:
            logging.warning(f"Folder '{folder}' does not exist.")
            return "already deleted"
    except Exception as e:
        logging.error(f"Error clearing folder '{folder}': {e}")
        return "failed"


def delete_all():
    """Deletes all predefined folders and their contents."""
    folders = ['data', 'downloader/__pycache__', 'handlers/__pycache__', 'utils/__pycache__', '__pycache__']
    results = {}
    for folder in folders:
        result = clear_folder(folder)
        results[folder] = result
    return results
    
def delete_cache():
    """Deletes only cache folders."""
    folders = ['downloader/__pycache__', 'handlers/__pycache__', 'utils/__pycache__', '__pycache__']
    try:
        for folder in folders:
            clear_folder(folder)
        logging.info("Cache deleted successfully.")
        return True
    except Exception as e:
        logging.error(f"Error deleting cache: {e}")
        return False

def delete_file(video_path=None, audio_path=None, song_path=None):
    """Deletes specific files and predefined folders."""
    try:
        # Delete specific files if provided
        for file_path in [video_path, audio_path, song_path]:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
                logging.info(f"File '{file_path}' deleted successfully.")
            elif file_path:
                logging.warning(f"File '{file_path}' does not exist.")

        logging.info("Specified files and folders deleted successfully.")
        return True
    except Exception as e:
        logging.error(f"Error deleting file(s): {e}")
        return False