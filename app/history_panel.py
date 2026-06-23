from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QLabel
)


class HistoryPanel(QWidget):
    entry_clicked = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(4)

        title = QLabel("历史操作")
        title.setStyleSheet("font-size: 13px; font-weight: bold; color: #c0c0d0;")
        layout.addWidget(title)

        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet(
            "QListWidget { background: transparent; border: none; }"
            "QListWidget::item { padding: 4px 6px; border-radius: 3px; }"
            "QListWidget::item:hover { background: #3d3d5f; }"
        )
        self.list_widget.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self.list_widget)

    def refresh(self, entries):
        self.list_widget.blockSignals(True)
        self.list_widget.clear()
        for desc, rel_idx, is_current, is_future in entries:
            label = f"{desc} ({self._format_idx(rel_idx)})"
            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, rel_idx)
            if is_current:
                item.setForeground(Qt.GlobalColor.white)
                item.setBackground(Qt.GlobalColor.darkBlue)
            elif is_future:
                item.setForeground(Qt.GlobalColor.gray)
            else:
                item.setForeground(Qt.GlobalColor.lightGray)
            self.list_widget.addItem(item)
        self.list_widget.blockSignals(False)

    def _format_idx(self, rel_idx):
        if rel_idx == 0:
            return "#0"
        elif rel_idx > 0:
            return f"#{rel_idx}"
        else:
            return f"#{rel_idx}"

    def _on_item_clicked(self, item):
        rel_idx = item.data(Qt.ItemDataRole.UserRole)
        self.entry_clicked.emit(rel_idx)
