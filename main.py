from multiprocessing import Pool, cpu_count, Manager
import time
import os
from config import mass_grid, theta_grid
from runner import process_grid_point
from global_summary import update_global_summary

param_grid = [(m, theta) for m in mass_grid for theta in theta_grid]
status_file = "pipeline_status.json"

def print_progress(progress_dict, total):
    completed = sum(1 for status in progress_dict.values() if status == "done")
    running = sum(1 for status in progress_dict.values() if status == "running")
    failed = sum(1 for status in progress_dict.values() if status == "error")
    print(f"Progress: {completed}/{total} completed | {running} running | {failed} failed")

def wrapped_process(mass, theta, progress_dict):
    tag = f"m_{mass:.1e}_theta_{theta:.1e}"
    progress_dict[tag] = "running"
    try:
        process_grid_point(mass, theta)
        # Only mark as done if results.json was created
        result_path = os.path.join("outputs", tag, "results.json")
        if os.path.exists(result_path):
            progress_dict[tag] = "done"
        else:
            progress_dict[tag] = "error"
    except Exception as e:
        progress_dict[tag] = "error"
        error_dir = os.path.join("outputs", tag)
        os.makedirs(error_dir, exist_ok=True)
        with open(os.path.join(error_dir, "error.log"), "a") as log:
            log.write(str(e) + "\n")
        with open(os.path.join(error_dir, ".fail"), "w") as f:
            f.write("FAILED\n")


def run_all():
    total = len(param_grid)

    with Manager() as manager:
        progress = manager.dict()

        with Pool(cpu_count()) as pool:
            results = [
                pool.apply_async(wrapped_process, args=(m, theta, progress))
                for m, theta in param_grid
            ]

            while any(not r.ready() for r in results):
                print_progress(progress, total)
                time.sleep(5)

            # Wait for all to finish
            for r in results:
                r.wait()

        # Final update
        print_progress(progress, total)
        update_global_summary()

if __name__ == "__main__":
    run_all()
