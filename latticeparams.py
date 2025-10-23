import pandas as pd
import numpy as np

# --- File path ---
file_path = '/Users/hpark108/maxima_2theta_by_column.csv'

# --- Load Excel file safely ---
try:
    df = pd.read_csv(file_path)
except ImportError as e:
    print("Error: 'openpyxl' is not installed. Install it using 'pip install openpyxl'.")
    raise e

# --- Clean column names ---
df.columns = [col.strip() for col in df.columns]  # remove extra spaces
print("Columns found in the file:", df.columns.tolist())

# --- Find the column with reciprocal lattice data ---
reciprocal_column = None
for col in df.columns:
    if 'max_29_32_2theta' in col:
        reciprocal_column = col
        break

if reciprocal_column is None:
    raise KeyError("Could not find a column with reciprocal lattice data (nm^-1).")

# --- Calculate interplanar spacing d (nm) for each scan point ---
df['d_nm'] = 2*np.pi / df[reciprocal_column]

# --- Lattice parameter calculation for FCC Cu (111 plane) for each scan point ---
h, k, l = 1, 1, 1
df['a_nm'] = df['d_nm'] * np.sqrt(h**2 + k**2 + l**2)
df['a_A'] = df['a_nm'] * 10  # convert nm to Å

# --- Print results ---
print(df[['scan_point', 'd_nm', 'a_nm', 'a_A']])

# --- Optional: save results to a new Excel file ---
output_file = '/Users/hpark108/Desktop/lattice_parameters_results.xlsx'
df.to_excel(output_file, index=False)
print(f"Results saved to {output_file}")

import matplotlib.pyplot as plt

# --- Use index as scan number (0, 1, 2, ... N-1) ---
x_vals = range(len(df))  # gives 0 to number of rows-1

plt.figure(figsize=(8,3))
plt.plot(x_vals, df['a_A'], marker='o', linestyle='-', color='b', label='Lattice parameter (Å)')

# --- Labels & title ---
plt.xlabel('Position (mm)', fontsize=15)
plt.ylabel('Lattice Parameter (Å)', fontsize=15)
# plt.ylim(3.6075, 3.6225)
#plt.title('FCC Cu (111) Lattice Parameter vs Scan Number', fontsize=14)
#plt.legend()
#plt.grid(True, linestyle='--', alpha=0.6)

plt.show()

