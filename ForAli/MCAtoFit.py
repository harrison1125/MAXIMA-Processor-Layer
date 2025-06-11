import subprocess
import os

# Config path
config_path = "/Users/hpark108/Desktop/pymca/AutomaticModeMAXIMACalib.cfg"
root_dir = "/Users/hpark108/Desktop/Immediate"

for dirpath, dirnames, filenames in os.walk(root_dir):
    # Collect .mca files only in the current folder
    mca_files = [os.path.join(dirpath, f) for f in filenames if f.lower().endswith(".mca")]

    # Process .tif/.tiff files (same folder)
    for f in filenames:
        if f.lower().endswith((".tif", ".tiff")):
            base_name, _ = os.path.splitext(f)
            output_dat = os.path.join(dirpath, base_name + ".dat")
            output_png = os.path.join(dirpath, base_name + ".png")
            print(f"Found TIFF: {os.path.join(dirpath, f)}")
            print(f"Would generate: {output_dat}, {output_png}")
            # Insert TIFF processing here if needed

    # Run pymcabatch if there are .mca files in the folder
    if mca_files:
        print(f"Processing folder: {dirpath} with {len(mca_files)} .mca files")
        
        # Make sure output directory exists (in this case, same as folder)
        os.makedirs(dirpath, exist_ok=True)

        command = [
            "pymcabatch",
            f"--cfg={config_path}",
            f"--outdir={dirpath}",
            "--concentrations=1",
            "--exitonend=1"
        ] + mca_files

        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode == 0:
            print(result.stdout)
        else:
            print(f"pymcabatch failed in {dirpath} with error code {result.returncode}")
            print(result.stderr)
