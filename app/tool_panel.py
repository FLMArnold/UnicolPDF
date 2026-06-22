from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel


class ToolPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        label = QLabel("工具栏")
        label.setStyleSheet("color: #606078; font-size: 12px;")
        layout.addWidget(label)

        layout.addStretch()
