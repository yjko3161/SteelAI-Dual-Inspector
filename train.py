from ultralytics import YOLO

def train():
    # 1. 모델 선택
    # v8n (Nano): 가장 빠름, 가벼움 (테스트용 추천)
    # v8s (Small) / v8m (Medium): 성능과 속도 균형 (논문용 추천)
    model = YOLO('yolov8n.pt') 

    # 2. 학습 시작
    results = model.train(
        data='data.yaml',   # 위에서 만든 설정 파일
        epochs=100,         # 100번 반복 학습 (조기 종료 기능 자동 작동함)
        imgsz=640,          # 이미지 크기 (철판 결함은 디테일이 중요하면 1024로 늘려도 됨)
        batch=16,           # GPU 메모리 터지면 8로 줄이세요
        device=0,           # GPU 번호 (없으면 'cpu', 맥은 'mps')
        workers=4,          # 데이터 로딩 속도
        name='steel_defect_result', # 결과 저장 폴더 이름
        exist_ok=True,      # 덮어쓰기 허용
        patience=20         # 성능 향상 없으면 20 epoch 후 자동 종료 (시간 절약)
    )

if __name__ == '__main__':
    train()