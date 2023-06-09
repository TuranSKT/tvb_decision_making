import tvb_model_reference.src.tools_simulation as tools
import matplotlib.pyplot as plt
import numpy as np
from tvb_model_reference.simulation_file.parameter.parameter_macaque import Parameter
parameters = Parameter()
import time 
from utility import find_max_value
import pdb

class Simulation:
    def __init__(self, root_folder, sim_name, connectome_instance, rois_stim_values, 
                 isIntNoise = True, isWeightNoise = True):
        '''
        This is a custom simulation class that helps to minimise the amount of code in the main ipynb file when
        running multiple simulation with different parameters. 
        This simulation loops through different stim_values and also has built-in plot functions.
        
        param root_folder (str): Relative path of the result folder.
        param sim_name (str): name of the simulation. Needed for saving the result.
        param connectome_instance (SurfacePreparer Obj): instance of the SurfacePreparer class.
        param rois_stim_values (dict): dictionary with regions of interest as keys and lists of stim values as values.
        param isIntNoise (bool): False to disable integrator noise which is 
        'nsig':[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0] by default.
        param isWeightNoise (bool) : False to disable weight noise in the model. Default: 1e-4
        '''
        # Prepare surface plot:
        self.root_folder = root_folder
        self.connectome_instance = connectome_instance
        self.conn = self.connectome_instance.get_connectivity()
        
        # Set the parameters of the simulation
        self.run_sim = 15000.0 # ms, length of the simulation default:5000.0
        self.cut_transient = 2000.0 # ms, length of the discarded initial segment; default:2000.0
        self.Iext = 0.000315 # External input
        self.isIntNoise = isIntNoise
        self.isWeightNoise = isWeightNoise 
     
        # Set the parameters of the stimulus (choose stimval = 0 to simulate spontaneous activity)
        self.stimdur = 4000 # Duration of the stimulus [ms] default:50
        self.stimtime_mean = 2500. # Time after simulation start (it will be shuffled) [ms] default:2500
        self.bval = [5] # list of b_values which are frequency adaptation parameter.
        self.sim_name = sim_name
        self.interstim_T = [1e9] # Interstimulus interval [ms] to ensure that only one stimulus is simulated.
        self.rois_stim_values = rois_stim_values  # Dictionary with format {roi_key: [stim_values]}
        self.ROIs = list(self.rois_stim_values.keys())
        self.ROIsId = self.connectome_instance.id_finder(self.ROIs)
        
        # Init plot variables
        self.ylim = 100
        self.FR_exc, self.FR_inh, self.Ad_exc, self.time_s = [], [], [], []

        # Init default simulator
        self.simulator = tools.init(parameters.parameter_simulation,
                                    parameters.parameter_model,
                                    parameters.parameter_connection_between_region,
                                    parameters.parameter_coupling,
                                    parameters.parameter_integrator,
                                    parameters.parameter_monitor)

    
    def get_inh_signals_from_region(self, target_region_name):
        '''
        Get all inh signals from a targetted area and map them in a dict according to the stimval used.

        param target_region_name (str): area's name from where to get signals.
        '''
        target_region_id = self.connectome_instance.id_finder(target_region_name)[0]
        time_series_dict = {}
        for index, stim_val in [(i, v) for sv in self.rois_stim_values.values() for i, v in enumerate(sv)]:
            time_series_dict[stim_val] = self.FR_inh[index][:, target_region_id]
        return time_series_dict


    def update_simulator_param(self, stim_param):
        '''
        Re-update the default simulator
        
        param stim_param (parameter_stimulus object)
        '''
        return tools.init(parameters.parameter_simulation,
                          parameters.parameter_model,
                          parameters.parameter_connection_between_region,
                          parameters.parameter_coupling,
                          parameters.parameter_integrator,
                          parameters.parameter_monitor,
                          parameter_stimulation = stim_param)

  
    def single_simulation(self, stim_val_roi_dict, sim_number):
        '''
        Run a single simulation for a stim_val.

        param stim_val_roi_dict (dict): dictionary with region keys and stimulus strength values.
        param sim_number (int): simulation number. Needed for records.
        '''
        parameters.parameter_model['b_e'] = self.bval
        parameters.parameter_model['external_input_ex_ex'] = self.Iext
        parameters.parameter_model['external_input_in_ex'] = self.Iext
        if not self.isIntNoise:
            parameters.parameter_integrator['noise_parameter'] = {'nsig':[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                                                                  'ntau':0.0,
                                                                  'dt': 0.1}
        if not self.isWeightNoise:
            parameters.parameter_model['weight_noise'] = 0

        parameters.parameter_stimulus["tau"] = self.stimdur # Stimulus duration [ms]
        parameters.parameter_stimulus["T"] = self.interstim_T # Interstimulus interval [ms]
        parameters.parameter_stimulus["variables"] = [0] # Variable to kick

        weight = list(np.zeros(self.simulator.number_of_nodes))
        for roi in self.ROIs:
            roi_id = self.connectome_instance.id_finder(roi)[0]
            weight[roi_id] = stim_val_roi_dict[roi] # Region and stimulation strength of the region

        parameters.parameter_stimulus["weights"] =  weight

        parameters.parameter_stimulus['onset'] = self.cut_transient + 0.5 * (self.run_sim-self.cut_transient)
        stim_time = parameters.parameter_stimulus['onset']
        stim_steps = stim_time * 10 # Number of steps until stimulus

        parameters.parameter_simulation['path_result'] = (f'{self.root_folder}/{self.sim_name}_{sim_number}')
        # Update simulation with previously defined parameters and modifications
        self.simulator = self.update_simulator_param(parameters.parameter_stimulus)

        tools.run_simulation(self.simulator,
                             self.run_sim,                            
                             parameters.parameter_simulation,
                             parameters.parameter_monitor)


    def main_simulation_loop(self):
        '''
        Main simulation loop in which single_simulation() will be looped through stimvals.
        '''
#         print(f"Stimulus duration: {parameters.parameter_stimulus['tau']}ms \n" +
#               f"Adaptation parameter (b): {self.bval[0]}\n" + 
#               f"Interstimulus duration: {self.interstim_T[0]}mS\n" +
#               "*" * 38)    
        
        start_time = time.time()
        
        for sim_number, stim_val_dict in enumerate(zip(*self.rois_stim_values.values())): 
            stim_val_roi_dict = dict(zip(self.rois_stim_values.keys(), stim_val_dict))
            print("|" * 38)
            print(f"SimNb: {sim_number}\n" +
                  f"ROI/Stimval: {stim_val_roi_dict}")
            self.single_simulation(stim_val_roi_dict, sim_number)

        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Simulation took {elapsed_time:.2f} seconds to complete.")
        
        
    def load_simulation(self):
        '''
        Load a previously done simulation. Needed to plot the result.
        '''
        # Load simulation variables:      
        for i in range(len(next(iter(self.rois_stim_values.values())))):
                result = tools.get_result(f"{self.root_folder}/{self.sim_name}_{i}", self.cut_transient, self.run_sim)[0]
                self.time_s = result[0] * 1e-3 # From ms to sec
                self.FR_exc.append(result[1][:,0,:] * 1e3) # From KHz to Hz; Excitatory firing rate
                self.FR_inh.append(result[1][:,1,:] * 1e3) # From KHz to Hz; Inhibitory firing rate
                self.Ad_exc.append(result[1][:,5,:]) # Excitatory adaptation [nA]  

                
    def plot_simulation(self, target_region_name):
        '''
        Plot the result of the simulation on a targeted area.

        param target_region_name (str): Name of the target area to plot.
        '''
        total_sim_nb = len(next(iter(self.rois_stim_values.values())))
        fig, axes = plt.subplots(nrows=total_sim_nb, ncols=2, figsize=(16, 8))
        if total_sim_nb == 1:
            axes = np.array([axes])
        plt.rcParams.update({'font.size': 14})
        target_region_id = self.connectome_instance.id_finder(target_region_name)[0]

        for sim_nb, stim_val in enumerate(zip(*self.rois_stim_values.values())): 
            ax_fr, ax_ad = axes[sim_nb, 0], axes[sim_nb, 1]

            # Firing rate plot
            inh_signal = self.FR_inh[sim_nb][:, target_region_id]
            exc_signal = self.FR_exc[sim_nb][:, target_region_id]
            ax_fr.plot(self.time_s, inh_signal, color='darkred')
            ax_fr.plot(self.time_s, exc_signal, color='SteelBlue')
            ax_fr.set_xlabel('Time (s)')
            ax_fr.set_ylabel('Firing rate (Hz)')
            ax_fr.set_title(f'From {target_region_name[0]} with stim strength of {stim_val} in {", ".join(self.ROIs)}')
            self.ylim = max(np.max(inh_signal), np.max(exc_signal))
            ax_fr.set_ylim([0, self.ylim + 40])
            ax_fr.legend(['Inh.', 'Exc.'], loc='best')

            # Adaptation plot
            ax_ad.plot(self.time_s, self.Ad_exc[sim_nb][:, target_region_id], color='goldenrod')
            ax_ad.set_xlabel('Time (s)')
            ax_ad.set_ylabel('Adaptation (nA)')

            for ax in [ax_fr, ax_ad]:
                ax.set_xlim([3, self.run_sim/1000])
                ax.set_xticks(np.arange(3, self.run_sim/1000+0.5, 0.5))

        plt.tight_layout()
        plt.show()