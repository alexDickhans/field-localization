import numpy as np
import cv2
import argparse

parser = argparse.ArgumentParser(description="Calculate homography matrix from corresponding points.")
parser.add_argument("output_file", type=str, help="Path to save the homography matrix.")
args = parser.parse_args()

width = 2000

# Four corners of the book in source image
pts_src = np.array([[460,145], [1560, 110], [476, 1210], [1529, 1247]])

# Read destination image.
# Four corners of the book in destination image.
pts_dst = np.array([[0, 0], [width, 0], [0, width], [width, width]])

# Calculate Homography
H, status = cv2.findHomography(pts_src, pts_dst)

# Save the homography matrix to a .npz file
np.savez(args.output_file, H=H)
print(f"Homography matrix saved to {args.output_file}")