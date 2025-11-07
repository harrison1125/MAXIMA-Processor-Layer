import os
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import pandas as pd
import numpy as np
from matplotlib.image import imread
import matplotlib.ticker as ticker
import glob
import re

# -------------------------
# File paths
# -------------------------
image_path = '/Users/hpark108/Desktop/Sample Image.png'

# Directories containing both XRF CSV and XRD .dat files
data_dirs = [
    '/Users/hpark108/Desktop/Immediate/20250930 updated XRF run/JHAMAC00001-S3R1C1_JHAMAC00001-S3R1C1_1_1_2025-09-29_19-42-34',
    '/Users/hpark108/Desktop/Immediate/20250930 updated XRF run/JHAMAC00001-S3R2C1_JHAMAC00001-S3R2C1_1_1_2025-09-29_19-18-56',
    '/Users/hpark108/Desktop/Immediate/20250930 updated XRF run/JHAMAC00001-S3R3C1_JHAMAC00001-S3R3C1_1_1_2025-09-29_18-51-46',
    '/Users/hpark108/Desktop/Immediate/20250930 updated XRF run/JHAMAC00001-S3R4C1_JHAMAC00001-S3R4C1_1_1_2025-09-29_18-27-12',
    '/Users/hpark108/Desktop/Immediate/20250930 updated XRF run/JHAMAC00001-S3R5C1_JHAMAC00001-S3R5C1_1_1_2025-09-29_17-59-03',
    '/Users/hpark108/Desktop/Immediate/20250930 updated XRF run/JHAMAC00001-S3R6C1_JHAMAC00001-S3R6C1_1_1_2025-09-29_17-28-24'
]

# -------------------------
# Load lattice parameter CSVs in same order as XRF folders
# -------------------------
lattice_data_list = []

for i, dir_path in enumerate(data_dirs):
    folder_name = os.path.basename(os.path.normpath(dir_path))
    csv_path = os.path.join(dir_path, f"{folder_name}_lattice_parameters.xlsx")
    
    if not os.path.isfile(csv_path):
        print(f"⚠️ Lattice CSV not found: {csv_path}")
        lattice_data_list.append(np.array([]))
        continue
    
    df_lat = pd.read_excel(csv_path)
    if 'a_A_avg' not in df_lat.columns:
        print(f"⚠️ Column 'a_A_avg' not found in {csv_path}")
        lattice_data_list.append(np.array([]))
        continue

    a_values = df_lat['a_A_avg'].values

    # # Reverse folders 0,1,2,5 to match XRF flipping
    # if i in [0, 1, 2, 5]:
    #     a_values = a_values[::-1]
    
    lattice_data_list.append(a_values)

# -------------------------
# Load XRF data for all directories
# -------------------------
xrf_data_list = []
for dir_path in data_dirs:
    xrf_csv_path = os.path.join(dir_path, "raw", "TiAtomicPercent.csv")
    if os.path.isfile(xrf_csv_path):
        xrf_df = pd.read_csv(xrf_csv_path)
        xrf_df = xrf_df[xrf_df.iloc[:, 0].between(4, 31)]
        scan_points = xrf_df.iloc[:, 0]
        ti_atomic_percent = xrf_df.iloc[:, 3]
        xrf_data_list.append((scan_points, ti_atomic_percent))
    else:
        print(f"⚠️ XRF CSV not found: {xrf_csv_path}")
        xrf_data_list.append(([], []))

# -------------------------
# Set up figure with GridSpec
# -------------------------
fig = plt.figure(figsize=(13, 7))
gs = gridspec.GridSpec(1, 5, width_ratios=[0, 1.5, 3, 0, 0], wspace=0.01)

# -------------------------
# PANEL 1: Image
# -------------------------
ax_img = fig.add_subplot(gs[0])
img = imread(image_path)
ax_img.imshow(img)
ax_img.axis('off')

# -------------------------
# PANEL 2: XRF + Lattice parameter
# -------------------------
ax_xrf = fig.add_subplot(gs[1])
colors = ['#1b9e77', '#d95f02', '#7570b3', '#e7298a', '#66a61e', '#e6ab02']
current_bottom = 10

