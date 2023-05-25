import zipfile
import os
from sklearn.metrics import mean_squared_error
import numpy as np

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
                
                
def are_signals_similar(series1, series2, threshold = None):
    '''
    Compare two timeseries using MSE given as threshold
    
    param series1 (array): inh or exb timeseries i.e result of a TVB simulation
    param series2 (array): inh or exb timeseries i.e result of a TVB simulation
    threshold (int): if set to None, this function will only print MSE result.
    This helps to have a range of value to set the threshold
    '''
    mse = mean_squared_error(series1, series2)
    if threshold is not None:
        if np.sqrt(mse) <= threshold:
            return 1
        else:
            return 0
    else:
        print("MSE:", np.sqrt(mse))    
        
def find_max_value(timeseries1, timeseries2):
    # Combine the two time series
    combined_series = timeseries1 + timeseries2
    # Find the maximum value
    max_value = max(combined_series)
    return max_value
        