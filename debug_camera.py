import cv2
from camera_manager import CameraManager

print("Testing CameraManager.get_available_cameras()...")
try:
    cameras = CameraManager.get_available_cameras()
    print(f"Found cameras: {cameras}")
except Exception as e:
    print(f"Error: {e}")

print("\nDetailed check:")
for i in range(5):
    cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
    opened = cap.isOpened()
    print(f"Index {i}: CAP_DSHOW isOpened={opened}")
    cap.release()
    
    cap2 = cv2.VideoCapture(i)
    opened2 = cap2.isOpened()
    print(f"Index {i}: Default backend isOpened={opened2}")
    cap2.release()
