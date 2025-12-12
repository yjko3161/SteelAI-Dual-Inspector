import sys
import os
import cv2
import numpy as np
import config
from PyQt5.QtWidgets import QApplication
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
    
    # Fix for Qt platform plugin "windows" not found error
    import PyQt5
    pkg_path = os.path.dirname(PyQt5.__file__)
    # Try typical paths for plugins
    plugin_path = os.path.join(pkg_path, "Qt5", "plugins")
    if not os.path.exists(plugin_path):
        # Fallback for some installations
        plugin_path = os.path.join(pkg_path, "Qt", "plugins")
    
    os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = plugin_path
    print(f"Setting QT_QPA_PLATFORM_PLUGIN_PATH to: {plugin_path}")

    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())