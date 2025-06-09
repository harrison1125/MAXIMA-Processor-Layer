import os
import cv2
import numpy as np
from PIL import Image

# === CONFIGURATION ===
sample_img_path = "/Users/hpark108/Desktop/Sample Images/Overaged 1.png"
image_dir = "/Users/hpark108/Desktop/Immediate/20250604 Overaged CuTi samples for Rohit/156 2506_4_5_0001-01-01_00-00-00+00-00/images"
lineout_dir = image_dir
output_video = "Overaged 1.mp4"
fps = 3

# Marker movement: 0.0 = top, 1.0 = bottom
marker_start_pos = 1
marker_end_pos = 0

# Frame range (inclusive)
start_scan_point = 62
end_scan_point = 92

# === FUNCTIONS ===
def resize_with_padding(img, target_size=(400, 400), pad_color=(0, 0, 0)):
    original_size = img.size
    ratio = min(target_size[0] / original_size[0], target_size[1] / original_size[1])
    new_size = (int(original_size[0] * ratio), int(original_size[1] * ratio))
    img = img.resize(new_size, Image.LANCZOS)

    new_img = Image.new("RGB", target_size, pad_color)
    paste_pos = ((target_size[0] - new_size[0]) // 2, (target_size[1] - new_size[1]) // 2)
    new_img.paste(img, paste_pos)
    return new_img, paste_pos[1], new_size[1]  # return padding for marker placement

# === SETUP ===
scan_indices = list(range(start_scan_point, end_scan_point + 1))
num_frames = len(scan_indices)

# Load and resize sample image with aspect ratio preserved
sample_image_pil = Image.open(sample_img_path).convert("RGB")
sample_image_pil, top_padding, img_height = resize_with_padding(sample_image_pil)
sample_array = np.array(sample_image_pil)

# Video writer setup
frame_height, frame_width = 400, 400 * 3  # 3 panels
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video_writer = cv2.VideoWriter(output_video, fourcc, fps, (frame_width, frame_height))

for frame_num, scan_index in enumerate(scan_indices):
    # Compute marker position
    frac = frame_num / (num_frames - 1)
    relative_marker_pos = marker_start_pos * (1 - frac) + marker_end_pos * frac
    y_pos = int(top_padding + relative_marker_pos * img_height)

    # Draw marker on sample
    marker_img = sample_array.copy()
    cv2.circle(marker_img, (marker_img.shape[1] // 2, y_pos), 6, (255, 0, 0), -1)

    # Load TIFF
    tiff_path = os.path.join(image_dir, f"scan_point_{scan_index}.tiff")
    if not os.path.exists(tiff_path):
        print(f"❌ Missing TIFF: {tiff_path}")
        continue
    tiff_img = Image.open(tiff_path).convert("RGB").resize((400, 400))
    tiff_array = np.array(tiff_img)
    tiff_array = cv2.convertScaleAbs(tiff_array, alpha=500, beta=0)  # contrast/brightness

    # Load PNG lineout
    png_path = os.path.join(lineout_dir, f"scan_point_{scan_index}.png")
    if not os.path.exists(png_path):
        print(f"❌ Missing PNG: {png_path}")
        continue
    lineout_img = Image.open(png_path).convert("RGB").resize((400, 400))
    lineout_array = np.array(lineout_img)

    # Combine panels
    combined = np.hstack((marker_img, tiff_array, lineout_array))

    # Write to video
    video_writer.write(cv2.cvtColor(combined, cv2.COLOR_RGB2BGR))

video_writer.release()
print("✅ Video saved as:", output_video)
