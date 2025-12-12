from ultralytics import YOLO
import torch

def train():
    # 0. GPU 확인
    if torch.cuda.is_available():
        print(f"🔥 GPU Connected: {torch.cuda.get_device_name(0)}")

    # 1. 모델 체급 업그레이드 (s -> m)
    # 5080이면 Medium(m)이나 Large(l) 정도는 써야 '돈 쓴 보람'이 있는 성능이 나옵니다.
    model = YOLO('yolov8m.pt') 

    # 2. 학습 시작
    results = model.train(
        data='data.yaml',   
        epochs=150,
        
        # === 5080 전용 튜닝 ===
        imgsz=1280,          # [중요] 해상도 2배 UP -> 미세한 스크래치/홀 검출력 떡상
        batch=64,            # [중요] 배치 뻥튀기 -> VRAM 점유율 높이고 학습 안정화
        workers=8,           # CPU 병렬 로딩
        
        device=0,
        cache=True,          # 램 캐싱 (속도 UP)
        amp=True,            # 혼합 정밀도 사용
        name='5080_high_res', # 결과 저장 폴더명
        exist_ok=True,
        patience=30          # 성능 정체 시 30에폭 기다려보고 종료
    )

if __name__ == '__main__':
    # 윈도우 멀티프로세싱 에러 방지 (필수)
    train()