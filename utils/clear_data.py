import os, shutil

def delete_all():
    folders = ['temp/audios', 'temp/videos']  # Predefined folders
    for folder in folders:
        if os.path.exists(folder):
            [shutil.rmtree(p) if os.path.isdir(p) else os.remove(p) for p in (os.path.join(folder, f) for f in os.listdir(folder))]
    print('File Deleted')
# delete_all()
