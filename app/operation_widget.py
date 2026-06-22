from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton


class OperationWidget(QWidget):
    operation_triggered = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        self.btn_insert_before = QPushButton("页面前增")
        self.btn_insert_before.clicked.connect(
            lambda: self.operation_triggered.emit("insert_before")
        )
        layout.addWidget(self.btn_insert_before)

        self.btn_insert_after = QPushButton("页面后增")
        self.btn_insert_after.clicked.connect(
            lambda: self.operation_triggered.emit("insert_after")
        )
        layout.addWidget(self.btn_insert_after)

        self.btn_delete = QPushButton("页面删除")
        self.btn_delete.clicked.connect(
            lambda: self.operation_triggered.emit("delete")
        )
        layout.addWidget(self.btn_delete)

        layout.addStretch()

    def set_buttons_enabled(self, enabled):
        self.btn_insert_before.setEnabled(enabled)
        self.btn_insert_after.setEnabled(enabled)
        self.btn_delete.setEnabled(enabled)
