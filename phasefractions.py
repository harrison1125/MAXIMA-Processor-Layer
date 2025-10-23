import numpy as np
import pandas as pd
import glob
from scipy.interpolate import interp1d
from scipy.ndimage import uniform_filter1d
from scipy.optimize import nnls
import os
import matplotlib.pyplot as plt

# Paths
csv_path1 = '/Users/hpark108/Desktop/CIF Files/Cu4Ti.csv'
csv_path2 = '/Users/hpark108/Desktop/CIF Files/95Cu5Ti.csv'
dat_folder = '/Users/hpark108/Desktop/Immediate/20250611 Sample 5 Deep Analysis for MAXIMA paper for Rohit/2506_11_3_0001-01-01_00-00-00+00-00/'
output_plot_folder = '/Users/hpark108/Desktop/Deep'

# Create output folder if it doesn't exist
os.makedirs(output_plot_folder, exist_ok=True)

# Load reference patterns
cu4ti = pd.read_csv(csv_path1, header=None).to_numpy()
cu95ti5 = pd.read_csv(csv_path2, header=None).to_numpy()

q_ref = cu4ti[:, 0]  # assuming both CSVs have same q
int_ref1 = cu4ti[:, 1]
int_ref2 = cu95ti5[:, 1]

# Get list of .dat files
dat_files = sorted(glob.glob(os.path.join(dat_folder, 'scan_point_*.dat')))

def preprocess_dat(file_path, q_min=2.0, q_max=6.8, smooth_window=1):
    import pandas as pd
    from scipy.ndimage import uniform_filter1d

    # Load data with pandas, skip headers
    df = pd.read_csv(file_path, delim_whitespace=True, comment='#')
    
    # Convert q from nm^-1 to Å^-1
    q = df.iloc[:,0].to_numpy() / 10
    intensity = df.iloc[:,1].to_numpy()

    # Restrict q range
    mask = (q >= q_min) & (q <= q_max)
    q = q[mask]
    intensity = intensity[mask]

    # Smooth background
    smoothed = uniform_filter1d(intensity, size=smooth_window)

    # Subtract background
    intensity_corrected = intensity - smoothed
    intensity_corrected[intensity_corrected < 0] = 0

    return q, intensity_corrected


# Function to fit linear combination
def fit_linear_combination(q_data, intensity_data, q_ref, int_ref1, int_ref2):
    # Interpolate reference patterns onto data q
    interp1 = interp1d(q_ref, int_ref1, kind='linear', bounds_error=False, fill_value=0)
    interp2 = interp1d(q_ref, int_ref2, kind='linear', bounds_error=False, fill_value=0)
    ref_matrix = np.vstack([interp1(q_data), interp2(q_data)]).T

    # Non-negative least squares fit
    coefs, _ = nnls(ref_matrix, intensity_data)
    fitted = ref_matrix @ coefs
    return coefs, fitted, interp1(q_data), interp2(q_data)

# Process each .dat file
results = []

for f in dat_files:
    q_data, intensity_corrected = preprocess_dat(f, smooth_window=10)
    coefs, fitted, ref1_interp, ref2_interp = fit_linear_combination(q_data, intensity_corrected, q_ref, int_ref1, int_ref2)
    
    # Save results
    results.append({
        'file': f,
        'a_Cu4Ti': coefs[0],
        'b_Cu95Ti5': coefs[1]
    })
    
    # Plot
    plt.figure(figsize=(8,5))
    plt.plot(q_data, intensity_corrected, label='DAT file', color='blue')
    plt.plot(q_data, ref1_interp * coefs[0], label='Cu4Ti', color='green')
    plt.plot(q_data, ref2_interp * coefs[1], label='95Cu5Ti', color='yellow')
    plt.plot(q_data, fitted, label='Fitted combination', color='red', linestyle='--')
    plt.xlabel('q (Å⁻¹)')
    plt.ylabel('Intensity (counts)')
    plt.title(os.path.basename(f))
    plt.legend()
    plt.tight_layout()
    
    # Save figure
    plot_file = os.path.join(output_plot_folder, os.path.basename(f).replace('.dat', '.png'))
    plt.savefig(plot_file, dpi=300)
    plt.close()
    
    print(f"{f} -> a: {coefs[0]:.4f}, b: {coefs[1]:.4f}, plot saved to {plot_file}")

# Convert results to DataFrame and save
results_df = pd.DataFrame(results)
results_df.to_csv(os.path.join(output_plot_folder, 'linear_combination_results.csv'), index=False)

