# 🏭 SteelAI-Dual-Inspector

**Edge AIoT-based High-Precision Steel Surface Defect & Fastener Inspection System** (엣지 AIoT 기반 고정밀 철판 표면 결함 및 체결 부품 검사 시스템)

    

## 📖 프로젝트 개요 (Overview)

**SteelAI-Dual-Inspector**는 딥러닝(YOLO)과 컴퓨터 비전(OpenCV) 기술을 융합한 하이브리드 산업용 검사 솔루션입니다.
RTX 5080 기반의 고성능 학습 모델을 활용하여 \*\*철판 표면의 미세 결함(스크래치, 홀 등)\*\*과 **체결 부품(너트, 볼트)의 상태**를 실시간으로 탐지합니다. 단순 탐지를 넘어, 렌즈 왜곡 보정과 서브 픽셀 알고리즘을 통해 결함의 \*\*실제 물리적 크기(mm)\*\*를 정밀 측정하여 자동 불량 판정(NG/OK)을 수행합니다.

### 🎯 핵심 목표 (Objectives)

  * **고정밀 탐지:** YOLO11x 기반 mAP@50 95% 이상 달성.
  * **정량적 측정:** 픽셀-mm 변환을 통해 홀 지름(±0.1mm) 및 크랙 길pip list이(±0.5mm) 정밀 계측.
  * **실시간 처리:** RTX 5080 및 엣지 디바이스(Jetson Orin) 환경에서 60 FPS 이상의 처리 속도 확보.

-----

## 🚀 주요 기능 (Key Features)

### 1\. 철판 표면 결함 검사 (Surface Inspection)

  * **다중 클래스 탐지:** Scratches, Patches, Pitted Surface, Inclusions 등 6종 결함 분류.
  * **하이브리드 정밀 측정 (Hybrid Measurement):**
      * **홀(Hole):** 바운딩 박스 내 ROI 추출 → 윤곽선(Contour) 분석 → 외접원 지름 측정.
      * **스크래치(Scratch):** 회전된 사각형(Rotated Rect) 알고리즘으로 정확한 길이 및 폭 산출.
  * **자동 판정:** 측정된 치수가 임계값(Threshold)을 초과할 경우 즉시 'NG' 판정 및 알람.

### 2\. 체결 부품 검사 (Fastener Inspection)

  * **부품 인식:** Nut, Bolt, Washer의 존재 유무(Missing Parts) 실시간 판별.
  * **체결 상태 확인:** 정상 체결, 미체결, 오체결 상태 분류 (Option: 아이마킹 인식).

### 3\. 영상 전처리 및 시스템 (System & Pre-processing)

  * **Camera Calibration:** 체커보드 기반 렌즈 왜곡 보정(Undistort)으로 가장자리 측정 오차 최소화.
  * **GUI & Reporting:** PyQt5 기반 실시간 오버레이 UI, 검사 이력(결함 종류, 크기, 시간) CSV/DB 자동 로깅.

-----

## 🛠️ 기술 스택 (Tech Stack)

| 구분 | 상세 내용 |
| --- | --- |
| **Language** | Python 3.9+ |
| **AI Framework** | PyTorch (Ultralytics YOLO11x), CUDA 12.x, TensorRT |
| **Vision Lib** | OpenCV (Image Processing, Measurement) |
| **GUI** | PyQt5 (Desktop Application) |
| **Hardware** | **Training:** NVIDIA RTX 5080 (Local Workstation)<br>**Inference:** Jetson Orin / Industrial PC |
| **OS** | Windows 11 (Training), Ubuntu 22.04 (Inference) |

-----

## 💾 설치 방법 (Installation)

**1. 저장소 복제 (Clone the repository)**

```bash
git clone https://github.com/your-username/SteelAI-Dual-Inspector.git
cd SteelAI-Dual-Inspector
```

**2. 가상 환경 생성 (Virtual Environment)**

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate
```

**3. 의존성 설치 (Install Dependencies)**
*RTX 5080 사용 시 CUDA 지원 PyTorch 설치 권장*

```bash
# PyTorch (CUDA 12.x) 설치 예시
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# 나머지 라이브러리 설치
pip install -r requirements.txt
```

-----

## ▶️ 실행 방법 (Usage)

**애플리케이션 실행**

```bash
python main.py
```

**모델 학습 (Training Example)**

```bash
# RTX 5080 전용 고성능 학습 스크립트 실행
python train_5080.py
```

-----

## 📅 개발 로드맵 (Roadmap & To-Do)

본 프로젝트는 박사 학위 연구의 일환으로 단계별 고도화가 진행 중입니다.

### Phase 1: 데이터 확장 및 모델 최적화 (Current)

  - [ ] **데이터셋 확보:** Roboflow/Kaggle 활용 너트/볼트 데이터셋 구축 및 `data.yaml` 구성.
  - [ ] **멀티 모델 전략:** 표면 결함(Model A)과 부품 검사(Model B) 분리 학습 및 앙상블 적용.
  - [ ] **모델 고도화:** RTX 5080을 활용한 `YOLO11x` (Extra Large) 모델 도입 및 1280px 고해상도 학습.

### Phase 2: 정밀 측정 알고리즘 구현 (Core Research)

  - [ ] **카메라 캘리브레이션:** 체커보드 촬영 및 `cv2.undistort` 적용 (왜곡 계수 산출).
  - [ ] **픽셀-mm 변환 로직:** 참조 물체(Reference Object) 또는 고정 거리(Scale Factor) 방식 구현.
  - [ ] **하이브리드 측정 통합:** YOLO ROI 추출 + OpenCV 서브 픽셀 엣지 검출 알고리즘 결합.

### Phase 3: 시스템 통합 및 시각화

  - [ ] **로깅 시스템:** 검사 결과(결함 종류, 치수, 신뢰도) 자동 DB/CSV 저장.
  - [ ] **Rule-based 판정:** "지름 3mm 이상 불량" 등 사용자 정의 품질 기준 적용 로직.
  - [ ] **실시간 UI 고도화:** 웹캠 스트림 위 바운딩 박스 및 실측 치수(mm) 실시간 오버레이.

-----

## 📊 성능 목표 (Performance Goals)

  * **Detection Accuracy:** mAP@50 \> 95%
  * **Measurement Error:** Hole \< ±0.1mm, Crack \< ±0.5mm
  * **Inference Speed:** \> 60 FPS (on RTX 5080)

-----

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](https://www.google.com/search?q=LICENSE) file for details.

-----

### 📞 Contact

  * **Developer:** [Your Name]
  * **Email:** [Your Email]
  * **Institution:** [University/Lab Name]