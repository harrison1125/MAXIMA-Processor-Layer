import numpy as np
import matplotlib.pyplot as plt
import os
import glob
import re

# Directories containing your .dat files
data_dirs = [
    '/Users/hpark108/Desktop/Immediate/20250930 updated XRF run/JHAMAC00001-S3R1C1_JHAMAC00001-S3R1C1_1_1_2025-09-29_19-42-34',
    '/Users/hpark108/Desktop/Immediate/20250930 updated XRF run/JHAMAC00001-S3R2C1_JHAMAC00001-S3R2C1_1_1_2025-09-29_19-18-56',
    '/Users/hpark108/Desktop/Immediate/20250930 updated XRF run/JHAMAC00001-S3R3C1_JHAMAC00001-S3R3C1_1_1_2025-09-29_18-51-46',
    '/Users/hpark108/Desktop/Immediate/20250930 updated XRF run/JHAMAC00001-S3R4C1_JHAMAC00001-S3R4C1_1_1_2025-09-29_18-27-12',
    '/Users/hpark108/Desktop/Immediate/20250930 updated XRF run/JHAMAC00001-S3R5C1_JHAMAC00001-S3R5C1_1_1_2025-09-29_17-59-03',
    '/Users/hpark108/Desktop/Immediate/20250930 updated XRF run/JHAMAC00001-S3R6C1_JHAMAC00001-S3R6C1_1_1_2025-09-29_17-28-24'
]


plt.figure(figsize=(12, 8))

offset = 0
offset_step = 0.15  # adjust vertical spacing between curves

# Function to numerically sort filenames
def numerical_sort(value):
    numbers = re.findall(r'\d+', os.path.basename(value))
    return [int(num) for num in numbers]

colors = ['blue', 'orange', 'green', 'blue', 'orange', 'green']

for i, dir_path in enumerate(data_dirs):
    dat_lower = glob.glob(os.path.join(dir_path, "**/*.dat"), recursive=True)
    dat_upper = glob.glob(os.path.join(dir_path, "**/*.DAT"), recursive=True)

    dat_lower_sorted = sorted(dat_lower, key=numerical_sort)
    dat_lower_sorted = dat_lower_sorted[::- 1]
    dat_upper_sorted = sorted(dat_upper, key=numerical_sort)

    dat_files = dat_lower_sorted + dat_upper_sorted

    if not dat_files:
        print(f"⚠️ No .dat files found in {dir_path}")
        continue

    color = colors[i % len(colors)]

    for j, file in enumerate(dat_files[::3]):
    # for j, file in enumerate(dat_files):
        try:
            data = np.loadtxt(file, skiprows=1)
            two_theta, intensity = data[:, 0], data[:, 1]
            intensity = intensity / np.max(intensity)
            # Plot with offset
            plt.plot(two_theta, intensity + offset, lw=1.5, color=color)

            # # Add label at the end of the curve
            # plt.text(two_theta[-1] + 0.2, intensity[-1] + offset, os.path.basename(file),
            #          fontsize=10, color=color, va='center')

            offset += offset_step

        except Exception as e:
            print(f"Error reading {file}: {e}")

plt.xlabel(r"$Q$ (nm$^{-1}$)", fontsize=15)
# plt.ylabel("Intensity + offset", fontsize=15)
plt.xlim(25, 65)
plt.yticks([])
plt.tick_params(axis='x', which='major', labelsize=12)
plt.tick_params(axis='x', which='minor', labelsize=12)
plt.tight_layout()

# Save figure
output_png = "/Users/hpark108/Desktop/Immediate/q-range-waterfall.png" 
plt.savefig(output_png, dpi=150)
plt.close()

print(f"✅ Saved waterfall plot with data labels: {output_png}")