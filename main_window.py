import sys
import cv2
import numpy as np
import csv
import random
from datetime import datetime
from pathlib import Path

from PyQt5.QtWidgets import (QMainWindow, QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QComboBox, QTableWidget, QTableWidgetItem,
                             QMessageBox, QGridLayout, QGroupBox, QHeaderView, QAction, QFileDialog,
                             QRadioButton, QButtonGroup, QSplitter, QTabWidget)
from PyQt5.QtGui import QPixmap, QImage, QFont, QColor
from PyQt5.QtCore import Qt, QTimer

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import config
from camera_manager import CameraManager
from detector import DefectDetector
from settings_dialog import SettingsDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.app_config = config.load_config()
        self.camera_manager = CameraManager()
        self.detector = DefectDetector(self.app_config)

        self.img_front = None
        self.img_back = None
        self.defects = []
        self.env_data = {"temp": 0, "humid": 0, "dust": 0}
        self.history_cracks = [] # 트렌드 차트용 데이터
        self.defect_counts = {"crack": 0, "hole": 0, "nut": 0} # 파이 차트용

        # Matplotlib 한글 폰트 설정 (Windows 기준)
        plt.rcParams['font.family'] = 'Malgun Gothic'

        self.preview_timer = QTimer(self)
        self.preview_timer.timeout.connect(self._update_previews)

        self._init_ui()
        
        # FR-AutoConnect: 3초 후 카메라 자동 연결 시도
        QTimer.singleShot(3000, self._connect_cameras)

    def _init_ui(self):
        self.setWindowTitle("SteelAI-Dual Inspector")
        # self.showFullScreen() <- Removed from here

        # --- 메뉴바 설정 ---
        menubar = self.menuBar()
        
        # 시스템 메뉴 (종료 등)
        sys_menu = menubar.addMenu('시스템')
        exit_action = QAction('종료', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self._exit_program)
        sys_menu.addAction(exit_action)

        # 설정 메뉴
        settings_menu = menubar.addMenu('설정')
        cam_setting_action = QAction('카메라 설정', self)
        cam_setting_action.triggered.connect(self._open_settings)
        settings_menu.addAction(cam_setting_action)

        # --- 레이아웃 설정 ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # 3-Pane Layout (Left, Center, Right)
        content_layout = QHBoxLayout()
        main_layout.addLayout(content_layout)

        # [Zone 1] 좌측: 제어 및 로그
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_panel.setFixedWidth(350)
        
        # 1-1. 공정 선택
        process_group = QGroupBox("공정 선택")
        process_layout = QHBoxLayout(process_group)
        self.rb_press = QRadioButton("프레스 공정")
        self.rb_weld = QRadioButton("용접 공정")
        self.rb_press.setChecked(True)
        process_layout.addWidget(self.rb_press)
        process_layout.addWidget(self.rb_weld)
        left_layout.addWidget(process_group)

        # 1-2. 환경 정보
        env_group = QGroupBox("환경 센서 정보")
        env_layout = QGridLayout(env_group)
        self.lbl_temp = QLabel("온도: - °C")
        self.lbl_humid = QLabel("습도: - %")
        self.lbl_dust = QLabel("미세먼지: - µg/m³")
        env_layout.addWidget(self.lbl_temp, 0, 0)
        env_layout.addWidget(self.lbl_humid, 1, 0)
        env_layout.addWidget(self.lbl_dust, 2, 0)
        left_layout.addWidget(env_group)

        # 1-3. 실시간 로그
        log_group = QGroupBox("실시간 검사 로그")
        log_layout = QVBoxLayout(log_group)
        self.log_table = QTableWidget()
        self.log_table.setColumnCount(4)
        self.log_table.setHorizontalHeaderLabels(["시간", "ID", "판정", "내용"])
        self.log_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.log_table.verticalHeader().setVisible(False)
        log_layout.addWidget(self.log_table)
        left_layout.addWidget(log_group)

        left_layout.addWidget(log_group)

        content_layout.addWidget(left_panel)

        # [Zone 2] 중앙: 2채널 영상 모니터링
        center_panel = QWidget()
        center_layout = QVBoxLayout(center_panel)
        
        self.front_view = QLabel("FRONT 카메라 프리뷰")
        self.back_view = QLabel("BACK 카메라 프리뷰")
        self.front_view.setAlignment(Qt.AlignCenter)
        self.back_view.setAlignment(Qt.AlignCenter)
        self.front_view.setStyleSheet("background-color: #333; color: white;")
        self.back_view.setStyleSheet("background-color: #333; color: white;")
        
        # 화면 분할 (상/하 대신 편의상 좌/우 유지하되 크기 조정)
        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(self.front_view)
        splitter.addWidget(self.back_view)
        center_layout.addWidget(splitter)
        
        content_layout.addWidget(center_panel, stretch=1)

        # [Zone 3] 우측: 탭 인터페이스 (검사 / 대시보드)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_panel.setFixedWidth(400)

        tabs = QTabWidget()
        right_layout.addWidget(tabs)

        # Tab 1: 검사 (Inspection)
        tab_inspection = QWidget()
        inspect_layout = QVBoxLayout(tab_inspection)
        
        # 1-1. 최종 판정 결과 (Result) - Font Size increased (32 -> 64)
        result_group = QGroupBox("최종 판정 (Result)")
        result_layout = QVBoxLayout(result_group)
        self.lbl_final_result = QLabel("READY")
        self.lbl_final_result.setAlignment(Qt.AlignCenter)
        self.lbl_final_result.setFont(QFont("Arial", 64, QFont.Bold))
        self.lbl_final_result.setStyleSheet("color: gray; border: 2px solid gray;")
        self.lbl_final_result.setMinimumHeight(150) # Ensure enough space
        result_layout.addWidget(self.lbl_final_result)
        inspect_layout.addWidget(result_group)

        # 1-2. 검사 제어 버튼 (Inspect Only) - Size increased (60 -> 120)
        btn_group = QGroupBox("검사 제어")
        btn_layout = QVBoxLayout(btn_group)
        
        self.inspect_btn = QPushButton("검사 실행 (Inspect)")
        self.inspect_btn.clicked.connect(self._run_inspection)
        self.inspect_btn.setMinimumHeight(120)
        self.inspect_btn.setStyleSheet("font-weight: bold; font-size: 20px; background-color: #2196F3; color: white;")
        
        btn_layout.addWidget(self.inspect_btn)
        inspect_layout.addWidget(btn_group)
        
        # 1-3. 시스템 제어 (System Control) - New location for Connect, Capture, Resume
        sys_group = QGroupBox("시스템 제어")
        sys_layout = QVBoxLayout(sys_group)
        
        self.connect_btn = QPushButton("카메라 연결")
        self.connect_btn.clicked.connect(self._connect_cameras)
        self.connect_btn.setMinimumHeight(40)

        self.capture_btn = QPushButton("촬영 (Capture)")
        self.capture_btn.clicked.connect(self._capture_images)
        self.capture_btn.setMinimumHeight(40)
        
        self.resume_btn = QPushButton("프리뷰 재개")
        self.resume_btn.clicked.connect(self._resume_preview)
        self.resume_btn.setMinimumHeight(40)
        
        sys_layout.addWidget(self.connect_btn)
        sys_layout.addWidget(self.capture_btn)
        sys_layout.addWidget(self.resume_btn)
        
        inspect_layout.addWidget(sys_group)
        
        inspect_layout.addStretch() # 상단 정렬
        
        tabs.addTab(tab_inspection, "검사")

        # Tab 2: 분석 대시보드 (Dashboard)
        tab_dashboard = QWidget()
        dash_layout = QVBoxLayout(tab_dashboard)

        chart_group = QGroupBox("분석 차트")
        chart_layout = QVBoxLayout(chart_group)
        
        self.figure = Figure(figsize=(4, 6), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.ax1 = self.figure.add_subplot(211) # Trend
        self.ax2 = self.figure.add_subplot(212) # Pie
        self.figure.tight_layout()
        
        chart_layout.addWidget(self.canvas)
        dash_layout.addWidget(chart_group)
        
        tabs.addTab(tab_dashboard, "대시보드")

        content_layout.addWidget(right_panel)

        # 초기 차트 그리기
        self._update_charts()
        
        self.showFullScreen() # Kiosk Mode (Full Screen) - Moved here to ensure widgets exist

    def _exit_program(self):
        """프로그램 종료 시 확인 대화상자를 띄웁니다."""
        reply = QMessageBox.question(self, '종료 확인', 
                                     "프로그램을 종료하시겠습니까?", 
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.close()

    def _open_settings(self):
        """설정 다이얼로그를 엽니다."""
        # 설정을 열기 전에 카메라 자원을 해제해야 검색이 가능함
        if self.preview_timer.isActive():
            self.preview_timer.stop()
        self.camera_manager.close()

        dlg = SettingsDialog(self.app_config, self)
        if dlg.exec_():
            self.app_config = dlg.get_settings()
            config.save_config(self.app_config)
            self.detector = DefectDetector(self.app_config) # 설정 변경 시 디텍터(픽셀값 등) 업데이트
            QMessageBox.information(self, "설정 저장", "설정이 저장되었습니다. 카메라를 재연결해주세요.")

    def _connect_cameras(self):
        if self.camera_manager.open(self.app_config['front'], self.app_config['back']):
            self.preview_timer.start(30) # 30ms 간격으로 프리뷰 업데이트
            QMessageBox.information(self, "성공", "카메라가 성공적으로 연결되었습니다.")
        else:
            QMessageBox.warning(self, "실패", "카메라 연결 실패. [촬영] 버튼을 눌러 샘플 모드로 진행하세요.")

    def _update_environment(self):
        """환경 센서 데이터 시뮬레이션"""
        self.env_data['temp'] = round(random.uniform(20.0, 30.0), 1)
        self.env_data['humid'] = round(random.uniform(40.0, 60.0), 1)
        self.env_data['dust'] = int(random.uniform(10, 80))
        
        self.lbl_temp.setText(f"온도: {self.env_data['temp']} °C")
        self.lbl_humid.setText(f"습도: {self.env_data['humid']} %")
        self.lbl_dust.setText(f"미세먼지: {self.env_data['dust']} µg/m³")

    def _update_previews(self):
        img_f, img_b = self.camera_manager.capture_both()
        if img_f is not None:
            self._display_image(img_f, self.front_view)
        if img_b is not None:
            self._display_image(img_b, self.back_view)
        
        # 환경 정보도 주기적으로 업데이트 (실제로는 센서 주기 따름)
        self._update_environment()

    def _capture_images(self):
        self.preview_timer.stop()
        img_f, img_b = self.camera_manager.capture_both()

        # 카메라 캡처 실패 시 샘플 이미지 로드 (Fallback)
        if img_f is None or img_b is None:
            QMessageBox.information(self, "정보", "카메라 캡처에 실패하여 샘플 이미지로 대체합니다.")
            front_path = config.SAMPLE_IMAGE_DIR / "sample_front.png"
            back_path = config.SAMPLE_IMAGE_DIR / "sample_back.png"
            if not front_path.exists() or not back_path.exists():
                 QMessageBox.critical(self, "오류", f"샘플 이미지를 찾을 수 없습니다: {front_path}")
                 return
            img_f = cv2.imread(str(front_path))
            img_b = cv2.imread(str(back_path))

        self.img_front = img_f
        self.img_back = img_b
        self._display_image(self.img_front, self.front_view)
        self._display_image(self.img_back, self.back_view)
        self.defects = []

        # 자동 저장 (설정된 경로 사용)
        save_dir = self.app_config.get('save_path', str(config.CAPTURE_DIR))
        save_path = Path(save_dir)
        save_path.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        try:
            cv2.imwrite(str(save_path / f"capture_front_{timestamp}.png"), self.img_front)
            cv2.imwrite(str(save_path / f"capture_back_{timestamp}.png"), self.img_back)
            self.statusBar().showMessage(f"이미지 저장 완료: {save_path}", 3000)
        except Exception as e:
            QMessageBox.critical(self, "저장 실패", f"이미지 저장 중 오류가 발생했습니다:\n{e}")

        # 촬영 및 저장 후 프리뷰 자동 재개
        self.preview_timer.start(30)

    def _resume_preview(self):
        """프리뷰를 다시 시작합니다."""
        if not self.preview_timer.isActive():
            self.preview_timer.start(30)

    def _run_inspection(self):
        # FR-01: 검사 실행 버튼 클릭 시 자동 촬영
        # 프리뷰가 활성화되어 있다면 일시 정지
        if self.preview_timer.isActive():
            self.preview_timer.stop()

        # FR-09: 상태 전환 (PROCESSING...)
        self.lbl_final_result.setText("PROCESSING...")
        self.lbl_final_result.setStyleSheet("color: gray; border: 2px solid gray;")
        QApplication.processEvents() # UI 갱신 강제 (로딩 효과)

        # FR-02: 자동 촬영 (Auto Capture)
        img_f, img_b = self.camera_manager.capture_both()

        # SR-03: 오류 처리 (카메라 캡처 실패)
        if img_f is None or img_b is None:
            # 테스트를 위해 샘플 이미지 로드 (Fallback)
            front_path = config.SAMPLE_IMAGE_DIR / "sample_front.png"
            back_path = config.SAMPLE_IMAGE_DIR / "sample_back.png"
            if front_path.exists() and back_path.exists():
                img_f = cv2.imread(str(front_path))
                img_b = cv2.imread(str(back_path))
            else:
                self.lbl_final_result.setText("ERROR")
                QMessageBox.critical(self, "오류", "카메라 캡처 실패")
                return

        self.img_front = img_f
        self.img_back = img_b

        # FR-03: YOLO 분석 모듈 연동
        try:
            front_defects = self.detector.detect(self.img_front, "FRONT")
            back_defects = self.detector.detect(self.img_back, "BACK")
            self.defects = front_defects + back_defects
        except Exception as e:
            self.lbl_final_result.setText("AI ERROR")
            QMessageBox.critical(self, "오류", f"AI 분석 실패: {e}")
            return

        # FR-07: 최종 판정 논리 (PASS / NG)
        # 하나라도 NG 또는 WARNING(Rework) 상태의 결함이 있으면 NG로 판정
        final_status = "PASS"
        if any(d.status in ["NG", "WARNING"] for d in self.defects):
            final_status = "NG"

        # FR-05, FR-06: 결과 시각화 (Overlay)
        self._draw_overlays()

        # FR-08: 최종 판정 출력
        self._update_result_label(final_status)
        self._update_log(final_status, self.defects[0] if self.defects else None)
        self._update_charts()

    def _update_log(self, status, defect):
        """좌측 로그 테이블 업데이트"""
        row = self.log_table.rowCount()
        self.log_table.insertRow(row)
        
        time_str = datetime.now().strftime("%H:%M:%S")
        part_id = f"P-{random.randint(1000, 9999)}" # 임시 ID
        
        desc = "-"
        if defect:
            if defect.defect_type == "crack":
                desc = f"Crack {defect.length_mm:.1f}mm"
            elif defect.defect_type == "hole":
                desc = f"Hole Ø{defect.diameter_mm:.1f}mm"
            elif defect.defect_type == "nut":
                desc = "Nut Missing"

        self.log_table.setItem(row, 0, QTableWidgetItem(time_str))
        self.log_table.setItem(row, 1, QTableWidgetItem(part_id))
        self.log_table.setItem(row, 2, QTableWidgetItem(status))
        self.log_table.setItem(row, 3, QTableWidgetItem(desc))
        self.log_table.scrollToBottom()

    def _update_result_label(self, status):
        """우측 하단 최종 판정 라벨 업데이트"""
        self.lbl_final_result.setText(status)
        if status == "PASS":
            self.lbl_final_result.setStyleSheet("color: white; background-color: #4CAF50; border: 2px solid #4CAF50;") # Green
        else: # NG (WARNING 포함)
            self.lbl_final_result.setStyleSheet("color: white; background-color: #F44336; border: 2px solid #F44336;") # Red

    def _update_charts(self):
        """Matplotlib 차트 업데이트"""
        self.ax1.clear()
        self.ax2.clear()

        # Trend Chart
        self.ax1.set_title("Crack Length Trend (Recent 20)")
        self.ax1.plot(self.history_cracks, marker='o', linestyle='-')
        self.ax1.set_ylabel("Length (mm)")
        self.ax1.grid(True)

        # Pie Chart
        labels = list(self.defect_counts.keys())
        sizes = list(self.defect_counts.values())
        if sum(sizes) > 0:
            self.ax2.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
            self.ax2.set_title("Defect Share")
        
        self.canvas.draw()

    def _draw_overlays(self):
        overlay_front = self.img_front.copy()
        overlay_back = self.img_back.copy()

        for defect in self.defects:
            img_to_draw = overlay_front if defect.camera == "FRONT" else overlay_back
            x, y, w, h = defect.bbox
            
            # 색상 결정 (BGR)
            if defect.status == "OK":
                color = (0, 255, 0) # Green
            elif defect.status == "WARNING":
                color = (0, 165, 255) # Orange (OpenCV BGR: Orange is roughly 0, 165, 255)
            else:
                color = (0, 0, 255) # Red

            cv2.rectangle(img_to_draw, (x, y), (x + w, y + h), color, 2)

            # 결함 정보 텍스트 추가
            label_text = defect.defect_type.upper()
            if defect.defect_type == "crack":
                label_text += f" {defect.length_mm:.1f}mm"
            elif defect.defect_type == "hole":
                label_text += f" D:{defect.diameter_mm:.1f}mm"
            elif defect.defect_type == "nut":
                label_text = "NUT MISSING"
                cv2.line(img_to_draw, (x, y), (x+w, y+h), color, 2) # X 표시
                cv2.line(img_to_draw, (x+w, y), (x, y+h), color, 2)
            
            cv2.putText(img_to_draw, label_text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        self._display_image(overlay_front, self.front_view)
        self._display_image(overlay_back, self.back_view)

    def _save_results(self):
        if not self.defects:
            QMessageBox.warning(self, "경고", "저장할 검사 결과가 없습니다.")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_folder = config.RESULT_DIR / timestamp
        capture_folder = config.CAPTURE_DIR / timestamp
        result_folder.mkdir(parents=True, exist_ok=True)
        capture_folder.mkdir(parents=True, exist_ok=True)

        # 원본 이미지 저장
        cv2.imwrite(str(capture_folder / "original_front.png"), self.img_front)
        cv2.imwrite(str(capture_folder / "original_back.png"), self.img_back)

        # 오버레이 이미지 저장
        overlay_front = self.front_view.pixmap().toImage()
        overlay_back = self.back_view.pixmap().toImage()
        overlay_front.save(str(result_folder / "overlay_front.png"))
        overlay_back.save(str(result_folder / "overlay_back.png"))

        # CSV 결과 저장
        csv_path = result_folder / "report.csv"
        try:
            with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                # 헤더에 환경 정보 추가
                header = ["Camera", "Type", "Status", "Value(mm)", "Temp", "Humid", "Dust"]
                writer.writerow(header)

                for defect in self.defects:
                    val = ""
                    if defect.length_mm: val = f"{defect.length_mm:.2f}"
                    elif defect.diameter_mm: val = f"{defect.diameter_mm:.2f}"
                    
                    writer.writerow([
                        defect.camera,
                        defect.defect_type,
                        defect.status,
                        val,
                        self.env_data['temp'], self.env_data['humid'], self.env_data['dust']
                    ])
            QMessageBox.information(self, "성공", f"결과가 다음 위치에 저장되었습니다:\n{result_folder}")
        except Exception as e:
            QMessageBox.critical(self, "오류", f"CSV 파일 저장 중 오류 발생:\n{e}")

    def resizeEvent(self, event):
        """창 크기 변경 시 이미지도 다시 스케일링하여 표시"""
        super().resizeEvent(event)
        # 현재 표시된 pixmap이 있다면, 그것을 기준으로 다시 스케일링
        if self.front_view.pixmap() and not self.front_view.pixmap().isNull():
            original_pixmap = self.front_view.property("original_pixmap")
            if original_pixmap:
                 self.front_view.setPixmap(original_pixmap.scaled(self.front_view.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

        if self.back_view.pixmap() and not self.back_view.pixmap().isNull():
            original_pixmap = self.back_view.property("original_pixmap")
            if original_pixmap:
                self.back_view.setPixmap(original_pixmap.scaled(self.back_view.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def _display_image(self, img: np.ndarray, label: QLabel):
        """OpenCV 이미지를 QLabel에 표시하고, 원본 QPixmap을 저장합니다."""
        if img is None:
            label.setText(f"{label.objectName()} 비어 있음")
            return

        h, w, ch = img.shape
        bytes_per_line = ch * w
        rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        q_img = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        
        pixmap = QPixmap.fromImage(q_img)
        label.setProperty("original_pixmap", pixmap) # 원본 저장
        label.setPixmap(pixmap.scaled(label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))


    def closeEvent(self, event):
        """애플리케이션 종료 시 카메라 자원 해제"""
        self.camera_manager.close()
        event.accept()