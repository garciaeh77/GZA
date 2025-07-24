import os
import json
from datetime import datetime

def update_global_summary(results_dir="outputs", html_path="summary.html", results_json="all_results.json"):
    """Collects all run results and generates a global HTML summary."""
    entries = []

    # Search all grid point results
    for folder in sorted(os.listdir(results_dir)):
        result_path = os.path.join(results_dir, folder, "results.json")
        if os.path.exists(result_path):
            with open(result_path) as f:
                data = json.load(f)
            data["tag"] = folder
            timestamp = os.path.getmtime(result_path)
            data["timestamp"] = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
            entries.append(data)

    # Save a central JSON
    with open(results_json, "w") as f:
        json.dump(entries, f, indent=2)

    # Build the HTML
    with open(html_path, "w") as f:
        f.write("<html><body><h1>Global Neutrino Pipeline Summary</h1>\n")
        f.write("<table border='1'>\n")
        f.write("<tr><th>Tag</th><th>Mass (keV)</th><th>Mixing</th><th>Lepton #</th><th>Thermal Mass</th><th>DM Density</th><th>Timestamp</th></tr>\n")
        
        for entry in entries:
            tag_link = f"<a href='outputs/{entry['tag']}/summary.html'>{entry['tag']}</a>"
            mass = f"{entry['mass_keV']:.2e}"
            mixing = f"{entry['mixing_angle']:.1e}"
            L = f"{entry['lepton_asymmetry']:.2e}"
            
            # Handle SKIPPED thermal mass
            thermal_mass = entry['thermal_mass']
            if isinstance(thermal_mass, (float, int)):
                thermal_mass_str = f"{thermal_mass:.2f}"
            else:
                thermal_mass_str = f"<i>{thermal_mass}</i>"

            # Format DM density
            dm_density = entry.get("dm_density", "N/A")
            if isinstance(dm_density, (float, int)):
                dm_density_str = f"{dm_density:.3g}"
            else:
                dm_density_str = str(dm_density)

            time_str = entry["timestamp"]

            f.write(f"<tr><td>{tag_link}</td><td>{mass}</td><td>{mixing}</td><td>{L}</td>")
            f.write(f"<td>{thermal_mass_str}</td><td>{dm_density_str}</td><td>{time_str}</td></tr>\n")

        f.write("</table></body></html>")
