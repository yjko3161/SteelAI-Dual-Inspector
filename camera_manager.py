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
                idx = int(address)
                # Fallback Strategy: DSHOW -> MSMF -> ANY
                backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]
                for backend in backends:
                    cap = cv2.VideoCapture(idx, backend)
                    if cap.isOpened():
                        print(f"Camera {idx} opened with backend {backend}")
                        return cap
                    cap.release()
                print(f"Failed to open Camera {idx} with any backend.")
                return cv2.VideoCapture(idx) # Return closed capture as last resort
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

    @staticmethod
    def get_available_cameras(max_to_check: int = 10) -> list[int]:
        """
        0부터 max_to_check까지 순회하며 열리는 카메라 인덱스 리스트를 반환합니다.
        DSHOW 등 특정 백엔드 강제보다 기본값(ANY)으로 검색하여 호환성을 높입니다.
        """
        available_indices = []
        for i in range(max_to_check):
            # 검색 시에는 CAP_DSHOW 강제보다는 ANY(자동) 혹은 MSMF/DSHOW 순차 시도가 안전할 수 있음.
            # 하지만 간단히 CAP_ANY(0)로 시도하여 열리는지 확인.
            cap = cv2.VideoCapture(i) 
            if cap.isOpened():
                available_indices.append(i)
                cap.release()
        return available_indices