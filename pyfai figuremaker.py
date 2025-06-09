import os
import fabio
import numpy as np
import matplotlib.pyplot as plt
from pyFAI.azimuthalIntegrator import AzimuthalIntegrator

# Function to convert .xrf to .mca
def convert_xrf_to_mca(input_file, output_file):
    with open(input_file, 'r') as f:
        lines = f.readlines()

    counts = []
    for line in lines:
        parts = line.strip().split()
        if len(parts) >= 2:
            if parts[0] == "xrf_data":
                continue
            try:
                count = int(float(parts[1]))
                counts.append(count)
            except ValueError:
                continue

    mca_lines = []
    mca_lines.append("<<PMCA SPECTRUM>>")
    mca_lines.append("VERSION: 1.0")
    mca_lines.append(f"CHANNELS: {len(counts)}")
    mca_lines.append("<<DATA>>")
    mca_lines.extend(str(count) for count in counts)
    mca_lines.append("<<END>>")

    with open(output_file, 'w') as f:
        f.write("\n".join(mca_lines))

    print(f"Converted {input_file} -> {output_file}")

# Main script

# Path to the folder containing data
root_dir = "/Users/hpark108/Desktop/Immediate"

# Path to the .poni file
poni_file = "/Users/hpark108/Desktop/Immediate/20240604 run.poni"

# Load the calibration
ai = AzimuthalIntegrator()
ai.load(poni_file)

# Walk through all directories and files
for dirpath, dirnames, filenames in os.walk(root_dir):
    for filename in filenames:
        full_path = os.path.join(dirpath, filename)
        base_name, ext = os.path.splitext(filename)
        ext = ext.lower()

        if ext in [".tif", ".tiff"]:
            output_dat = os.path.join(dirpath, base_name + ".dat")
            output_png = os.path.join(dirpath, base_name + ".png")
            try:
                image = fabio.open(full_path).data
                two_theta, intensity = ai.integrate1d(image, npt=1000)
                np.savetxt(output_dat, np.column_stack((two_theta, intensity)),
                           header="2theta intensity", comments='')
                plt.figure(figsize=(8, 8))
                plt.plot(two_theta, intensity, lw=1)
                plt.xlabel("2θ (degrees)")
                plt.ylabel("Intensity")
                plt.ylim(0.005, 500)
                plt.yscale("log")
                plt.xlim(10, 65)
                plt.tight_layout()
                plt.savefig(output_png, dpi=150)
                plt.close()
                print(f"Saved: {output_dat} and {output_png}")
            except Exception as e:
                print(f"Failed to process TIFF {full_path}: {e}")

        elif ext == ".xrf":
            output_mca = os.path.join(dirpath, base_name + ".mca")
            try:
                convert_xrf_to_mca(full_path, output_mca)
            except Exception as e:
                print(f"Failed to convert XRF {full_path}: {e}")
