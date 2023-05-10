import numpy as np
from tvb_model_reference.view.plot_macaque import prepare_surface_regions_macaque
from tvb_model_reference.simulation_file.parameter.parameter_macaque import Parameter

class SurfacePreparer:
    def __init__(self, root_folder, con_name = 'Connectivity.zip', 
                 surf_name = 'surface_147k.zip', 
                 regmap_name = 'regionMapping_147k_84.txt'):
        '''
        Prepare the surface regions of the Macaque.
        
        param root_folder (str): Relative path of the result folder.
        param con_name (str): file_name of the connectivity .zip file
        param surf_name (str): file_name of the surface .zip file
        param regmap_name (str): file_name of the region mapping .txt file
        '''
        self.root_folder = root_folder
        self.cortex, self.conn, self.hemispheres_left, self.hemispheres_right =\
        prepare_surface_regions_macaque(Parameter(), 
                                        conn_filename = con_name, 
                                        zip_filename = surf_name, 
                                        region_map_filename = regmap_name)
            
    def get_features(self):
        return self.cortex, self.conn, self.hemispheres_left, self.hemispheres_right 

    
    def id_finder(self, region_name):
        '''
        Return region_id (int) given its name.
        
        param region_name (str): name of the region of interest.
        '''
        return np.where(self.conn.region_labels == f'{region_name}')[0][0]
    
    
    def region_name_finder(self, region_id):
        '''
        Return region_name (str) given its id.
        
        param region_id (int): id of the region of interest.
        '''
        return self.conn.region_labels[region_id]
