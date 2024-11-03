import cv2
import time

import subprocess

import numpy as np

from matrix import coordinate_system


def set_frame_rate(device, fps):
    try:
        # Set the frame rate using v4l2-ctl
        subprocess.run(['v4l2-ctl', '--device=' + device, '--set-parm=' + str(fps)], check=True)
        print(f"Frame rate set to {fps} FPS.")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")

def set_brightness(device, brightness_value):
    try:
        # Set the brightness using v4l2-ctl
        # Replace 'brightness' with the actual control name if different
        subprocess.run(['v4l2-ctl', '--device=' + device, '--set-ctrl=brightness=' + str(brightness_value)], check=True)
        print(f"Brightness set to {brightness_value}.")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")

def main():

    # Example usage
    set_brightness('/dev/video0',-64)

    # Initialize video capture object (0 is typically the default camera)
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

    # Check if the camera opened successfully
    if not cap.isOpened():
        print("Error: Could not open video capture.")
        return

    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))

    # Create a blob detector with default parameters
    params = cv2.SimpleBlobDetector_Params()

    # Set the parameters for blob detection
    params.filterByArea = True
    params.minArea = 0.0
    params.maxArea = 300.0
    params.filterByCircularity = True
    params.minCircularity = 0.5
    params.filterByConvexity = True
    params.minConvexity = 0.4
    params.filterByInertia = False

    detector = cv2.SimpleBlobDetector_create(params)

    last_time = time.time()

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()

        # Check if frame was captured correctly
        if not ret:
            print("Error: Failed to grab frame.")
            break

        # Convert the frame to grayscale
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Apply binary thresholding
        threshold_value = 150
        max_value = 255
        _, binary_frame = cv2.threshold(gray_frame, threshold_value, max_value, cv2.THRESH_BINARY)

        inverted_binary_frame = cv2.bitwise_not(binary_frame)

        # Detect blobs in the binary frame
        keypoints = detector.detect(inverted_binary_frame)

        # Draw keypoints on the original frame
        # frame_with_blobs = cv2.drawKeypoints(frame, keypoints, None, (0, 255, 0), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

        # Display the original frame and binary frame
        # cv2.imshow('Original Frame', frame)
        # cv2.imshow('Binary Frame', inverted_binary_frame)
        # cv2.imshow('Blobs', frame_with_blobs)

        # Calculate the position using matrix.py for the largest blob
        if len(keypoints) > 0:
            largest_blob = max(keypoints, key=lambda x: x.size)
            x, y = largest_blob.pt

            final = coordinate_system.transform(np.array([x, y]))

            # Print the coordinates of the largest blob before and after
            print(f"Before: ({x}, {y})")
            print(f"After: ({final[0]}, {final[1]})")
        else:
            print("None")

        # Break the loop when 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the capture and close all OpenCV windows
    cap.release()
    # cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
