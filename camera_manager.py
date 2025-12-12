import cv2
import numpy as np

class CameraManager:
    """두 개의 USB 카메라를 관리하는 클래스"""
    def __init__(self):
        self.cam_front = None
        self.cam_back = None

    def open(self, front_config: dict, back_config: dict) -> bool:
        """설정값(USB/RTSP)에 따라 두 카메라를 엽니다."""
        self.close()  # 기존 연결이 있다면 해제

        def _open_cam(cfg):
            src_type = cfg.get('type', 'USB')
            address = cfg.get('address', 0)
            
            if src_type == 'USB':
                # USB 카메라는 DirectShow(Windows) 사용 권장
                return cv2.VideoCapture(int(address), cv2.CAP_DSHOW)
            else:
                # RTSP 등 네트워크 스트림
                return cv2.VideoCapture(str(address))

        self.cam_front = _open_cam(front_config)
        self.cam_back = _open_cam(back_config)

        if not self.cam_front.isOpened() or not self.cam_back.isOpened():
            self.close()
            return False
        return True

    def close(self):
        """열려있는 모든 카메라를 해제합니다."""
        if self.cam_front:
            self.cam_front.release()
            self.cam_front = None
        if self.cam_back:
            self.cam_back.release()
            self.cam_back = None

    def capture_both(self) -> tuple[np.ndarray | None, np.ndarray | None]:
        """두 카메라에서 동시에 프레임을 캡처합니다."""
        if not self.cam_front or not self.cam_back or \
           not self.cam_front.isOpened() or not self.cam_back.isOpened():
            return None, None

        ret1, frame1 = self.cam_front.read()
        ret2, frame2 = self.cam_back.read()

        return frame1 if ret1 else None, frame2 if ret2 else None