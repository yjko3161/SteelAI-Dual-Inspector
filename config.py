import json
from pathlib import Path

# 기본 경로 설정
BASE_DIR = Path(__file__).resolve().parent

# 주요 디렉토리 경로
UI_DIR = BASE_DIR / "ui"
MODELS_DIR = BASE_DIR / "models"
RESOURCES_DIR = BASE_DIR / "resources"
SAMPLE_IMAGE_DIR = RESOURCES_DIR / "sample_images"
DATA_DIR = BASE_DIR / "data"
CAPTURE_DIR = DATA_DIR / "captures"
RESULT_DIR = DATA_DIR / "results"

# 설정 파일 경로
CONFIG_FILE = BASE_DIR / "config.json"

# 검사 기준값 (Thresholds)
CRACK_LIMIT_OK = 3.0      # 3mm 이하 OK
CRACK_LIMIT_WARNING = 7.0 # 3mm 초과 ~ 7mm 미만 Warning (Rework)
HOLE_LIMIT_NG = 5.0       # 5mm 이상 NG
NUT_SIZE_MIN = 10.0       # 너트 최소 크기

def load_config() -> dict:
    """config.json 파일에서 설정을 불러옵니다."""
    default_config = {
        "front": {"type": "USB", "address": 0, "pixels_per_mm": 10.0},
        "back": {"type": "USB", "address": 1, "pixels_per_mm": 10.0},
        "save_path": str(CAPTURE_DIR)
    }

    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            loaded_config = json.load(f)
            default_config.update(loaded_config)
            return default_config
    
    return default_config

def save_config(config_data: dict):
    """설정을 config.json 파일에 저장합니다."""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, indent=4, ensure_ascii=False)