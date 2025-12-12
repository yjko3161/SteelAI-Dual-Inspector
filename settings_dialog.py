from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QGroupBox, QComboBox, 
                             QLineEdit, QDialogButtonBox, QDoubleSpinBox, QFormLayout, QLabel,
                             QPushButton, QHBoxLayout, QFileDialog)

class SettingsDialog(QDialog):
    def __init__(self, current_config, parent=None):
        super().__init__(parent)
        self.config = current_config
        self.setWindowTitle("카메라 및 시스템 설정")
        self.resize(400, 400)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        # General Settings (Save Path)
        self.general_widgets = self._create_general_group("일반 설정", self.config)
        layout.addWidget(self.general_widgets['group'])

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

    def _create_cam_group(self, title, cam_config):
        group = QGroupBox(title)
        form = QFormLayout(group)
        
        type_combo = QComboBox()
        type_combo.addItems(["USB", "RTSP"])
        type_combo.setCurrentText(cam_config.get('type', 'USB'))
        
        address_edit = QLineEdit(str(cam_config.get('address', 0)))
        address_label = QLabel("주소/인덱스:")
        
        # 연결 방식에 따라 입력 필드 힌트 변경
        def _update_ui(text):
            if text == "USB":
                address_label.setText("카메라 번호 (Index):")
                address_edit.setPlaceholderText("카메라 인덱스 (예: 0, 1)")
                address_edit.setToolTip("PC에 연결된 USB 카메라 번호 (0부터 시작)")
            else:
                address_label.setText("RTSP 주소 (URL):")
                address_edit.setPlaceholderText("RTSP 주소 (예: rtsp://192.168.0.1:554/stream)")
                address_edit.setToolTip("IP 카메라의 RTSP 스트림 주소 입력")
        
        type_combo.currentTextChanged.connect(_update_ui)
        _update_ui(type_combo.currentText())
        
        pixels_spin = QDoubleSpinBox()
        pixels_spin.setRange(0.1, 10000.0)
        pixels_spin.setValue(cam_config.get('pixels_per_mm', 10.0))
        
        form.addRow("연결 방식:", type_combo)
        form.addRow(address_label, address_edit)
        form.addRow("픽셀 보정 (px/mm):", pixels_spin)
        
        return {'group': group, 'type': type_combo, 'address': address_edit, 'pixels': pixels_spin}

    def get_settings(self):
        """사용자가 입력한 설정을 딕셔너리 형태로 반환합니다."""
        new_config = self.config.copy()
        
        def _extract_data(widgets):
            ctype = widgets['type'].currentText()
            addr_text = widgets['address'].text()
            # USB일 경우 정수로 변환, 실패 시 0
            if ctype == "USB":
                address = int(addr_text) if addr_text.isdigit() else 0
            else:
                address = addr_text
            return {"type": ctype, "address": address, "pixels_per_mm": widgets['pixels'].value()}

        new_config['front'] = _extract_data(self.front_widgets)
        new_config['back'] = _extract_data(self.back_widgets)
        new_config['save_path'] = self.general_widgets['save_path'].text()
        return new_config