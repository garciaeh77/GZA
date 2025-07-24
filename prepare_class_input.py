import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy.ndimage import gaussian_filter1d
from config import save_plots, P_k_max_h_Mpc

def modify_psd(input_file, output_dir, T_ref=10.0):
    """Prepares a CLASS-compatible PSD file from sterile-dm output."""
    raw_data = np.loadtxt(input_file, comments="#")[:, :2]
    raw_data[:, 0] /= T_ref  # Convert p to q = p / T

    raw_data = raw_data[~np.isnan(raw_data).any(axis=1)]
    raw_data = raw_data[raw_data[:, 1] > 0]

    if len(raw_data) < 20:
        raise ValueError("Too few valid PSD points")

    raw_data = raw_data[np.argsort(raw_data[:, 0])]

    q_min = max(raw_data[0, 0], 1e-3)
    q_max = min(raw_data[-1, 0], 50)
    q_vals = np.logspace(np.log10(q_min), np.log10(q_max), 200)

    interp_fn = interp1d(raw_data[:, 0], raw_data[:, 1], bounds_error=False, fill_value=0.0)
    f_vals = interp_fn(q_vals)
    f_vals = gaussian_filter1d(f_vals, sigma=0.5)

    f_vals = np.clip(f_vals, 1e-20, 1e2)

    if np.trapz(f_vals, q_vals) < 1e-10:
        raise ValueError("PSD integral too small, likely nonphysical")

    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, "Snapshot100_modified.dat")
    np.savetxt(out_path, np.column_stack([q_vals, f_vals]), fmt="%13.7e  %13.7e")

    if save_plots:
        plot_dir = os.path.join(output_dir, "../plots")
        os.makedirs(plot_dir, exist_ok=True)

        plt.plot(q_vals, q_vals**2 * f_vals)
        plt.xlabel("q = p/T")
        plt.ylabel(r"$q^2 f(q)$")
        plt.title("Modified and Smoothed PSD")
        plt.savefig(os.path.join(plot_dir, "psd_plot.png"))
        plt.close()


    return out_path

def generate_class_ini(psd_path, sterile_mass_keV, mixing_angle, output_dir):
    """Generates a CLASS .ini file for a sterile neutrino with a given PSD."""
    os.makedirs(output_dir, exist_ok=True)
    ini_path = os.path.join(output_dir, "class.ini")
    root_tag = f"ms{sterile_mass_keV:.3e}_s2{mixing_angle:.3e}"
    class_psd_filename = os.path.basename(psd_path)

    with open(ini_path, "w") as f:
        f.write(f"""# CLASS input for sterile neutrino
output = tCl,pCl,lCl,mPk
evolver = 0
modes = s
ic = ad
gauge = synchronous

h = 0.67360
T_cmb = 2.72548
omega_b = 0.022369232127999995
omega_cdm = 0.0
Omega_k = 0.
N_ur = 2.0308
N_ncdm = 2
use_ncdm_psd_files = 1,1
ncdm_psd_filenames = psd_FD_single.dat,{class_psd_filename}
m_ncdm = 0.06,{sterile_mass_keV * 1e3:.1f}
omega_ncdm = 0,0.12
T_ncdm = 0.71611,0.71611
ksi_ncdm = 0,0
deg_ncdm = 1.0,1.0
ncdm_quadrature_strategy = 0,0
ncdm_maximum_q = 12.,12.
ncdm_N_momentum_bins = 150,150
ncdm_fluid_approximation = 3,3

tol_ncdm = 1e-3
tol_ncdm_bg = 1e-3

recombination = HyRec
YHe = BBN
reio_parametrization = reio_camb
z_reio = 7.6711

Pk_ini_type = analytic_Pk
k_pivot = 0.05
A_s = 2.100549e-09
n_s = 0.9660499
alpha_s = 0.
l_max_scalars = 2500
P_k_max_h/Mpc = {P_k_max_h_Mpc}
z_pk = 0
lensing = yes

overwrite_root = no
headers = yes
format = class
write_background = y
write_parameters = yes
write_warnings = no

input_verbose = 1
output_verbose = 1

root = output/{root_tag}_
""")

    return ini_path
