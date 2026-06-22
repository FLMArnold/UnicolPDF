from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QCheckBox


class BatchPanel(QWidget):
    batch_changed = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        self.batch_cb = QCheckBox("批处理模式")
        self.batch_cb.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.batch_cb.toggled.connect(self.batch_changed.emit)
        layout.addWidget(self.batch_cb)

        layout.addStretch()

    def set_batch_mode(self, checked):
        self.batch_cb.blockSignals(True)
        self.batch_cb.setChecked(checked)
        self.batch_cb.blockSignals(False)