for i, (scan_points, ti_atomic_percent) in enumerate(xrf_data_list):
    if len(scan_points) == 0:
        continue

    min_len = min(len(scan_points), len(lattice_data_list[i]))
    scan_points_trimmed = scan_points[:min_len].values
    ti_atomic_percent_trimmed = ti_atomic_percent[:min_len].values

    # Flip directories 0,1,2,5
    if i in [0, 1, 2, 5]:
        scan_points_flipped = scan_points_trimmed.max() - (scan_points_trimmed - scan_points_trimmed.min())
        scan_points_trimmed = scan_points_flipped

    # Shift to stack
    scan_points_shifted = scan_points_trimmed - scan_points_trimmed.min() + current_bottom

    ax_xrf.plot(ti_atomic_percent_trimmed, scan_points_shifted, marker='o',  markeredgecolor = 'k', linestyle = 'none',
                color=colors[i % len(colors)], label=f'Sample {i+1}')

    current_bottom = scan_points_shifted.max() + 13

ax_xrf.set_xlabel('Ti (at%)', fontsize=14)
ax_xrf.set_ylabel('Position (mm)', fontsize=14)
ax_xrf.tick_params(axis='both', labelsize=12)
ax_xrf.set_xlim(0, 6.99)
ax_xrf.set_ylim(-4, 220)
ax_xrf.yaxis.set_major_locator(ticker.MultipleLocator(20))
ax_xrf.yaxis.set_minor_locator(ticker.MultipleLocator(4))
ax_xrf.xaxis.set_major_locator(ticker.MultipleLocator(1))
ax_xrf.xaxis.set_minor_locator(ticker.MultipleLocator(0.5))
# ax_xrf.legend(fontsize=10)

# Secondary x-axis: lattice parameter
ax_lat = ax_xrf.twiny()
current_bottom_lat = 10

for i, a_values in enumerate(lattice_data_list):
    if len(a_values) == 0:
        continue
    
    min_len = min(len(a_values), len(xrf_data_list[i][0]))
    scan_positions = xrf_data_list[i][0][:min_len].values
    a_values_trimmed = a_values[:min_len] 
    
    if i in [0, 1, 2, 5]:
        scan_positions = scan_positions.max() - (scan_positions - scan_positions.min())
    
    scan_positions_shifted = scan_positions - scan_positions.min() + current_bottom_lat
    ax_lat.plot(a_values_trimmed, scan_positions_shifted, marker = "s", linestyle='None', color=colors[i % len(colors)], label=f'Sample {i+1}')
    
    current_bottom_lat = scan_positions_shifted.max() + 13

ax_lat.set_xlabel('(Cu) Lattice parameter (Å)', fontsize=14)
ax_lat.tick_params(axis='x')
ax_lat.set_xlim(3.61, 3.69)

import matplotlib.lines as mlines

# Create custom legend entries for marker shapes
xrf_marker = mlines.Line2D([], [], color='w', marker='o', linestyle='None', markeredgecolor= 'k',
                            markersize=8, label='Composition')
lat_marker = mlines.Line2D([], [], color='k', marker='s', linestyle='None',
                            markersize=8, label='Lattice parameter') 

# # Add the legend (bottom right, for example)
# ax_xrf.legend(handles=[xrf_marker, lat_marker],
#               fontsize=12, loc='lower right', frameon=False)

# # -------------------------
# # PANEL 3: XRD patterns
# # -------------------------
# ax_xrd = fig.add_subplot(gs[2])
# offset = 0
# offset_step = 0.05
# directory_spacing = 0.3

# def numerical_sort(value):
#     numbers = re.findall(r'\d+', os.path.basename(value))
#     return [int(num) for num in numbers]

# colors_xrd = ['#1b9e77', '#d95f02', '#7570b3', '#e7298a', '#66a61e', '#e6ab02'] #repeated. Consider connecting to XRF colors

# for i, dir_path in enumerate(data_dirs):
#     dat_lower = glob.glob(os.path.join(dir_path, "**/*.dat"), recursive=True)
#     dat_upper = glob.glob(os.path.join(dir_path, "**/*.DAT"), recursive=True)

#     dat_lower_sorted = sorted(dat_lower, key=numerical_sort)[::-1]
#     dat_upper_sorted = sorted(dat_upper, key=numerical_sort)
#     dat_files = dat_lower_sorted + dat_upper_sorted

#     if not dat_files:
#         print(f"⚠️ No .dat files found in {dir_path}")
#         continue

#     color = colors_xrd[i % len(colors_xrd)]

#     for j, file in enumerate(dat_files):
#         try:
#             data = np.loadtxt(file, skiprows=1)
#             two_theta, intensity = data[:, 0], data[:, 1]
#             intensity = intensity / np.max(intensity)
#             ax_xrd.plot(two_theta, intensity + offset, lw=1.5, color=color)
#             offset += offset_step
#         except Exception as e:
#             print(f"Error reading {file}: {e}")
#     offset += directory_spacing

