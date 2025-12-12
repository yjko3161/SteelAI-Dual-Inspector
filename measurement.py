import math

def pixels_to_mm(px: float, pixels_per_mm: float) -> float:
    """픽셀 단위를 실제 mm 단위로 변환합니다."""
    if pixels_per_mm == 0:
        return 0.0
    return px / pixels_per_mm

def measure_scratch(bbox: tuple, pixels_per_mm: float) -> float:
    """
    스크래치 결함의 길이를 mm 단위로 측정합니다.
    bbox의 너비와 높이 중 더 긴 쪽을 길이로 간주합니다.
    """
    _x, _y, w, h = bbox
    length_px = max(w, h)
    length_mm = pixels_to_mm(length_px, pixels_per_mm)
    return length_mm

def measure_hole(bbox: tuple, pixels_per_mm: float) -> tuple[float, float]:
    """
    원형 홀 결함의 지름과 면적을 mm 단위로 측정합니다.
    지름은 너비와 높이의 평균으로 계산합니다.
    """
    _x, _y, w, h = bbox
    diameter_px = (w + h) / 2
    diameter_mm = pixels_to_mm(diameter_px, pixels_per_mm)
    area_mm2 = math.pi * (diameter_mm / 2) ** 2
    return diameter_mm, area_mm2