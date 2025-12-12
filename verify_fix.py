import cv2
from camera_manager import CameraManager

# Simulate conflict
print("Simulating conflict: Opening camera 0...")
cam0 = cv2.VideoCapture(0, cv2.CAP_DSHOW)
if cam0.isOpened():
    print("Camera 0 is OPEN.")
else:
    print("Could not open Camera 0 (might not exist or busy).")

print("\nTrying to search for cameras WHILE camera 0 is open (should find fewer or none if exclusive)...")
found = CameraManager.get_available_cameras()
print(f"Cameras found during conflict: {found}")

print("\nReleasing Camera 0...")
cam0.release()

print("\nTrying to search after release (should find camera 0)...")
found_after = CameraManager.get_available_cameras()
print(f"Cameras found after release: {found_after}")
