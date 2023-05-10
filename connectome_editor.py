import os
import numpy as np
from utility import toZip 

class ConnectomeEditor:
    
    def __init__(self, surface_instance, conn_path, new_conn_path):
        '''
        Basic tools to edit the Macaque Connectome.
        
        param surface_instance (SurfacePreparer Obj): instance of the SurfacePreparer class.
        param conn_path (str): Full path to the Connectivity folder.
        param conn_path (str): Full path to the New Connectivity folder that will be saved after changes.
        '''
        self.weights = np.loadtxt(conn_path + 'weights.txt')
        self.tract_lengths = np.loadtxt(conn_path + 'tract_lengths.txt')
        self.centers = np.genfromtxt(conn_path + 'centres.txt', dtype=None, encoding=None)
        self.surface_instance = surface_instance
        self.conn_path = conn_path
        self.new_conn_path = new_conn_path
    
    def get_features(self):
        '''
        Return Connectivity's features.
        '''
        return self.weights, self.tract_lengths, self.centers
    
    
    def duplicate_region(self, region_index):
        '''
        Duplicate column and row where a given area occurs.
        Weight are divided/2 to ensure cohesion of the connectivity matrix.
        
        param region_idx (int): region's index on which to perform duplication.
        '''
        # Reduce dedicated weights by 2 
        self.weights[region_index, :] /= 2
        self.weights[:, region_index] /= 2
        
        # Duplicate column/row where region_idx occurs
        self.weights = np.insert(self.weights, region_index, self.weights[region_index], axis=0)
        self.weights = np.insert(self.weights, region_index, self.weights[:, region_index], axis=1)
        self.tract_lengths = np.insert(self.tract_lengths, region_index, self.tract_lengths[region_index], axis=0)
        self.tract_lengths = np.insert(self.tract_lengths, region_index, self.tract_lengths[:, region_index], axis=1)
        self.centers = np.insert(self.centers, region_index, self.centers[region_index], axis=0)

        # Rename <region_name> to <region_name_a> and <region_name_b> in the Connectome
        self.centers[region_index][0] = f'{self.surface_instance.region_name_finder(region_index)}a'
        self.centers[region_index + 1][0] = f'{self.surface_instance.region_name_finder(region_index)}b'
        
    def save_changes(self):
        '''
        Save changes in the dedicated new_conn_path and compress it into a .zip file.
        '''
        # Create the new folder
        os.makedirs(self.new_conn_path, exist_ok=True)

        # Save edited files
        np.savetxt(self.new_conn_path + 'new_weights.txt', self.weights)
        np.savetxt(self.new_conn_path + 'new_tract_lengths.txt', self.tract_lengths)
        np.savetxt(self.new_conn_path + 'new_centers.txt', self.centers, fmt='%s')

        # Compress the new folder into a zip file
        zip_path = self.new_conn_path[:-1] + '.zip' if self.new_conn_path.endswith('/') else self.new_conn_path + '.zip'
        toZip(self.new_conn_path, zip_path)
