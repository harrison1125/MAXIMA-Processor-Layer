import os
import matplotlib.pyplot as plt

# Define the target directory
directory = "/Users/hpark108/20250318_CuTi_for_Rohit/Automated_Data_Handling"

# Change to the directory
os.chdir(directory)

# List all files
filenames = os.listdir(directory)

# Filter only .mca files
mca_files = [f for f in filenames if f.endswith(".mca")]

# Print the filenames
print("MCA Files in directory:", mca_files)

# Loop through each MCA file and read content
for filename in mca_files:
    filepath = os.path.join(directory, filename)
    
    try:
        # Open and read the ASCII .mca file
        with open(filepath, "rb") as file:
            lines = file.readlines()

            if not lines:  # Check if the file is empty
                print(f"Skipping {filename}: File is empty.")
                continue

            data_start = 0
            for i, line in enumerate(lines):
                if line.strip().isdigit():  # First numeric-only line marks data start
                    data_start = i
                    break

            # Extract spectrum data (assuming each line represents a count)
            spectrum_counts = [int(line.strip()) for line in lines[data_start:] if line.strip().isdigit()]
            channels = range(0, len(spectrum_counts))

            # Plot the spectrum
            plt.figure(figsize=(10, 6))
            plt.plot(channels, spectrum_counts, marker='o', linestyle='-', markersize=2)
            plt.xlabel("Channel")
            plt.ylabel("Counts")
            plt.title(f"Spectrum Data - {filename}")
            plt.grid(True)

            # Save the plot
            plot_filename = os.path.join(directory, f"{os.path.splitext(filename)[0]}.png")
            plt.savefig(plot_filename, dpi=300)
            plt.close()

            print(f"Plot saved: {plot_filename}")

    except Exception as e:
        print(f"Could not process {filename}: {e}")
