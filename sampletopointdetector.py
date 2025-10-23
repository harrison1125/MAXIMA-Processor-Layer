import numpy as np
import matplotlib.pyplot as plt

# Detector settings
detector_width_mm = 75      # Total width of detector in mm
num_pixels = 1024           # Number of pixels across the detector
pixel_size_mm = detector_width_mm / num_pixels

# Pixel positions across the detector (centered at 0)
y = np.linspace(-detector_width_mm / 2, detector_width_mm / 2, num_pixels)

# Sample-to-detector distances to analyze
D_values = [70, 100, 130]  # in mm

# Map D_values to thicknesses for consistent coloring
thickness_map = {70: 0.1, 100: 0.3, 130: 0.5}

# Fixed parameter
b = 120.0  # offset

# Color map for thickness
colors = {0.1: "blue", 0.3: "green", 0.5: "red"}

# Plotting
plt.figure(figsize=(10, 5))

for D in D_values:
    # Compute 2theta from detector geometry
    two_theta = np.arctan(y / D)  # in radians
    
    # Broadening equation
    t = thickness_map[D]
    delta_2theta_rad = np.arctan((D + t) / (np.tan(two_theta) * D - b)) - two_theta
    delta_2theta_deg = np.degrees(delta_2theta_rad)
    
    # Plot vs. detector position (y, mm)
    plt.plot(y, delta_2theta_deg, 
             label=f'STDD = {D} mm', 
             color=colors[thickness_map[D]], linewidth=2)

plt.xlabel("Position on detector (mm)", fontsize=15)
plt.ylabel("Δ2θ (degrees)", fontsize=15)
plt.legend(fontsize=15)
plt.grid(True)
plt.tick_params(labelsize=15)
plt.tight_layout()
plt.show()
