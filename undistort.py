import cv2
import numpy as np
import argparse

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Undistort a video using saved calibration matrices.")
parser.add_argument("video_path", type=str, help="Path to the video file to be undistorted.")
parser.add_argument("calibration_file", type=str, help="Path to the .npz file containing calibration data.")
args = parser.parse_args()

# Load the calibration data
with np.load(args.calibration_file) as data:
    K = data['K']
    D = data['D']

# Open the video file
cap = cv2.VideoCapture(args.video_path)
if not cap.isOpened():
    print(f"Error: Could not open video {args.video_path}")
    exit()

# Get the video frame size
ret, frame = cap.read()
if not ret:
    print("Error: Could not read frame from video.")
    cap.release()
    exit()

h, w = frame.shape[:2]

# Estimate new camera matrix for undistort rectify
balance = 0.5  # Adjust this value to show more or less of the original image
new_K = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(K, D, (w, h), np.eye(3), balance=balance)

# Initialize undistort rectify map
map1, map2 = cv2.fisheye.initUndistortRectifyMap(K, D, np.eye(3), new_K, (w, h), cv2.CV_16SC2)

# Create a VideoWriter object to save the undistorted video
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
output_path = args.video_path.rsplit('.', 1)[0] + "_undistorted.mp4"
out = cv2.VideoWriter(output_path, fourcc, cap.get(cv2.CAP_PROP_FPS), (w, h))

# Process the video frames
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Undistort the frame
    undistorted_frame = cv2.remap(frame, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)

    # Write the undistorted frame to the output video
    out.write(undistorted_frame)

    # Display the undistorted frame
    cv2.imshow("Undistorted Video", undistorted_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
out.release()
cv2.destroyAllWindows()

print(f"Undistorted video saved to {output_path}")