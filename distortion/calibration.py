import cv2
import numpy as np
import argparse

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Camera calibration using a checkerboard pattern.")
parser.add_argument("video_path", type=str, help="Path to the video file for calibration.")
parser.add_argument("output_file", type=str, help="File to save the calibration results.")
args = parser.parse_args()

# Parameters
CHECKERBOARD = (5, 8)  # Dimensions of the checkerboard (internal corners)
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.01)

# Arrays to store object points and image points
objpoints = []  # 3D points in real-world space
imgpoints = []  # 2D points in image plane

# Prepare object points based on checkerboard size
objp = np.zeros((CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)

# Open the video file
cap = cv2.VideoCapture(args.video_path)

if not cap.isOpened():
    print(f"Error: Unable to open video {args.video_path}")
    exit()

frame_count = 0
success_count = 0

# Process video frames
while True:
    ret, frame = cap.read()
    if not ret:
        break  # End of video

    frame_count += 1

    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect the checkerboard corners
    ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, None)

    if ret:
        # Refine corner detection
        corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        imgpoints.append(corners2)
        objpoints.append(objp)

        # Draw the corners on the frame for visualization
        frame_with_corners = cv2.drawChessboardCorners(frame, CHECKERBOARD, corners, ret)
        # cv2.imshow("Checkerboard Detection", frame_with_corners)

        success_count += 1

        # Break early if enough frames are detected
        # if success_count >= 15:
        #     print("Sufficient frames for calibration.")
        #     break
    print(ret)

    # Show the frame (for debugging purposes)
    cv2.imshow("Video Frame", gray)
    if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to quit early
        break

cap.release()
cv2.destroyAllWindows()

if len(objpoints) < 10:
    print("Error: Not enough checkerboard detections for calibration. Ensure proper lighting and checkerboard visibility.")
    exit()
# Ensure object points have the correct data type
objpoints = [np.array(obj, dtype=np.float32) for obj in objpoints]

# Perform calibration
K = np.zeros((3, 3))
D = np.zeros((4, 1))
rvecs = []  # Rotation vectors
tvecs = []  # Translation vectors

objpoints = np.array(objpoints)

# Image size (must be consistent for all calibration images)
image_size = gray.shape[::-1]  # (width, height)

# Fisheye calibration parameters
K = np.zeros((3, 3))  # Intrinsic camera matrix
D = np.zeros((4, 1))  # Distortion coefficients

# Calibration
flags = (
    cv2.fisheye.CALIB_RECOMPUTE_EXTRINSIC +
    cv2.fisheye.CALIB_CHECK_COND +
    cv2.fisheye.CALIB_FIX_SKEW
)

ret, K, D, rvecs, tvecs = cv2.fisheye.calibrate(
    np.expand_dims(np.asarray(objpoints), -2),
    imgpoints,
    image_size,
    K,
    D,
    flags=flags,
    criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 1e-6)
)

# Print results
print("Calibration successful:", ret)
print("Camera Matrix (K):\n", K)
print("Distortion Coefficients (D):\n", D)

# Save the calibration data to a .npz file
np.savez(
    args.output_file,
    K=K,
    D=D,
    rvecs=rvecs,
    tvecs=tvecs,
    objpoints=objpoints,
    imgpoints=imgpoints,
)
print(f"Calibration data saved to {args.output_file}")

# show undistorted video
cap = cv2.VideoCapture(args.video_path)

while True:
    ret, frame = cap.read()
    if not ret:
        break  # End of video

    map1, map2 = cv2.fisheye.initUndistortRectifyMap(K, D, np.eye(3), K, frame.shape[:2][::-1], cv2.CV_16SC2)
    undistorted_img = cv2.remap(frame, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)

    # Show the frame
    cv2.imshow("Undistorted Video", undistorted_img)
    if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to quit early
        break