from dataclasses import dataclass

@dataclass
class Defect:
    """검출된 결함 정보를 저장하는 데이터 클래스"""
    camera: str              # "FRONT" or "BACK"
    defect_type: str         # "crack", "hole", "nut"
    status: str              # "OK", "WARNING", "NG"
    bbox: tuple              # (x, y, w, h) in px
    length_mm: float | None
    width_mm: float | None   # 향후 사용을 위해 남겨둠
    diameter_mm: float | None
    area_mm2: float | None
    score: float             # 신뢰도(0~1)