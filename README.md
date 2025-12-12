# SteelAI-Dual-Inspector
A dual-camera desktop inspection system for automated steel surface defect detection and real-world size measurement.

SteelVision Dual은 듀얼 카메라 기반으로 철판 표면의 스크래치·핀홀 등 결함을 자동 검출하고,
픽셀 보정값을 이용해 실제 결함 크기를 mm 단위로 산출하는 산업용 비전 검사 프로그램입니다.

- Dual camera capture (Front/Back)
- Scratch / Hole automatic detection (AI-ready structure)
- Pixel-to-mm measurement (length, width, diameter, area)
- PyQt5 기반 데스크톱 애플리케이션
- 실시간 미리보기, 오버레이, CSV 리포트 저장

## 🛠️ 설치 방법 (Installation)

1.  **저장소 복제 (Clone the repository)**
    ```bash
    git clone https://github.com/your-username/SteelAI-Dual-Inspector.git
    cd SteelAI-Dual-Inspector
    ```

2.  **가상 환경 생성 및 활성화 (Create and activate a virtual environment)**
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **의존성 설치 (Install dependencies)**
    ```bash
    pip install -r requirements.txt
    ```

## ▶️ 실행 방법 (How to Run)

애플리케이션을 실행하려면 다음 명령어를 입력하세요.

```bash
python main.py
```