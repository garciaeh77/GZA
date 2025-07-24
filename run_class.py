import os
import shutil
import subprocess
from config import class_path

CLASS_WORKDIR = class_path
CLASS_EXECUTABLE = "./class"

def extract_psd_path_from_ini(ini_path):
    """Returns the full path to the Snapshot100_modified.dat referenced in the .ini file."""
    with open(ini_path, "r") as f:
        for line in f:
            if "Snapshot100_modified.dat" in line:
                return os.path.join(os.path.dirname(ini_path), "Snapshot100_modified.dat")
    raise FileNotFoundError("Could not find PSD filename in .ini file.")

def run_class(ini_file, output_dir, class_exec):
    """
    Runs CLASS from its working directory.
    Copies PSD and .ini file into CLASS_WORKDIR, runs CLASS, then moves the output pk.dat back to output_dir.
    """
    os.makedirs(output_dir, exist_ok=True)

    psd_path = extract_psd_path_from_ini(ini_file)
    psd_basename = "Snapshot100_modified.dat"
    ini_basename = "class.ini"

    psd_target = os.path.join(CLASS_WORKDIR, psd_basename)
    ini_target = os.path.join(CLASS_WORKDIR, ini_basename)

    class_output_dir = os.path.join(CLASS_WORKDIR, "output")

    try:
        # === Step 0: Clean existing CLASS output directory ===
        if os.path.exists(class_output_dir):
            for f in os.listdir(class_output_dir):
                os.remove(os.path.join(class_output_dir, f))

        # === Step 1: Copy inputs ===
        shutil.copy(psd_path, psd_target)
        shutil.copy(ini_file, ini_target)

        # === Step 2: Run CLASS ===
        subprocess.run([CLASS_EXECUTABLE, ini_basename], cwd=CLASS_WORKDIR, check=True)

        # === Step 3: Find and move *_pk.dat to pipeline output ===
        found_pk = False
        for fname in os.listdir(class_output_dir):
            if fname.endswith("_pk.dat"):
                shutil.move(os.path.join(class_output_dir, fname), os.path.join(output_dir, "pk.dat"))
                found_pk = True
                break

        if not found_pk:
            raise FileNotFoundError("CLASS run completed but pk.dat not found in output.")

    except subprocess.CalledProcessError as e:
        print(f"CLASS run failed for {ini_file}: {e}")
    except Exception as err:
        print(f"Unexpected error running CLASS: {err}")
    finally:
        # === Step 4: Cleanup copied files ===
        for temp_file in [psd_target, ini_target]:
            if os.path.exists(temp_file):
                os.remove(temp_file)
