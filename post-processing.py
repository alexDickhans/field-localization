import cv2
import numpy as np
import json
import argparse

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

def detect_bright_objects(frame, frame_count):
    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Apply a threshold to get a binary image
    _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)

    # Find contours in the binary image
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        # Get the bounding rectangle for each contour
        x, y, w, h = cv2.boundingRect(contour)
        print(f"Contour location: x={x}, y={y}, width={w}, height={h}")

        # Draw the bounding rectangle on the original frame
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    if len(contours) > 0:
        x, y, _, _ = cv2.boundingRect(contours[0])

        x_transformed = x - 1000
        y_transformed = y - 1000

        x_final = x_transformed * 1.783207 / 1000
        y_final = y_transformed * -1.783207 / 1000

        print("x: {}, y: {}".format(x_final, y_final))

        # Append data
        append_data(frame_count / cap.get(cv2.CAP_PROP_FPS), x_final, y_final)

        # Put in the frame
        cv2.putText(frame, f"x: {x_final:.2f}, y: {y_final:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    return frame

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Undistort and apply homography to a video.")
parser.add_argument("video_path", type=str, help="Path to the video file.")
parser.add_argument("calibration_file", type=str, help="Path to the .npz file containing calibration data.")
parser.add_argument("homography_file", type=str, help="Path to the .npz file containing homography matrix.")
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

# Get the video frame size
ret, frame = cap.read()
if not ret:
    print("Error: Could not read frame from video.")
    cap.release()
    exit()

h, w = frame.shape[:2]
width = 2000

# Estimate new camera matrix for undistort rectify
balance = 0.5  # Adjust this value to show more or less of the original image
new_K = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(K, D, (w, h), np.eye(3), balance=balance)

# Initialize undistort rectify map
map1, map2 = cv2.fisheye.initUndistortRectifyMap(K, D, np.eye(3), new_K, (w, h), cv2.CV_16SC2)

# Create a VideoWriter object to save the processed video
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
output_path = args.video_path.rsplit('.', 1)[0] + "_processed.mp4"
out = cv2.VideoWriter(output_path, fourcc, cap.get(cv2.CAP_PROP_FPS), (width, width))

# Process the video frames
frame_count = 0
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.UMat(frame)

    # Undistort the frame
    undistorted_frame = cv2.remap(frame, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)

    # Apply homography to undo perspective shift
    warped_frame = cv2.warpPerspective(undistorted_frame, H, (width, width))

    warped_frame_with_contours = detect_bright_objects(warped_frame, frame_count)

    # Write the processed frame to the output video
    out.write(warped_frame_with_contours)

    # Display the processed frame
    cv2.imshow("Processed Video", warped_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    frame_count += 1

# Release resources
cap.release()
out.release()
cv2.destroyAllWindows()

# Save the point data to a .json file
output_json_path = args.video_path.rsplit('.', 1)[0] + "_point_data.json"
with open(output_json_path, 'w') as f:
    json.dump({"data": pointData}, f, indent=4)

print(f"Processed video saved to {output_path}")