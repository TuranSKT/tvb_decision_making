import os
import numpy as np
from utility import toZip 
import shutil
from tvb_model_reference.view.plot_macaque import prepare_surface_regions_macaque
from tvb_model_reference.simulation_file.parameter.parameter_macaque import Parameter

class Connectome:
    def __init__(self, conn_path, 
                 con_name = 'Connectivity.zip', 
                 surf_name = 'surface_147k.zip', 
                 regmap_name = 'regionMapping_147k_84.txt'):
        '''
        Basic tools to edit the Macaque Connectome.
        
        param conn_path (str): Full path to the Connectivity folder.
                
        param con_name (str): file_name of the connectivity .zip file.
        param surf_name (str): file_name of the surface .zip file.
        param regmap_name (str): file_name of the region mapping .txt file.
        '''
        self.weights = np.loadtxt(conn_path + 'weights.txt')
        self.tract_lengths = np.loadtxt(conn_path + 'tract_lengths.txt')
        self.centers = np.genfromtxt(conn_path + 'centres.txt', dtype=None, encoding=None)
        
        self.conn_path = conn_path
        
        self.cortex, self.conn, self.hemispheres_left, self.hemispheres_right =\
        prepare_surface_regions_macaque(Parameter(), 
                                        conn_filename = con_name, 
                                        zip_filename = surf_name, 
                                        region_map_filename = regmap_name)
    
    
    
    def get_features(self):
        '''
        Return Connectivity's features.
        '''
        return self.weights, self.tract_lengths, self.centers
    
    def get_connectivity(self):
        '''
        Return in TVB in-built connectivity object.
        '''
        return self.conn
    
    
    def id_finder(self, region_names):
        '''
        Return a list of region_ids (int) given their names.

        param region_names (List[str]): list of names of the regions of interest.
        '''
        return [i for i, item in enumerate(self.centers) if item[0] in region_names]
        

    def region_name_finder(self, region_ids):
        '''
        Return a list of region_names (str) given their ids.

        param region_ids (List[int]): list of ids of the regions of interest.
        '''
        return [self.centers[i][0] for i in region_ids]

    
    def duplicate_region(self, region_name):
        '''
        Duplicate column and row where a given area occurs.
        Weight are divided/2 to ensure cohesion of the connectivity matrix.
        
        param region_name (str): region's name on which to perform duplication.
        '''
        region_index = self.id_finder([region_name])[0]

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
        self.centers[region_index][0] = f'{region_name}a'
        self.centers[region_index + 1][0] = f'{region_name}b'
        
    def set_weight(self, region_name1, region_name2, weight_val):
        '''
        Target intersection of two regions in the connectome and modifity its weight.
        
        param region_name1 (str)
        param region_name2 (str)
        param weight_val (int)
        '''
        region_index = self.id_finder([region_name1, region_name2])
        self.weights[region_index[0], region_index[1]] = weight_val
        
    def save_changes(self, new_conn_path, delete_temp_folder = False):
        '''
        Save changes in the dedicated new_conn_path and compress it into a .zip file.
        
        param delete_temp_folder (bool): True to delete the temporary created conn folder.
        param new_conn_path (str): Full path to the New Connectivity folder that will be saved after changes.
        '''
        # Create the new folder
        os.makedirs(new_conn_path, exist_ok=True)

        # Save edited files
        np.savetxt(new_conn_path + 'weights.txt', self.weights)
        np.savetxt(new_conn_path + 'tract_lengths.txt', self.tract_lengths)
        np.savetxt(new_conn_path + 'centres.txt', self.centers, fmt='%s')

        # Compress the new folder into a zip file
        zip_path = new_conn_path[:-1] + '.zip' if new_conn_path.endswith('/') else new_conn_path + '.zip'
        toZip(new_conn_path, zip_path)
            
        if delete_temp_folder: # Delete tmp created folder
            shutil.rmtree(new_conn_path)
