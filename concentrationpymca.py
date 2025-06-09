import sys
import os
from PyMca5.PyMcaIO import specfilewrapper as spec
from PyMca5.PyMcaIO import EdfFile
from PyMca5.PyMcaIO.ConfigDict import ConfigDict
from PyMca5.PyMcaCore import Config
from PyMca5.PyMcaPhysics.xrf import FitAll
from PyMca5.PyMcaCore import Spectrum

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

def analyze_with_pymca(mca_file, cfg_file, calib_file):
    # Load the configuration
    config = Config.Config()
    cfg = ConfigDict()
    cfg.read(cfg_file)
    config.update(cfg)

    # Apply calibration file
    if calib_file:
        calib = ConfigDict()
        calib.read(calib_file)
        if 'calibration' in calib:
            config['calibration'] = calib['calibration']

    # Load spectrum
    spectrum = Spectrum.Spectrum(config=config)
    spectrum.readMca(mca_file)
    
    # Perform the fit
    spectrum.estimateBackground()
    spectrum.fitSpectrum()
    results = spectrum.getFitResult()

    # Extract mass fractions
    concentrations = results.get('concentrations', {})

    print("\n--- Mass Fractions ---")
    for element, value in concentrations.items():
        print(f"{element}: {value:.4f}")

    return concentrations

# Example usage: python script.py input.xrf output.mca config.cfg calib.calib
if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python script.py input.xrf output.mca config.cfg calib.calib")
        sys.exit(1)

    xrf_file = sys.argv[1]
    mca_file = sys.argv[2]
    cfg_file = sys.argv[3]
    calib_file = sys.argv[4]

    convert_xrf_to_mca(xrf_file, mca_file)
    analyze_with_pymca(mca_file, cfg_file, calib_file)
