import cv2
import numpy as np
import json
import argparse
from concurrent.futures import ThreadPoolExecutor
import os

pointData = []

def append_data(time, x, y):
    pointData.append({
        "time": time,
        "data": [
            {
                "x": x,
                "y": y,
                "t": None
            }
        ]
    })

def detect_bright_objects(frame, frame_count, fps):
    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Apply a threshold to get a binary image
    _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)

    # Find contours in the binary image
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        # Get the bounding rectangle for the largest contour
        contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(contour)
        print(f"Contour location: x={x}, y={y}, width={w}, height={h}")

        # Draw the bounding rectangle on the original frame
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        x_transformed = x - 1000
        y_transformed = y - 1000

        x_final = x_transformed * 1.783207 / 1000
        y_final = y_transformed * -1.783207 / 1000

        print("x: {}, y: {}".format(x_final, y_final))

        # Append data
        append_data(frame_count / fps, x_final, y_final)

        # Put in the frame
        cv2.putText(frame, f"x: {x_final:.2f}, y: {y_final:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    return frame

def process_frame(frame, frame_count, fps, map1, map2, H):
    frame = cv2.UMat(frame)

    # Undistort the frame
    undistorted_frame = cv2.remap(frame, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)

    # Apply homography to undo perspective shift
    warped_frame = cv2.warpPerspective(undistorted_frame, H, (2000, 2000))

    return detect_bright_objects(warped_frame, frame_count, fps)

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Undistort and apply homography to a video.")
parser.add_argument("--calibration_file", type=str, default=os.path.join(os.path.dirname(__file__), 'calibration_data.npz'), help="Path to the .npz file containing calibration data.")
parser.add_argument("--homography_file", type=str, default=os.path.join(os.path.dirname(__file__), 'homo.npz'), help="Path to the .npz file containing homography matrix.")
parser.add_argument("video_path", type=str, help="Path to the video file.")
args = parser.parse_args()

# Load the calibration data
with np.load(args.calibration_file) as data:
    K = data['K']
    D = data['D']

# Load the homography matrix
with np.load(args.homography_file) as data:
    H = data['H']

# Open the video file
cap = cv2.VideoCapture(args.video_path)
if not cap.isOpened():
    print(f"Error: Could not open video {args.video_path}")
    exit()

# Get the video frame size and FPS
ret, frame = cap.read()
if not ret:
    print("Error: Could not read frame from video.")
    cap.release()
    exit()

h, w = frame.shape[:2]
fps = cap.get(cv2.CAP_PROP_FPS)

# Estimate new camera matrix for undistort rectify
balance = 0.5  # Adjust this value to show more or less of the original image
new_K = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(K, D, (w, h), np.eye(3), balance=balance)

# Initialize undistort rectify map
map1, map2 = cv2.fisheye.initUndistortRectifyMap(K, D, np.eye(3), new_K, (w, h), cv2.CV_16SC2)

# Process the video frames
frame_count = 0
with ThreadPoolExecutor() as executor:
    futures = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        futures.append(executor.submit(process_frame, frame, frame_count, fps, map1, map2, H))

        frame_count += 1

    for future in futures:
        future.result()

print("Processing complete")

# Release resources
cap.release()
cv2.destroyAllWindows()

# Sort pointData by time
pointData = sorted(pointData, key=lambda x: x['time'])

# Save the point data to a .json file
output_json_path = args.video_path.rsplit('.', 1)[0] + "_point_data.json"
with open(output_json_path, 'w') as f:
    json.dump({"data": pointData}, f, indent=4)

print(f"Processed data saved to {output_json_path}")