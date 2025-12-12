import sys
import os
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication

import config
from main_window import MainWindow

def setup_environment():
    """프로그램 실행에 필요한 폴더와 샘플 파일을 생성합니다."""
    config.DATA_DIR.mkdir(exist_ok=True)
    config.CAPTURE_DIR.mkdir(exist_ok=True)
    config.RESULT_DIR.mkdir(exist_ok=True)
    config.RESOURCES_DIR.mkdir(exist_ok=True)
    config.SAMPLE_IMAGE_DIR.mkdir(exist_ok=True)

    # 샘플 이미지가 없으면 생성
    front_sample_path = config.SAMPLE_IMAGE_DIR / "sample_front.png"
    back_sample_path = config.SAMPLE_IMAGE_DIR / "sample_back.png"

    if not front_sample_path.exists():
        dummy_image = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(dummy_image, "Sample Front Image", (150, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.imwrite(str(front_sample_path), dummy_image)

    if not back_sample_path.exists():
        dummy_image = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(dummy_image, "Sample Back Image", (160, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.imwrite(str(back_sample_path), dummy_image)

if __name__ == "__main__":
    setup_environment()
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())