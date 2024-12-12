import os
import shutil

# Function to delete all files in the 'data/downloads' folder
def delete_files_in_downloads():
    downloads_folder = 'data/downloads'
    for filename in os.listdir(downloads_folder):
        file_path = os.path.join(downloads_folder, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)  # Delete the file
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)  # Delete the directory
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")