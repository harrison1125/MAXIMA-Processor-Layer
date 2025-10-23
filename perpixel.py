import numpy as np
import matplotlib.pyplot as plt
import numpy as np

# Thickness values in mm
thicknesses = [0.1, 0.3, 0.5]  
colors = {0.1: "blue", 0.3: "orange", 0.5: "green"}  # color mapping

# Detector settings
detector_width_mm = 75      # Total width of detector in mm
num_pixels = 1024           # Number of pixels across the detector
pixel_size_mm = detector_width_mm / num_pixels

# Pixel positions across the detector (centered at 0)
y = np.linspace(-detector_width_mm / 2, detector_width_mm / 2, num_pixels)

# Sample-to-detector distances to analyze
D_values = [70, 100, 130]  # in mm
thickness_map = {70: 0.1, 100: 0.3, 130: 0.5}

# X-ray wavelength in nm
wavelength_nm = 0.05134  # In Kα

# Plotting
plt.figure(figsize=(10, 5))

for D in D_values:
    # Δβ in radians
    delta_beta_rad = (D / (D**2 + y**2))*(pixel_size_mm)
    delta_beta_q = np.sin(delta_beta_rad/2) * (4*np.pi/wavelength_nm)

    plt.plot(y, delta_beta_q, 
             label=f'STDD = {D} mm', 
             color=colors[thickness_map[D]], linewidth=2)


plt.xlabel("Position on detector (mm)", fontsize=15)
plt.ylabel("$\Delta$q (nm⁻¹)", fontsize=15)
plt.ylim(0.05,0.16)
plt.legend(fontsize=15)
plt.grid(True)
plt.tick_params(labelsize=15)
plt.tight_layout()
plt.show()


import numpy as np
import matplotlib.pyplot as plt

import numpy as np
import matplotlib.pyplot as plt

# Detector settings
detector_width_mm = 75.0
num_pixels = 1024
y = np.linspace(-detector_width_mm / 2, detector_width_mm / 2, num_pixels)

# Geometry parameters
D = 100.0   # distance from sample to detector (mm)
b = 0.1     # beam height (mm)
thicknesses = [0.1, 0.2, 0.3]  # sample thicknesses (mm)
colors = {0.1: "blue", 0.2: "orange", 0.3: "green"}

# X-ray wavelength (nm)
λ = 0.514  # nm

def delta_q_positive(y, D, t, b, λ):
    """Δq for top-left → bottom-right corner."""
    y_tl, z_tl = -b / 2.0, +t / 2.0
    y_br, z_br = +b / 2.0, -t / 2.0
    θ_tl = np.arctan((y - y_tl) / (D - z_tl))
    θ_br = np.arctan((y - y_br) / (D - z_br))
    return (4 * np.pi / λ) * (np.sin(θ_tl) - np.sin(θ_br))


def delta_q_negative(y, D, t, b, λ):
    """Δq for top-right → bottom-left corner."""
    y_tr, z_tr = +b / 2.0, +t / 2.0
    y_bl, z_bl = -b / 2.0, -t / 2.0
    θ_tr = np.arctan((y - y_tr) / (D - z_tr))
    θ_bl = np.arctan((y - y_bl) / (D - z_bl))
    return (4 * np.pi / λ) * (np.sin(θ_tr) - np.sin(θ_bl))


def delta_q_top(y, D, t, b, λ):
    """Δq between top-left and top-right (same z = +t/2)."""
    y_tl, z_tl = -b / 2.0, +t / 2.0
    y_tr, z_tr = +b / 2.0, +t / 2.0
    θ_tl = np.arctan((y - y_tl) / (D - z_tl))
    θ_tr = np.arctan((y - y_tr) / (D - z_tr))
    return (4 * np.pi / λ) * (np.sin(θ_tl) - np.sin(θ_tr))


# Plot combined Δq with 3 regimes
plt.figure(figsize=(10, 5))

for t in thicknesses:
    dq_pos = delta_q_positive(y, D, t, b, λ)
    dq_neg = delta_q_negative(y, D, t, b, λ)
    dq_mid = delta_q_top(y, D, t, b, λ)

    # Combine three zones
    dq_combined = np.zeros_like(y)
    dq_combined[y >= b / 2] = dq_pos[y >= b / 2]
    dq_combined[y <= -b / 2] = dq_neg[y <= -b / 2]
    dq_combined[(y > -b / 2) & (y < b / 2)] = dq_mid[(y > -b / 2) & (y < b / 2)]

    plt.plot(y, np.abs(dq_combined), color=colors[t], lw=2, label=f't = {int(t*1000)} µm')

plt.xlabel("Detector position y (mm)", fontsize=14)
plt.ylabel(r"$\Delta q\ \mathrm{(nm^{-1})}$", fontsize=14)
plt.grid(True)
plt.legend(fontsize=12)
plt.tight_layout()
plt.show()
