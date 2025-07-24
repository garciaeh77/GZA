import os
import json
from config import mass_grid, theta_grid, sterile_dm_path, class_path, lcdm_reference_path, base_output_dir
from run_production import run_sterile_dm, OverproductionError  # 🔁
from prepare_class_input import modify_psd, generate_class_ini
from run_class import run_class
from postprocess import extract_transfer_function, fit_thermal_mass
from utils import extract_lepton_number, write_summary, extract_final_dm_density

def should_skip_step(output_dir, step):
    if step == "sterile":
        return os.path.exists(os.path.join(output_dir, "sterile_dm", "Snapshot100.dat"))
    elif step == "class":
        return os.path.exists(os.path.join(output_dir, "class_output", "pk.dat"))
    elif step == "postprocess":
        return os.path.exists(os.path.join(output_dir, "results.json"))
    return False

def run_pipeline_for_point(mass_keV, theta):
    tag = f"m_{mass_keV:.1e}_theta_{theta:.1e}"
    base_dir = os.path.join(base_output_dir, tag)
    os.makedirs(base_dir, exist_ok=True)

    # === 1. Sterile-DM ===
    if not should_skip_step(base_dir, "sterile"):
        try:
            print(f"[{tag}] Running sterile-dm...")
            run_sterile_dm(mass_keV, theta, base_dir, sterile_dm_path)
        except OverproductionError as e:  # 🔁
            print(f"[{tag}] Overproduction detected during sterile-dm: {e}")  # 🔁
            write_summary(base_dir, mass_keV, theta, L=None, t=None, omega_dm=float(str(e).split("=")[-1].split()[0]), status="OVERPRODUCED")  # 🔁
            return  # 🔁
        except Exception as e:
            print(f"[{tag}] Error in sterile-dm: {e}")
            log_error(base_dir, "sterile", e)
            return
    else:
        print(f"[{tag}] Skipping sterile-dm.")

    # === 2. Check for Overproduction ===
    state_path = os.path.join(base_dir, "sterile_dm", "state.dat")
    try:
        L = extract_lepton_number(state_path)
        omega_dm = extract_final_dm_density(state_path)
        if omega_dm > 0.125:
            print(f"[{tag}] Overproduction detected (Ω h^2 = {omega_dm:.5f} > 0.125). Skipping CLASS and postprocessing.")
            write_summary(base_dir, mass_keV, theta, L, "SKIPPED", omega_dm)
            return
    except Exception as e:
        print(f"[{tag}] Error while checking DM density: {e}")
        log_error(base_dir, "sterile", e)
        return

    # === 3. CLASS ===
    if not should_skip_step(base_dir, "class"):
        try:
            print(f"[{tag}] Preparing and running CLASS...")
            sterile_psd = os.path.join(base_dir, "sterile_dm", "Snapshot100.dat")
            class_input_dir = os.path.join(base_dir, "class_input")
            class_output_dir = os.path.join(base_dir, "class_output")

            modified_psd = modify_psd(sterile_psd, class_input_dir)
            ini_path = generate_class_ini(modified_psd, mass_keV, theta, class_input_dir)
            run_class(ini_path, class_output_dir, class_exec="./class")
        except Exception as e:
            print(f"[{tag}] Error in CLASS: {e}")
            log_error(base_dir, "class", e)
            return
    else:
        print(f"[{tag}] Skipping CLASS.")

    # === 4. Postprocess ===
    if not should_skip_step(base_dir, "postprocess"):
        try:
            print(f"[{tag}] Postprocessing results...")
            pk_path = os.path.join(base_dir, "class_output", "pk.dat")
            k, T = extract_transfer_function(pk_path, lcdm_reference_path)
            t_fit = fit_thermal_mass(k, T, output_dir=base_dir)

            L = extract_lepton_number(state_path)
            write_summary(base_dir, mass_keV, theta, L, t_fit, omega_dm)

        except Exception as e:
            print(f"[{tag}] Error in postprocessing: {e}")
            log_error(base_dir, "postprocess", e)
    else:
        print(f"[{tag}] Skipping postprocessing.")

def log_error(base_dir, step, exception):
    log_path = os.path.join(base_dir, "error.log")
    with open(log_path, "a") as log:
        log.write(f"[{step}] {type(exception).__name__}: {str(exception)}\n")

# For multiprocessing use
process_grid_point = run_pipeline_for_point

def main():
    for mass in mass_grid:
        for theta in theta_grid:
            try:
                run_pipeline_for_point(mass, theta)
            except Exception as e:
                tag = f"m_{mass:.1e}_theta_{theta:.1e}"
                print(f"[{tag}] ❌ Error: {e}")
                err_dir = os.path.join(base_output_dir, tag)
                os.makedirs(err_dir, exist_ok=True)
                with open(os.path.join(err_dir, "error.log"), "a") as log:
                    log.write(str(e) + "\n")
                with open(os.path.join(err_dir, ".fail"), "w") as f:
                    f.write("FAILED\n")

if __name__ == "__main__":
    main()
