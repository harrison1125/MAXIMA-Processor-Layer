import os
import re
import csv
import matplotlib.pyplot as plt

def calculate_atomic_percent_ti(ti_mass_fraction, cu_mass_fraction):
    """Calculate atomic percentages of Cu and Ti from mass fractions."""
    cu_atomic_weight = 63.546
    ti_atomic_weight = 47.867

    n_cu = cu_mass_fraction / cu_atomic_weight
    n_ti = ti_mass_fraction / ti_atomic_weight
    n_total = n_cu + n_ti

    at_percent_cu = (n_cu / n_total) * 100
    at_percent_ti = (n_ti / n_total) * 100

    return at_percent_cu, at_percent_ti

# === Root directory to search ===
root_dir = "/Users/hpark108/Desktop/Immediate"

# Regex pattern to extract scan point, Ti, and Cu mass fractions
pattern = re.compile(
    r"SOURCE:\s*scan_point_(\d+)\.mca.*?"
    r"Ti\s+K\s+[\d.eE+-]+\s+[\d.eE+-]+\s+([\d.eE+-]+).*?"
    r"Cu\s+K\s+[\d.eE+-]+\s+[\d.eE+-]+\s+([\d.eE+-]+)",
    re.DOTALL
)

# === Walk through directory and process .txt files ===
for dirpath, dirnames, filenames in os.walk(root_dir):
    for filename in filenames:
        base_name, ext = os.path.splitext(filename)
        ext = ext.lower()

        if ext == ".txt":
            full_path = os.path.join(dirpath, filename)
            print(f"Processing: {full_path}")

            with open(full_path, 'r') as f:
                data_text = f.read()

            matches = pattern.findall(data_text)

            if not matches:
                print(f"  No valid scan data found in {filename}")
                continue

            ti_mass = {}
            cu_mass = {}
            ti_at_percent = {}

            for scan_point, ti_frac, cu_frac in matches:
                sp = int(scan_point)
                ti_f = float(ti_frac)
                cu_f = float(cu_frac)
                ti_mass[sp] = ti_f
                cu_mass[sp] = cu_f
                _, ti_at = calculate_atomic_percent_ti(ti_f, cu_f)
                ti_at_percent[sp] = ti_at

            sorted_points = sorted(ti_mass.keys())
            ti_at_values = [ti_at_percent[sp] for sp in sorted_points]

            # === Plot Ti atomic percent ===
            plt.figure(figsize=(10, 6))
            plt.plot(sorted_points, ti_at_values, marker='^', color='purple', label='Ti Atomic Percent')
            plt.xlabel('Scan Point')
            plt.ylabel('Ti Atomic Percent (%)')
            plt.title(f'Ti Atomic Percent')
            plt.legend()
            plt.grid(True)
            plt.tight_layout()

            output_png = os.path.join(dirpath, f"TiAtomicPercent.png")
            plt.savefig(output_png)
            plt.close()
            print(f"  Saved plot: {output_png}") 

            # === Write CSV with scan data ===
            output_csv = os.path.join(dirpath, f"TiAtomicPercent.csv")
            with open(output_csv, "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Scan Point", "Ti Mass Fraction", "Cu Mass Fraction", "Ti Atomic Percent"])
                for sp in sorted_points:
                    writer.writerow([sp, ti_mass[sp], cu_mass[sp], ti_at_percent[sp]])

            print(f"  Saved CSV: {output_csv}")

