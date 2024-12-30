import os, shutil

def delete_all():
    folders = ['data', 'downloader/__pycache__', 'handlers/__pycache__', 'utils/__pycache__', '__pycache__']  # Predefined folders
    for folder in folders:
        if os.path.exists(folder):
            [shutil.rmtree(p) if os.path.isdir(p) else os.remove(p) for p in (os.path.join(folder, f) for f in os.listdir(folder))]
    print('File Deleted')
    return True

def delete_cache():
    folders = ['downloader/__pycache__', 'handlers/__pycache__', 'utils/__pycache__', '__pycache__']  # Predefined folders
    for folder in folders:
        if os.path.exists(folder):
            [shutil.rmtree(p) if os.path.isdir(p) else os.remove(p) for p in (os.path.join(folder, f) for f in os.listdir(folder))]
    print('Cache Deleted')
# delete_all()
