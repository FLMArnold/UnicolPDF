from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QButtonGroup, QRadioButton, QGroupBox
)


class BackgroundDialog(QDialog):
    def __init__(self, current_path=None, current_mode="fill", parent=None):
        super().__init__(parent)
        self.setWindowTitle("自定义背景")
        self.setFixedSize(420, 320)
        self.image_path = current_path
        self.mode = current_mode

        layout = QVBoxLayout(self)

        img_layout = QHBoxLayout()
        self.path_label = QLabel(current_path or "未选择图片")
        self.path_label.setWordWrap(True)
        btn_clear = QPushButton("清除背景")
        btn_clear.clicked.connect(self._clear_image)
        btn_select = QPushButton("选择图片")
        btn_select.clicked.connect(self._select_image)
        img_layout.addWidget(self.path_label, 1)
        img_layout.addWidget(btn_clear)
        img_layout.addWidget(btn_select)
        layout.addLayout(img_layout)

        mode_group = QGroupBox("背景模式")
        mode_layout = QVBoxLayout()
        self.mode_btns = QButtonGroup(self)
        self._mode_keys = ["fill", "crop", "stretch", "dense"]
        mode_labels = [("填充 (Fill)", "填充透明像素"), ("裁切 (Crop)", "裁切多余部分"),
                       ("拉伸 (Stretch)", "拉伸铺满"), ("密排 (Dense)", "原像素平铺")]
        for i, ((text, desc), key) in enumerate(zip(mode_labels, self._mode_keys)):
            rb = QRadioButton(f"{text} - {desc}")
            if key == current_mode:
                rb.setChecked(True)
            self.mode_btns.addButton(rb, i)
            mode_layout.addWidget(rb)
        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)

        btn_layout = QHBoxLayout()
        btn_ok = QPushButton("确认")
        btn_ok.clicked.connect(self.accept)
        btn_cancel = QPushButton("取消")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

    def _select_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择背景图片", "", "Images (*.png *.gif *.jpg *.jpeg *.bmp)"
        )
        if path:
            self.image_path = path
            self.path_label.setText(path)

    def _clear_image(self):
        self.image_path = None
        self.path_label.setText("未选择图片 (恢复纯白背景)")

    def get_result(self):
        btn_id = self.mode_btns.checkedId()
        mode = self._mode_keys[btn_id] if 0 <= btn_id < len(self._mode_keys) else "fill"
        return {"path": self.image_path, "mode": mode}
