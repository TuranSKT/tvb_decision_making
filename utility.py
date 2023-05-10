import zipfile
import os

def toZip(folder_path, zip_path):
    '''
    Compress a given folder given its full path (folder_path) to a desired path (zip_path).
    
    param folder_path (str): full path of the folder to compress.
    param zip_path (str): full path of where to save the zip file.
    '''
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, folder_path))
