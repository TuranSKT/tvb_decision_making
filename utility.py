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
                
                
def classify_signal(signal, threshold = 80):
    '''
    Binary classifier of a signal given a threshold. 
    
    param signal (matrix): the timeserie signal (exc or inh) 
    param threhold (int): threshold from which the signal is considered coming 
    from the strong audio stimulus i.e. with the higher stimval
    '''
    if any(value > threshold for value in signal):
        print('probably strong audio stimulus (stimval=2)')
    else:
        print('probably weak audio stimulus (stimval=1e-3)')