from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QSpinBox, QComboBox, QGroupBox, QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QBrush
from app.pdf_engine import PDFEngine


class _RatioPreview(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(200, 160)
        self.ratio_w = 4
        self.ratio_h = 3

    def set_ratio(self, w, h):
        self.ratio_w = w
        self.ratio_h = h
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#2d2d3f"))

        cw, ch = self.width() - 20, self.height() - 20
        aspect = self.ratio_w / self.ratio_h if self.ratio_h else 1
        if aspect > cw / ch:
            pw = cw
            ph = int(cw / aspect)
        else:
            ph = ch
            pw = int(ch * aspect)
        x = (self.width() - pw) // 2
        y = (self.height() - ph) // 2

        painter.setBrush(QBrush(QColor("#7c5cfc")))
        painter.setPen(QColor("#5a3cc0"))
        painter.drawRoundedRect(x, y, pw, ph, 4, 4)

        painter.setPen(QColor("#c0c0d0"))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, f"{self.ratio_w}:{self.ratio_h}")


class PageSettingsDialog(QDialog):
    def __init__(self, engine, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.setWindowTitle("图像-页面设置")
        self.setFixedSize(420, 480)

        layout = QVBoxLayout(self)

        res_group = QGroupBox("分辨率")
        res_layout = QHBoxLayout()
        res_layout.addWidget(QLabel("分辨率:"))
        self.dpi_spin = QSpinBox()
        self.dpi_spin.setRange(72, 1200)
        self.dpi_spin.setValue(engine.current_dpi)
        res_layout.addWidget(self.dpi_spin)
        self.unit_combo = QComboBox()
        self.unit_combo.addItems(["DPI", "DPCM"])
        res_layout.addWidget(self.unit_combo)
        res_layout.addStretch()
        res_group.setLayout(res_layout)
        layout.addWidget(res_group)

        size_group = QGroupBox("页面尺寸 (像素)")
        size_layout = QVBoxLayout()

        cur_w = engine.page_width
        cur_h = engine.page_height
        cur_pw = int(cur_w * engine.current_dpi / 72)
        cur_ph = int(cur_h * engine.current_dpi / 72)

        self.cur_label = QLabel(f"当前: {cur_w}×{cur_h} ({cur_pw}×{cur_ph}px)")
        size_layout.addWidget(self.cur_label)

        ratio_layout = QHBoxLayout()
        ratio_layout.addWidget(QLabel("目标比例:"))
        self.ratio_w_spin = QSpinBox()
        self.ratio_w_spin.setRange(1, 99999)
        self.ratio_w_spin.setValue(cur_w)
        ratio_layout.addWidget(self.ratio_w_spin)
        ratio_layout.addWidget(QLabel(":"))
        self.ratio_h_spin = QSpinBox()
        self.ratio_h_spin.setRange(1, 99999)
        self.ratio_h_spin.setValue(cur_h)
        ratio_layout.addWidget(self.ratio_h_spin)
        size_layout.addLayout(ratio_layout)

        self.adj_label = QLabel("调整后: —")
        size_layout.addWidget(self.adj_label)

        size_group.setLayout(size_layout)
        layout.addWidget(size_group)

        self.ratio_w_spin.valueChanged.connect(self._update_preview)
        self.ratio_h_spin.valueChanged.connect(self._update_preview)

        preview_group = QGroupBox("预览")
        preview_layout = QVBoxLayout()
        self.preview = _RatioPreview()
        self.preview.set_ratio(cur_w, cur_h)
        preview_layout.addWidget(self.preview, 0, Qt.AlignmentFlag.AlignCenter)
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)

        btn_layout = QHBoxLayout()
        btn_ok = QPushButton("确认")
        btn_ok.clicked.connect(self.accept)
        btn_cancel = QPushButton("取消")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

        self._update_preview()

    def _update_preview(self):
        rw = self.ratio_w_spin.value()
        rh = self.ratio_h_spin.value()
        self.preview.set_ratio(rw, rh)
        orig_w = self.engine.page_width
        orig_h = self.engine.page_height

        new_w, new_h = PDFEngine.calc_no_loss_size(orig_w, orig_h, rw, rh)
        new_pw = int(new_w * self.engine.current_dpi / 72)
        new_ph = int(new_h * self.engine.current_dpi / 72)
        self.adj_label.setText(f"调整后: {new_w}×{new_h} ({new_pw}×{new_ph}px)  (≈ {rw}:{rh})")

    def get_result(self):
        rw = self.ratio_w_spin.value()
        rh = self.ratio_h_spin.value()
        orig_w = self.engine.page_width
        orig_h = self.engine.page_height

        new_w, new_h = PDFEngine.calc_no_loss_size(orig_w, orig_h, rw, rh)

        return {
            "dpi": self.dpi_spin.value(),
            "width": new_w,
            "height": new_h,
        }
