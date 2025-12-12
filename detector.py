import numpy as np
import torch
from ultralytics import YOLO
from defect import Defect
import measurement
import config

class DefectDetector:
    """
    이미지에서 결함을 검출하는 클래스.
    YOLO 모델을 사용하여 실제 결함을 검출합니다.
    """
    def __init__(self, config_data: dict):
        self.config = config_data
        self.model = None
        self.device = 'cpu'
        self.confidence_threshold = self.config.get('confidence_threshold', 0.5)
        
        # 모델 파일 경로 설정 (models/best.pt 우선, 없으면 yolov8n.pt)
        model_path = config.MODELS_DIR / "best.pt"
        try:
            if model_path.exists():
                self.model = YOLO(str(model_path))
                print(f"Loaded custom model: {model_path}")
            else:
                print("Custom model not found. Loading YOLOv8n (nano) model...")
                self.model = YOLO("yolov8n.pt")
            
            # GPU 사용 가능 여부 확인
            if torch.cuda.is_available():
                self.device = 'cuda'
                print("CUDA available: Using GPU for inference.")
            else:
                print("CUDA not available: Using CPU for inference.")
        except Exception as e:
            print(f"Error loading YOLO model: {e}")

    def detect(self, image: np.ndarray, camera_name: str) -> list[Defect]:
        """
        이미지에서 결함을 검출하고, 각 결함의 크기를 계산하여 리스트로 반환합니다.
        """
        if self.model is None or image is None:
            return []

        defects = []
        pixels_per_mm = self.config[camera_name.lower()]['pixels_per_mm']

        # YOLO 추론
        results = self.model(image, verbose=False, device=self.device)

        for result in results:
            for box in result.boxes:
                # Bounding Box
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                w, h = x2 - x1, y2 - y1
                bbox = (int(x1), int(y1), int(w), int(h))
                
                # Class & Confidence
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])

                # 신뢰도 임계값(Confidence Threshold) 필터링
                if conf < self.confidence_threshold:
                    continue

                label = result.names[cls_id].lower()

                # 결함 유형 매핑
                if 'scratch' in label or 'crack' in label:
                    defect_type = 'crack'
                elif 'hole' in label:
                    defect_type = 'hole'
                elif 'nut' in label:
                    defect_type = 'nut'
                else:
                    defect_type = label # 기타

                # 초기화
                status = "OK"
                length_mm = None
                diameter_mm = None
                area_mm2 = None

                # 유형별 측정 및 판정 로직
                if defect_type == "crack":
                    length_mm = measurement.measure_scratch(bbox, pixels_per_mm)
                    if length_mm <= config.CRACK_LIMIT_OK:
                        status = "OK"
                    elif length_mm < config.CRACK_LIMIT_WARNING:
                        status = "WARNING" # Rework
                    else:
                        status = "NG"
                    
                    defects.append(Defect(camera_name, defect_type, status, bbox, length_mm, None, None, None, conf))

                elif defect_type == "hole":
                    diameter_mm, area_mm2 = measurement.measure_hole(bbox, pixels_per_mm)
                    if diameter_mm >= config.HOLE_LIMIT_NG:
                        status = "NG"
                    else:
                        status = "OK"
                    
                    defects.append(Defect(camera_name, defect_type, status, bbox, None, None, diameter_mm, area_mm2, conf))
                
                elif defect_type == "nut":
                    # 너트가 검출되면 OK로 간주
                    status = "OK"
                    defects.append(Defect(camera_name, defect_type, status, bbox, None, None, None, None, conf))
                
                else:
                    # 기타 검출된 객체
                    defects.append(Defect(camera_name, defect_type, "WARNING", bbox, None, None, None, None, conf))
        
        return defects