# ax_xrd.set_xlabel(r"$Q$ (nm$^{-1}$)", fontsize=15)
# ax_xrd.set_xlim(24, 65)
# ax_xrd.set_yticks([])
# ax_xrd.tick_params(axis='x', which='major', labelsize=12)
# ax_xrd.tick_params(axis='x', which='minor', labelsize=12)

# -------------------------
# PANEL 3: XRD heatmap with preserved sample spacing
# -------------------------
ax_xrd = fig.add_subplot(gs[2])

def numerical_sort(value):
    numbers = re.findall(r'\d+', os.path.basename(value))
    return [int(num) for num in numbers]

colors_xrd = ['#1b9e77', '#d95f02', '#7570b3', '#e7298a', '#66a61e', '#e6ab02']

epsilon = 1e-6
q_min, q_max = 24, 63
num_points = 1000
directory_gap_rows = 10

q_grid = np.linspace(q_min, q_max, num_points)
heatmap_rows = []

# Add initial blank gap
heatmap_rows.extend([np.full_like(q_grid,0)] * directory_gap_rows)

for i, dir_path in enumerate(data_dirs):
    dat_lower = glob.glob(os.path.join(dir_path, "**/*.dat"), recursive=True)
    dat_upper = glob.glob(os.path.join(dir_path, "**/*.DAT"), recursive=True)
    dat_lower_sorted = sorted(dat_lower, key=numerical_sort)[::-1]
    dat_upper_sorted = sorted(dat_upper, key=numerical_sort)
    dat_files = dat_lower_sorted + dat_upper_sorted

    if not dat_files:
        print(f"⚠️ No .dat files found in {dir_path}")
        continue


    global_min = []
    for j, file in enumerate(dat_files):
        try:
            data = np.loadtxt(file, skiprows=1)
            two_theta, intensity = data[:, 0], data[:, 1]
            mask = (two_theta >= 25) & (two_theta <= 63)
            log_intensity = np.log10(intensity + epsilon)
            min_val = np.min(log_intensity[mask])
            global_min.append(min_val)
        except Exception as e:
            print(f"Error reading {file}: {e}")        
        global_min.sort
        specific_min = global_min[int(len(global_min)/2)]

    for j, file in enumerate(dat_files):
        try:
            data = np.loadtxt(file, skiprows=1)
            two_theta, intensity = data[:, 0], data[:, 1]

            # Log scale with epsilon
            log_intensity = np.log10(intensity + epsilon)

            # Mask to only points where two_theta < 63
            mask = (two_theta >= 25) & (two_theta <= 63)
            # min_val = np.min(log_intensity[mask])
            min_val = specific_min
            max_val = np.max(log_intensity)  # max still uses all points

            # Normalize min=0, max=1
            log_intensity = (log_intensity - min_val) / (max_val - min_val)

            # Interpolate to common q grid
            interp_intensity = np.interp(q_grid, two_theta, log_intensity, left=0, right=0)
            heatmap_rows.append(interp_intensity)
        except Exception as e:
            print(f"Error reading {file}: {e}")

    # Add actual dark gaps
    heatmap_rows.extend([np.full_like(q_grid,0)] * directory_gap_rows)

# Convert to array and plot
if len(heatmap_rows) > 0:
    heatmap_array = np.array(heatmap_rows)
    im = ax_xrd.imshow(
        heatmap_array,
        aspect='auto',
        extent=[q_min, q_max, 0, len(heatmap_rows)],
        origin='lower',
        cmap='cividis',
        vmin=0, vmax=1,
    )
    cbar = plt.colorbar(im, ax=ax_xrd, pad=0.01)
    cbar.set_label('Logarithmic Normalized intensity', fontsize=12)

ax_xrd.set_xlabel(r"$Q$ (nm$^{-1}$)", fontsize=15)
ax_xrd.set_xlim(q_min, q_max)
ax_xrd.set_yticks([])
ax_xrd.tick_params(axis='x', which='major', labelsize=12)
ax_xrd.tick_params(axis='x', which='minor', labelsize=12)

# -------------------------
# Save combined figure
# -------------------------
output_path = '/Users/hpark108/Desktop/Immediate/combined_figure_aligned.png'
plt.tight_layout()
fig.savefig(output_path, dpi=150)
print(f"✅ Figure saved to {output_path}")
