import numpy as np 

#can do single points or arrays. Delete sample poin output or change below values to test install
mass_grid = [44.0] 
theta_grid = [5e-15] 
  

sterile_dm_path = "/Users/temp/physcode/sterile-dm" #reference README for install
class_path = "/Users/temp/physcode/class_public" #reference README for install

base_output_dir = "outputs" #change for separate data storage
lcdm_reference_path = "LCDM.dat" #Generate from CLASS using your preferred cosmology (pk.dat)
P_k_max_h_Mpc = 100.0 #increase for larger particle masses
save_plots = True
summary_page = True
