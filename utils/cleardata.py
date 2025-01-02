import os
import shutil
import logging

def clear_folder(folder):
    """Delete all contents of a folder."""
    if not os.path.exists(folder):
        logging.warning(f"Folder '{folder}' does not exist.")
        return "already deleted"
    
    if not os.listdir(folder):  # Check if the folder is empty
        logging.info(f"Folder '{folder}' is already empty.")
        return "already deleted"
    
    try:
        # Clear folder contents
        for item in os.listdir(folder):
            item_path = os.path.join(folder, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)
        logging.info(f"Contents of '{folder}' deleted successfully.")
        return "deleted"
    except Exception as e:
        logging.error(f"Error clearing folder '{folder}': {e}")
        return "failed"

def delete_folders(folders):
    """Delete contents of multiple folders."""
    results = {}
    for folder in folders:
        results[folder] = clear_folder(folder)
    return results

def delete_all():
    """Deletes all predefined folders and their contents."""
    folders = [
        'data',
        'database/__pycache__',
        'decorator/__pycache__',
        'downloader/__pycache__',
        'handlers/__pycache__',
        'handlers/commands/__pycache__',
        'handlers/messages/__pycache__',
        'utils/__pycache__',
        '__pycache__'
    ]
    return delete_folders(folders)

def delete_cache():
    """Deletes only cache folders."""
    folders = [
        'database/__pycache__',
        'decorator/__pycache__',
        'downloader/__pycache__',
        'handlers/__pycache__',
        'handlers/commands/__pycache__',
        'handlers/messages/__pycache__',
        'utils/__pycache__',
        '__pycache__'
    ]
    delete_folders(folders)
    logging.info("Cache deleted successfully.")
    return True

def delete_files(*file_paths):
    """Delete specific files."""
    try:
        for file_path in file_paths:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
                logging.info(f"File '{file_path}' deleted successfully.")
            elif file_path:
                logging.warning(f"File '{file_path}' does not exist.")
        return True
    except Exception as e:
        logging.error(f"Error deleting file(s): {e}")
        return False