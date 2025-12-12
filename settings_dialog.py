from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QGroupBox, QComboBox, 
                             QLineEdit, QDialogButtonBox, QDoubleSpinBox, QFormLayout, QLabel,
                             QPushButton, QHBoxLayout, QFileDialog)
from camera_manager import CameraManager

class SettingsDialog(QDialog):
    def __init__(self, current_config, parent=None):
        super().__init__(parent)
        self.config = current_config
        self.setWindowTitle("카메라 및 시스템 설정")
        self.resize(400, 480) # Height increased
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        # General Settings (Save Path)
        self.general_widgets = self._create_general_group("일반 설정", self.config)
        layout.addWidget(self.general_widgets['group'])

        # Model Settings (YOLO Path)
        self.model_widgets = self._create_model_group("AI 모델 설정", self.config)
        layout.addWidget(self.model_widgets['group'])

        # Front Camera Settings
        self.front_widgets = self._create_cam_group("Front Camera", self.config.get('front', {}))
        layout.addWidget(self.front_widgets['group'])

        # Back Camera Settings
        self.back_widgets = self._create_cam_group("Back Camera", self.config.get('back', {}))
        layout.addWidget(self.back_widgets['group'])

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _create_general_group(self, title, config):
        group = QGroupBox(title)
        layout = QVBoxLayout(group)
        
        path_layout = QHBoxLayout()
        path_edit = QLineEdit(config.get('save_path', ''))
        path_edit.setReadOnly(True)
        browse_btn = QPushButton("경로 변경")
        
        def _browse_path():
            d = QFileDialog.getExistingDirectory(self, "저장 경로 선택", path_edit.text())
            if d: path_edit.setText(d)
            
        browse_btn.clicked.connect(_browse_path)
        path_layout.addWidget(path_edit)
        path_layout.addWidget(browse_btn)
        
        layout.addLayout(path_layout)
        return {'group': group, 'save_path': path_edit}

    def _create_model_group(self, title, config):
        group = QGroupBox(title)
        layout = QVBoxLayout(group)
        
        path_layout = QHBoxLayout()
        # Default fallback if key missing
        model_path = config.get('model_path', 'yolov8n.pt')
        path_edit = QLineEdit(model_path)
        path_edit.setReadOnly(True) 
        
        browse_btn = QPushButton("모델 찾기")
        
        def _browse_model():
            f, _ = QFileDialog.getOpenFileName(self, "YOLO 모델 선택", "", "YOLO Models (*.pt);;All Files (*)")
            if f: path_edit.setText(f)
            
        browse_btn.clicked.connect(_browse_model)
        path_layout.addWidget(path_edit)
        path_layout.addWidget(browse_btn)
        
        layout.addLayout(path_layout)
        return {'group': group, 'model_path': path_edit}

    def _create_cam_group(self, title, cam_config):
        group = QGroupBox(title)
        form = QFormLayout(group)
        
        type_combo = QComboBox()
        type_combo.addItems(["USB", "RTSP"])
        type_combo.setCurrentText(cam_config.get('type', 'USB'))
        
        # Address inputs
        address_layout = QHBoxLayout()
        
        # For RTSP: standard QLineEdit
        address_edit = QLineEdit(str(cam_config.get('address', 0)))
        
        # For USB: QComboBox + Search Button
        address_combo = QComboBox()
        address_combo.setEditable(True) 
        current_addr = cam_config.get('address', 0)
        address_combo.setCurrentText(str(current_addr))
            
        search_btn = QPushButton("검색")
        
        address_layout.addWidget(address_edit)
        address_layout.addWidget(address_combo)
        address_layout.addWidget(search_btn)
        
        address_label = QLabel("주소/인덱스:")
        
        def _search_cameras():
            search_btn.setEnabled(False)
            search_btn.setText("검색 중...")
            group.repaint() 
            
            try:
                indices = CameraManager.get_available_cameras()
                address_combo.clear()
                if indices:
                    address_combo.addItems([str(i) for i in indices])
                    address_combo.setCurrentIndex(0)
                else:
                    address_combo.addItem("0") # Default fallback
            finally:
                search_btn.setEnabled(True)
                search_btn.setText("검색")

        search_btn.clicked.connect(_search_cameras)

        def _update_ui(text):
            if text == "USB":
                address_label.setText("카메라 번호 (Index):")
                address_edit.hide()
                address_combo.show()
                search_btn.show()
            else:
                address_label.setText("RTSP 주소 (URL):")
                address_edit.show()
                address_combo.hide()
                search_btn.hide()
                address_edit.setPlaceholderText("RTSP 주소 (예: rtsp://...)")
        
        type_combo.currentTextChanged.connect(_update_ui)
        _update_ui(type_combo.currentText())
        
        pixels_spin = QDoubleSpinBox()
        pixels_spin.setRange(0.1, 10000.0)
        pixels_spin.setValue(cam_config.get('pixels_per_mm', 10.0))
        
        form.addRow("연결 방식:", type_combo)
        form.addRow(address_label, address_layout)
        form.addRow("픽셀 보정 (px/mm):", pixels_spin)
        
        return {
            'group': group, 
            'type': type_combo, 
            'address_edit': address_edit, 
            'address_combo': address_combo,
            'pixels': pixels_spin
        }

    def get_settings(self):
        """사용자가 입력한 설정을 딕셔너리 형태로 반환합니다."""
        new_config = self.config.copy()
        
        def _extract_data(widgets):
            ctype = widgets['type'].currentText()
            
            if ctype == "USB":
                addr_text = widgets['address_combo'].currentText()
                address = int(addr_text) if addr_text.isdigit() else 0
            else:
                address = widgets['address_edit'].text()
                
            return {"type": ctype, "address": address, "pixels_per_mm": widgets['pixels'].value()}

        new_config['front'] = _extract_data(self.front_widgets)
        new_config['back'] = _extract_data(self.back_widgets)
        new_config['save_path'] = self.general_widgets['save_path'].text()
        new_config['model_path'] = self.model_widgets['model_path'].text()
        return new_config