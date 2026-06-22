from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QCheckBox, QHBoxLayout
)


class PageInfoPanel(QWidget):
    anti_batch_changed = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        self.page_label = QLabel("0 / 0")
        self.page_label.setStyleSheet("font-size: 15px; font-weight: bold;")
        layout.addWidget(self.page_label)

        self.anti_batch_cb = QCheckBox("抗批处理")
        self.anti_batch_cb.toggled.connect(self.anti_batch_changed.emit)
        layout.addWidget(self.anti_batch_cb)

        dpi_layout = QHBoxLayout()
        dpi_layout.addWidget(QLabel("DPI:"))
        self.dpi_label = QLabel("300")
        dpi_layout.addWidget(self.dpi_label)
        dpi_layout.addStretch()
        layout.addLayout(dpi_layout)

        layout.addStretch()

    def update_page_info(self, current, total):
        self.page_label.setText(f"{current + 1} / {total}")

    def set_anti_batch(self, checked):
        self.anti_batch_cb.blockSignals(True)
        self.anti_batch_cb.setChecked(checked)
        self.anti_batch_cb.blockSignals(False)

    def set_dpi(self, dpi):
        self.dpi_label.setText(str(dpi))
