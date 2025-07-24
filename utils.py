import os
import json

def extract_lepton_number(state_path):
    """
    Extracts the initial L/n_gamma from the first data line in state.dat.
    This corresponds to the value at the highest temperature (early universe).
    """
    with open(state_path, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("!"):
                values = line.split()
                if len(values) >= 4:
                    return float(values[3])  # L/n_gamma is 4th column
                else:
                    raise ValueError("First data line has fewer than 4 columns.")
    raise ValueError("No valid data lines found in state.dat.")


def write_summary(output_dir, mass_keV, mixing_angle, lepton_number, thermal_mass, dm_density):
    result = {
        "mass_keV": mass_keV,
        "mixing_angle": mixing_angle,
        "lepton_asymmetry": lepton_number,
        "thermal_mass": thermal_mass if thermal_mass is not None else "SKIPPED",
        "dm_density": dm_density
    }

    summary_path = os.path.join(output_dir, "results.json")
    with open(summary_path, "w") as f:
        json.dump(result, f, indent=4)

    make_summary_page(output_dir, result)

import os

def make_summary_page(output_dir, result):
    """Create a basic HTML summary page for visualization."""
    print(f"Generating summary page for: {output_dir}")
    plots_dir = os.path.join(output_dir, "plots")
    os.makedirs(plots_dir, exist_ok=True)

    html_path = os.path.join(output_dir, "summary.html")
    with open(html_path, "w") as f:
        f.write("<html><body><h2>Run Summary</h2>\n")

        # Basic parameters
        f.write(f"<p><b>Mass (keV):</b> {result['mass_keV']:.2e}</p>\n")
        f.write(f"<p><b>Mixing Angle:</b> {result['mixing_angle']:.1e}</p>\n")
        f.write(f"<p><b>Lepton Asymmetry:</b> {result['lepton_asymmetry']:.2e}</p>\n")
        f.write(f"<p><b>DM Density:</b> {result['dm_density']:.3f}</p>\n")

        # Thermal mass (optional)
        if result.get("thermal_mass") == "SKIPPED":
            f.write("<p><b>Thermal Mass:</b> <i>Skipped (Overproduction)</i></p>\n")
        else:
            f.write(f"<p><b>Thermal Mass:</b> {result['thermal_mass']:.2f}</p>\n")

        # Plots
        f.write("<h3>Plots</h3>\n")
        if os.path.exists(os.path.join(plots_dir, "psd_plot.png")):
            f.write("<img src='plots/psd_plot.png' width='400'>\n")
        if os.path.exists(os.path.join(plots_dir, "transfer_fit.png")):
            f.write("<img src='plots/transfer_fit.png' width='400'>\n")

        f.write("</body></html>\n")


def extract_final_dm_density(state_path):
    """
    Extracts final Omega_wdm h^2 value from last data line of state.dat.
    """
    with open(state_path, "r") as f:
        lines = [line for line in f if line.strip() and not line.startswith("!")]
    if not lines:
        raise ValueError("No data lines found in state.dat.")
    values = lines[-1].split()
    if len(values) >= 5:
        return float(values[4])  # Final DM density is 5th column
    raise ValueError("Final line has fewer than 5 columns.")




# Optional: helper for safe numeric parsing (not currently used)
def safe_float(val):
    try:
        return float(val)
    except ValueError:
        return None
