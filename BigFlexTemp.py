import os
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import pandas as pd
import numpy as np
from matplotlib.image import imread
import matplotlib.ticker as ticker

# -------------------------
# File paths
# -------------------------
image_path = '/Users/hpark108/Desktop/Sample Image.png'
xrf_csv_path = '/Users/hpark108/Desktop/Immediate/20250930 updated XRF run/JHAMAC00001-S3R6C1_JHAMAC00001-S3R6C1_1_1_2025-09-29_17-28-24/raw/TiAtomicPercent.csv'
lattice_csv_path = '/Users/hpark108/maxima_2theta_by_column.csv'
xrd_sources = [
    {'dir': '/Users/hpark108/Desktop/Immediate/20250930 updated XRF run/JHAMAC00001-S3R6C1_JHAMAC00001-S3R6C1_1_1_2025-09-29_17-28-24','scan_points': range(4,31)}
]

# -------------------------
# Load XRF data
# -------------------------
xrf_df = pd.read_csv(xrf_csv_path)
xrf_df = xrf_df[xrf_df.iloc[:, 0].between(4, 31)]
scan_points = xrf_df.iloc[:, 0]
ti_atomic_percent = xrf_df.iloc[:, 3]

# -------------------------
# Load lattice parameter data
# -------------------------
df = pd.read_csv(lattice_csv_path)
df.columns = [col.strip() for col in df.columns]  # clean column names

# find the reciprocal column automatically
reciprocal_column = None
for col in df.columns:
    if 'max_29_32_2theta' in col:
        reciprocal_column = col
        break
if reciprocal_column is None:
    raise KeyError("Could not find a column with reciprocal lattice data (nm^-1).")

# compute lattice parameter
df['d_nm'] = 2*np.pi / df[reciprocal_column]
h, k, l = 1, 1, 1
df['a_nm'] = df['d_nm'] * np.sqrt(h**2 + k**2 + l**2)
df['a_A'] = df['a_nm'] * 10  # nm → Å

# -------------------------
# Set up figure with GridSpec
# -------------------------

# Set up figure and GridSpec
fig = plt.figure(figsize=(13, 7))
gs = gridspec.GridSpec(1, 5, width_ratios=[0, 1.5, 3, 0, 0], wspace=0.01)
#plt.style.use('seaborn-v0_8-dark-palette')

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

# --- Match lengths ---
min_len = min(len(scan_points), len(df['a_A']))
scan_points_trimmed = scan_points[:min_len]
ti_atomic_percent_trimmed = ti_atomic_percent[:min_len]
a_A_trimmed = df['a_A'][:min_len]

# XRF plot (primary x-axis)
ax_xrf.plot(ti_atomic_percent_trimmed, scan_points_trimmed, marker='o', 
            color='tab:blue', label='Ti (at%)')
ax_xrf.set_xlabel('Ti (at%)', fontsize=14, color='tab:blue')
ax_xrf.set_ylabel('Position (mm)', fontsize=14)
ax_xrf.tick_params(axis='x', labelcolor='tab:blue')
ax_xrf.tick_params(axis='both', labelsize=12)
ax_xrf.set_ylim(-3.8, 31)
ax_xrf.set_xlim(4, 7)

ax_xrf.yaxis.set_major_locator(ticker.MultipleLocator(5))
ax_xrf.yaxis.set_minor_locator(ticker.MultipleLocator(1))
ax_xrf.grid(axis='y', which='minor', linestyle='--', alpha=0.5)
ax_xrf.grid(axis='y', which='major', linestyle='-', alpha=0.7)

# Lattice parameter plot (secondary x-axis)
ax_lat = ax_xrf.twiny()
ax_lat.plot(a_A_trimmed, scan_points_trimmed, marker='s', linestyle='--', 
            color='tab:green', label='Lattice parameter (Å)')
ax_lat.set_xlabel('Lattice parameter (Å)', fontsize=14, color='tab:green')
ax_lat.tick_params(axis='x', labelcolor='tab:green')
ax_lat.set_xlim(a_A_trimmed.min()-0.002, a_A_trimmed.max()+0.002)
ax_lat.set_xlim(3.645, 3.67)
# ax_lat.set_xlim(3.42, 3.445)
# -------------------------
# PANEL 3: XRD patterns
# -------------------------
ax_xrd = fig.add_subplot(gs[2])
offset_base = 0

for i, source in enumerate(xrd_sources):
    xrd_dir = source['dir']
    scan_points_list = source['scan_points']
    colors = plt.cm.cividis(np.linspace(0, 0.6, len(scan_points_list))) 

    for j, scan_point in enumerate(scan_points_list):
        xrd_path = os.path.join(xrd_dir, f'scan_point_{scan_point}.dat')
        if os.path.isfile(xrd_path):
            try:
                data = np.loadtxt(xrd_path, skiprows=1)
                two_theta = data[:, 0]
                intensity = data[:, 1]
                ax_xrd.plot(two_theta, np.log(intensity) + offset_base, 
                            color=colors[j], linewidth=0.8)
                offset_base += 1
            except Exception as e:
                print(f"Error reading {xrd_path}: {e}")
        else:
            print(f"File not found: {xrd_path}")

ax_xrd.set_xlabel(r"$Q$ (nm$^{-1}$)", fontsize=15)
ax_xrd.set_xlim(22, 63)
ax_xrd.tick_params(axis='both', labelsize=12)
ax_xrd.set_yticks([])

plt.tight_layout()
plt.show()
