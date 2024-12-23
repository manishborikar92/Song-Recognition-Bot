import os
import shutil

def delete_files_in_downloads():
    """
    Deletes all files and directories in the 'data/downloads' folder.
    """
    downloads_folder = 'data/downloads'

    if not os.path.exists(downloads_folder):
        print(f"The folder {downloads_folder} does not exist.")
        return

    try:
        for entry in os.scandir(downloads_folder):
            if entry.is_file():
                os.unlink(entry.path)  # Delete the file
            elif entry.is_dir():
                shutil.rmtree(entry.path)  # Delete the directory
    except Exception as e:
        print(f"Error cleaning the downloads folder: {e}")
