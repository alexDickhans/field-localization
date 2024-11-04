import json
import math
import sys

import cv2
import time

import subprocess

import numpy as np

from matrix import coordinate_system, CoordinateSystem

# main program
if __name__ == "__main__":
    # Load the JSON data from a file
    config_file = sys.argv[2] if len(sys.argv) > 2 else 'config.json'
    with open(config_file, 'r') as file:
        data = json.load(file)

    coordinate_system = CoordinateSystem(data)

    # check for args
    if len(sys.argv) < 2:
        print("Usage: python post-processing.py <video_file>")
        sys.exit(1)

    # load a mp4 file from the first arguments
    cap = cv2.VideoCapture(sys.argv[1])

    # Check if the video opened successfully
    if not cap.isOpened():
        print("Error: Could not open video.")
        sys.exit(1)

    # Load the calibration data
    calibration_data = np.load('calibration_data.npz')
    mtx = calibration_data['mtx']
    dist = calibration_data['dist']

    # create a blob detector with default parameters
    params = cv2.SimpleBlobDetector_Params()

    # Set the parameters for blob detection
    params.filterByArea = False
    params.maxArea = 100.0
    params.filterByCircularity = False
    params.minCircularity = 0.8
    params.filterByConvexity = False
    params.minConvexity = 0.8
    params.filterByInertia = False

    detector = cv2.SimpleBlobDetector_create(params)

    # display the video
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_count += 1
        if (frame_count % 16 != 0):
            continue

        # Undistort the frame using the calibration data
        frame = cv2.undistort(frame, mtx, dist, None, mtx)

        # Apply binary thresholding
        threshold_value = 220
        max_value = 255
        _, binary_frame = cv2.threshold(frame, threshold_value, max_value, cv2.THRESH_BINARY)

        inverted_binary_frame = cv2.bitwise_not(binary_frame)

        # Detect blobs in the frame
        keypoints = detector.detect(inverted_binary_frame)

        # Draw the keypoints on the frame
        frame = cv2.drawKeypoints(frame, keypoints, np.array([]), (0, 0, 255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

        position = coordinate_system.inverse([0, math.cos(time.time())])

        # Draw the origin on the frame
        cv2.circle(frame, (int(position[0]), int(position[1])), 5, (0, 255, 0), -1)

        # Calculate the position using matrix.py for the smallest blob
        if len(keypoints) > 0:
            smallest_blob = min(keypoints, key=lambda x: x.size)
            x, y = smallest_blob.pt
            result = coordinate_system.transform(np.array([x, y]))
            cv2.putText(frame, f"({result[0]:.2f}, {result[1]:.2f})", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()