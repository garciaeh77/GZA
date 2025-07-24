import subprocess, shutil, time, os, glob, re
from math import isclose
class OverproductionError(Exception):
    """Raised when sterile-dm overproduces sterile neutrino density."""
    pass


def parse_outfile_dirname(name):
    """Extract ms and s2 from output directory name like ms2.000E-02s21.000E-10L..."""
    match = re.match(r"ms([\d.E+-]+)s2([\d.E+-]+)L.*", name)
    if match:
        try:
            return float(match.group(1)), float(match.group(2))
        except ValueError as e:
            raise ValueError(f"Failed to parse float from dirname: {name}") from e
    return None, None

def run_sterile_dm(mass, theta, output_dir, exe_path):
    os.makedirs(os.path.join(output_dir, "sterile_dm"), exist_ok=True)

    orig_params = os.path.join(exe_path, "params.ini")
    backup_params = os.path.join(exe_path, "params_backup.ini")
    temp_params = os.path.join(output_dir, "sterile_dm", "params.ini")
    temp_params_abs = os.path.abspath(temp_params)

    if not os.path.exists(backup_params):
        shutil.copy(orig_params, backup_params)

    mass_MeV = mass / 1e3
    with open(backup_params, "r") as f:
        lines = f.readlines()

    with open(temp_params, "w", newline="\n") as f:
        for line in lines:
            if line.strip().startswith("ms ="):
                f.write(f"ms = {mass_MeV:.6E}\n")
            elif line.strip().startswith("s2 ="):
                f.write(f"s2 = {theta:.6E}\n")
            else:
                f.write(line)

    # Allow process to finish even if exit code ≠ 0
    result = subprocess.run(
        ["./sterile-nu", temp_params_abs],
        cwd=exe_path,
        capture_output=True,
        text=True,
        check=False,
        timeout=1800
    )
    time.sleep(1)

    stdout = result.stdout + result.stderr
    match = re.search(r"Omega_wdm h\^2=\s+([\d.Ee+-]+)", stdout)
    if match:
        omega = float(match.group(1))
        if omega > 0.125:
            raise OverproductionError(f"Omega_wdm h^2 = {omega:.2e} (overproduction)")

    # If not overproduced, but sterile-dm failed, raise error
    if result.returncode != 0:
        raise subprocess.CalledProcessError(result.returncode, result.args, output=result.stdout, stderr=result.stderr)

    candidates = glob.glob(os.path.join(exe_path, "outfiles", "ms*s2*L*"))
    if not candidates:
        raise RuntimeError("sterile-dm completed but no output folder found.")

    actual_output = None
    for path in candidates:
        dirname = os.path.basename(path)
        ms_val, s2_val = parse_outfile_dirname(dirname)
        if ms_val is None:
            continue

        mass_tol = 0.01 / 1000.0
        mixing_tol = 0.01

        if abs(ms_val - mass_MeV) <= mass_tol and abs(s2_val - theta) / theta <= mixing_tol:
            actual_output = path
            break

    if actual_output is None:
        raise FileNotFoundError(f"No matching output: mass={mass:.3f} keV, s2={theta:.2e}")

    for file in ["Snapshot100.dat", "state.dat"]:
        src = os.path.join(actual_output, file)
        dst = os.path.join(output_dir, "sterile_dm", file)
        shutil.copy(src, dst)
