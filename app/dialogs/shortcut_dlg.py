from PyQt6.QtCore import Qt, QSettings, QEvent
from PyQt6.QtGui import QKeySequence
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QComboBox, QHeaderView
)


class ShortcutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("快捷键设置")
        self.setFixedSize(620, 320)

        layout = QVBoxLayout(self)

        self.table = QTableWidget(3, 4)
        self.table.setHorizontalHeaderLabels(["操作", "功能键1", "功能键2", "按键"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)

        self._mod_options = ["", "Ctrl", "Alt", "Shift"]
        self._actions = ["页面前增", "页面后增", "页面删除"]
        self._action_ids = ["insert_before", "insert_after", "delete"]

        settings = QSettings("UnicolPDF", "UnicolPDF")

        for i in range(3):
            self.table.setItem(i, 0, QTableWidgetItem(self._actions[i]))

            mod_cb1 = QComboBox()
            mod_cb1.addItems(self._mod_options)
            self.table.setCellWidget(i, 1, mod_cb1)

            mod_cb2 = QComboBox()
            mod_cb2.addItems(self._mod_options)
            self.table.setCellWidget(i, 2, mod_cb2)

            key_item = QTableWidgetItem("点击设置")
            key_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            key_item.setFlags(key_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 3, key_item)

            saved = settings.value(f"shortcut_{self._action_ids[i]}", "")
            if saved:
                parts = saved.split("+")
                mods = parts[:-1]
                key = parts[-1] if parts else ""
                if key not in ("点击设置", "按下按键..."):
                    for mod in mods:
                        if mod in self._mod_options:
                            if mod_cb1.currentText() == "":
                                mod_cb1.setCurrentText(mod)
                            elif mod_cb2.currentText() == "":
                                mod_cb2.setCurrentText(mod)
                    key_item.setText(key)

        self.table.cellClicked.connect(self._on_cell_clicked)
        layout.addWidget(self.table)
        self.table.installEventFilter(self)

        btn_layout = QHBoxLayout()
        btn_ok = QPushButton("确认")
        btn_ok.clicked.connect(self.accept)
        btn_cancel = QPushButton("取消")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

        self._capturing = None

    def _on_cell_clicked(self, row, col):
        if col != 3:
            return
        self._capturing = row
        self.table.item(row, 3).setText("按下按键...")
        self.table.setFocus()

    def _capture_key(self, event):
        key = event.key()
        if key in (
            Qt.Key.Key_Control, Qt.Key.Key_Alt,
            Qt.Key.Key_Shift, Qt.Key.Key_Meta
        ):
            self.table.item(self._capturing, 3).setText("点击设置")
            self._capturing = None
            return True

        name = QKeySequence(key).toString()
        if Qt.Key.Key_A <= key <= Qt.Key.Key_Z:
            name = name.upper()
        else:
            name = name.lower()

        self.table.item(self._capturing, 3).setText(name)
        self._capturing = None
        return True

    def eventFilter(self, obj, event):
        if obj is self.table and self._capturing is not None and event.type() == QEvent.Type.KeyPress:
            return self._capture_key(event)
        return super().eventFilter(obj, event)

    def keyPressEvent(self, event):
        if self._capturing is not None:
            self._capture_key(event)
            return
        super().keyPressEvent(event)

    def _get_shortcuts(self):
        result = {}
        for i, action_id in enumerate(self._action_ids):
            mod1 = self.table.cellWidget(i, 1).currentText()
            mod2 = self.table.cellWidget(i, 2).currentText()
            key = self.table.item(i, 3).text()
            if key and key not in ("点击设置", "按下按键..."):
                parts = [m for m in [mod1, mod2, key] if m]
                result[action_id] = "+".join(parts)
        return result

    def accept(self):
        settings = QSettings("UnicolPDF", "UnicolPDF")
        shortcuts = self._get_shortcuts()
        for action_id, shortcut in shortcuts.items():
            settings.setValue(f"shortcut_{action_id}", shortcut)
        super().accept()
