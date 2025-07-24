import os
import numpy as np
from scipy.interpolate import interp1d
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from config import save_plots

# Parameters for transfer function fitting (from Vogel et al. 2022)
a, b, v = 0.0437, -1.188, 1.049

def load_power_spectrum(path):
    """
    Load power spectrum data from a CLASS output file, skipping comment lines.
    Returns only the first two columns (k and P(k)).
    """
    try:
        data = np.loadtxt(path, comments="#")
        if data.shape[1] < 2:
            raise ValueError(f"{path} does not contain two columns.")
        return data[:, 0], data[:, 1]
    except Exception as e:
        print(f"Error loading {path}: {e}")
        raise

def extract_transfer_function(test_path, lcdm_path):
    """
    Compute T(k) = sqrt(P_test(k) / P_LCDM(k)) using interpolation on a shared k-grid.
    Filters out invalid values (NaNs, infs, negatives).
    """
    k_test, P_test = load_power_spectrum(test_path)
    k_lcdm, P_lcdm = load_power_spectrum(lcdm_path)

    k_common = np.unique(np.concatenate((k_test, k_lcdm)))
    P_test_interp = interp1d(k_test, P_test, bounds_error=False, fill_value="extrapolate")
    P_lcdm_interp = interp1d(k_lcdm, P_lcdm, bounds_error=False, fill_value="extrapolate")

    P_test_vals = P_test_interp(k_common)
    P_lcdm_vals = P_lcdm_interp(k_common)

    # Clip negative P_test values
    P_test_vals = np.clip(P_test_vals, a_min=0, a_max=None)

    # Avoid divide-by-zero and bad sqrt
    with np.errstate(divide='ignore', invalid='ignore'):
        ratio = P_test_vals / P_lcdm_vals
        valid = np.isfinite(ratio) & (ratio > 0)

    if not np.any(valid):
        raise ValueError("All transfer function points are invalid. Nothing to fit.")

    if np.sum(~valid) > 0:
        print(f"[extract_transfer_function] Warning: Skipped {np.sum(~valid)} bad T(k) points")

    T_k = np.sqrt(ratio[valid])
    return k_common[valid], T_k



def _fit_model(k, t):
    """
    Parametric form of the transfer function model T(k, t).
    """
    return (1 + (a * k * t**b)**(2*v))**(-5/v)

def fit_thermal_mass(k, T, output_dir=None):
    """
    Fit T(k) to extract the thermal mass parameter t.
    Optionally saves a plot in output_dir if save_plots is True.
    """
    popt, _ = curve_fit(_fit_model, k, T, p0=[1.0])
    t_fit = popt[0]

    if save_plots and output_dir:
        plot_dir = os.path.join(output_dir, "plots")
        os.makedirs(plot_dir, exist_ok=True)
        plt.figure()
        plt.scatter(k, T, s=10, label="T(k)")
        plt.plot(k, _fit_model(k, t_fit), 'r--', label=f"Fit t={t_fit:.2f}")
        plt.xscale('log')
        plt.xlabel("k [h/Mpc]")
        plt.ylabel("Relative Transfer T(k)")
        plt.title("Transfer Function Fit")
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(plot_dir, "transfer_fit.png"))
        plt.close()

    return t_fit
