import os
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import pandas as pd
import numpy as np
from matplotlib.image import imread
import seaborn as sns 

# File paths
image_path = '/Users/hpark108/Desktop/Screenshot 2025-06-24 at 11.37.13 PM.png'
xrf_csv_path = '/Users/hpark108/Desktop/set1.csv'
# xrd_sources = [
#     {'dir': '/Users/hpark108/Desktop/Immediate/20250624 Ti-V for Rayna Thesis Proposal/2506_24_2_0001-01-01_00-00-00+00-00', 'scan_points': range(0, 8)},
#     {'dir': '/Users/hpark108/Desktop/Immediate/20250624 Ti-V for Rayna Thesis Proposal/2506_24_3_0001-01-01_00-00-00+00-00', 'scan_points': range(0,5)}
#]
xrd_sources = [
    {'dir': '/Users/hpark108/Desktop/Immediate/20250624 Ti-V for Rayna Thesis Proposal/2506_24_3_0001-01-01_00-00-00+00-00', 'scan_points': range(5,19)},
    {'dir': '/Users/hpark108/Desktop/Immediate/20250624 Ti-V for Rayna Thesis Proposal/2506_24_4_0001-01-01_00-00-00+00-00', 'scan_points': [0]} 
]

# Set up figure and GridSpec
fig = plt.figure(figsize=(15, 8))
gs = gridspec.GridSpec(1, 5, width_ratios=[1, 2, 3, 0, 0], wspace=0.3)
#plt.style.use('seaborn-v0_8-dark-palette')

# ---- PANEL 1: Image (1/5 width) ----
ax_img = fig.add_subplot(gs[0])
img = imread(image_path)
ax_img.imshow(img)
ax_img.axis('off')

# ---- PANEL 2: XRF Plot (2/5 width) ----
ax_xrf = fig.add_subplot(gs[1])
xrf_df = pd.read_csv(xrf_csv_path)
scan_points = xrf_df.iloc[:, 0]
ti_atomic_percent = xrf_df.iloc[:, 1]

ax_xrf.plot(ti_atomic_percent, scan_points, marker='o')
ax_xrf.set_xlabel('Ti Atomic Percent')
ax_xrf.set_ylabel('Scan Point')
#ax_xrf.invert_yaxis()

# ---- PANEL 3: XRD Patterns (3/5 width) ----
ax_xrd = fig.add_subplot(gs[2])

offset_base = 100000000000000

for i, source in enumerate(xrd_sources):
    xrd_dir = source['dir']
    scan_points_list = source['scan_points']
    colors = plt.cm.plasma(np.linspace(0, 1, 14))  # viridis colormap

    for j, scan_point in enumerate(scan_points_list):
        xrd_path = os.path.join(xrd_dir, f'scan_point_{scan_point}.dat')
        if os.path.isfile(xrd_path):
            try:
                data = np.loadtxt(xrd_path, skiprows=1)
                two_theta = data[:, 0]
                intensity = data[:, 1]
                offset = offset_base
                ax_xrd.plot(two_theta, np.log(intensity) + offset, label=f'{os.path.basename(xrd_dir)} Scan {scan_point}', 
                            color=colors[j], linewidth=0.8)
                offset_base += 1  # Increment for visual separation
            except Exception as e:
                print(f"Error reading {xrd_path}: {e}")
        else:
            print(f"File not found: {xrd_path}")

ax_xrd.set_xlabel(r"$q$ (nm$^{-1}$)", fontsize=15)
ax_xrd.set_xlim(20, 70)
ax_xrd.set_ylabel('Intensity (log scale)', fontsize=15)
ax_xrd.tick_params(axis='both', labelsize=12)
ax_xrd.set_yticks([])




q_lines3 = [24.7, 26.9, 28.2, 36.4, 42.6, 47.2, 49.2, 50.4, 51.0, 56.1, 59.1,  ] #Pure Ti HCP
q_lines1 = [29.4, 41.6, 50.8, 58.7, 65.5]

q_lines2 = [22.3, 27.4, 35.2, 38.6, 44.6, 47.4, 52.3, 54.7, 59.1, 61.0, 65.1] #omega - hexagonal
# q_lines = [24.9, 26.3 ,28.2, 36.2, 43.0, 46.8, 49.8, 50.6, 51.4, 52.7 ]

# for q in q_lines1:
#     ax_xrd.axvline(x=q, color='red', linestyle='--', linewidth=0.8)

# for q in q_lines2:
#    ax_xrd.axvline(x=q, color='black', linestyle='-', linewidth=0.8)

# for q in q_lines3:
#    ax_xrd.axvline(x=q, color='green', linestyle=':', linewidth=0.8)


#ax_xrd.legend(loc='upper right', fontsize='xx-small', ncol=2)

plt.tight_layout()
plt.show()
