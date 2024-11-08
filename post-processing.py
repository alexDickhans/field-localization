import json
import math
import sys

import cv2
import time

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
    params.maxArea = 80.0
    params.filterByCircularity = False
    params.minCircularity = 0.8
    params.filterByConvexity = False
    params.minConvexity = 0.8
    params.filterByInertia = False

    detector = cv2.SimpleBlobDetector_create(params)

    fps = cap.get(cv2.CAP_PROP_FPS)
    print(f"Framerate: {fps} frames per second")

    # Get the total number of frames in the video
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    processed_frames = 0

    # List to store x/y time data
    xy_time_data = []

    # display the video
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            print("not ret")
            break

        frame_count += 1

        if (frame_count % 4 != 0):
            continue

        # Undistort the frame using the calibration data
        frame = cv2.undistort(frame, mtx, dist, None, mtx)

        # Apply binary thresholding
        threshold_value = 20
        max_value = 255
        _, binary_frame = cv2.threshold(frame, threshold_value, max_value, cv2.THRESH_BINARY)

        inverted_binary_frame = cv2.bitwise_not(binary_frame)

        # Detect blobs in the frame
        keypoints = detector.detect(inverted_binary_frame)

        # Brighten the frame
        frame = cv2.multiply(frame, np.full(frame.shape, 5, dtype=np.uint8))

        # Draw the keypoints on the frame
        frame = cv2.drawKeypoints(frame, keypoints, np.array([]), (0, 0, 255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        time_stamp = frame_count / fps

        # Calculate the position using matrix.py for each blob
        if len(keypoints) > 0:
            keypoint_data = []
            for keypoint in keypoints:
                x, y = keypoint.pt
                result = coordinate_system.transform(np.array([x, y]))
                keypoint_data.append({"x": result[0], "y": result[1], "t": None})
                cv2.putText(frame, f"({result[0]:.2f}, {result[1]:.2f})", (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            xy_time_data.append({"time": time_stamp, "data": keypoint_data})
        else:
            # append nothing
            xy_time_data.append({"time": time_stamp, "data": []})

        # Update and print the percentage done
        processed_frames += 1
        percent_done = (processed_frames / total_frames) * 100
        print(f"Processing: {percent_done:.2f}% done")

        # cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    # Save x/y time data to JSON file
    with open('xy_time_data.json', 'w') as json_file:
        json.dump({"data": xy_time_data}, json_file, indent=4)

    print("x/y time data saved to 'xy_time_data.json'.")