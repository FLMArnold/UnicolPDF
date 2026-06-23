import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QApplication,
    QHBoxLayout, QVBoxLayout,
    QMessageBox, QFrame, QTabWidget
)
from PyQt6.QtCore import Qt, QSettings, QEvent
from PyQt6.QtGui import QShortcut, QKeySequence
from app.pdf_engine import PDFEngine
from app.viewer_widget import ViewerWidget
from app.page_info_panel import PageInfoPanel
from app.operation_widget import OperationWidget
from app.tool_panel import ToolPanel
from app.batch_panel import BatchPanel
from app.history_manager import HistoryManager
from app.history_panel import HistoryPanel
from app.menu_bar import build_menu
from app.dialogs.import_dialog import show_import_dialog
from app.dialogs.export_dialog import show_export_dialog
from app.dialogs.background_dlg import BackgroundDialog
from app.dialogs.shortcut_dlg import ShortcutDialog
from app.dialogs.page_settings_dlg import PageSettingsDialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Unicol PDF")
        self.setMinimumSize(900, 650)

        self.engine = PDFEngine()
        self._original_pdf_name = "output"
        self._anti_batch_pages = set()
        self._batch_active = False
        self.history = HistoryManager()
        self._autosave_counter = 0
        self._autosave_threshold = 10
        self._autosave_dir = None
        self._autosave_path = None
        self._load_settings()

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Left sidebar: 操作栏 (top) + 信息栏 (bottom tabs)
        left_sidebar = QFrame()
        left_sidebar.setFixedWidth(180)
        left_sidebar.setStyleSheet("background-color: #2d2d3f;")
        left_layout = QVBoxLayout(left_sidebar)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        self.operation_widget = OperationWidget()
        left_layout.addWidget(self.operation_widget)

        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(
            "QTabWidget::pane { border: none; background: transparent; }"
            "QTabBar::tab { padding: 6px 12px; color: #ccc; background: #2d2d3f; border: none; }"
            "QTabBar::tab:selected { color: #fff; border-bottom: 2px solid #7c5cfc; }"
        )

        self.page_info = PageInfoPanel()
        self.tab_widget.addTab(self.page_info, "页面信息")

        self.batch_panel = BatchPanel()
        self.tab_widget.addTab(self.batch_panel, "工具属性")

        self.history_panel = HistoryPanel()
        self.tab_widget.addTab(self.history_panel, "历史操作")
        self.history_panel.entry_clicked.connect(self._on_history_navigate)

        left_layout.addWidget(self.tab_widget, 1)
        main_layout.addWidget(left_sidebar)

        # Center: PDF Viewer
        self.viewer = ViewerWidget()
        self.viewer.set_engine(self.engine)
        self.viewer.page_changed.connect(self._on_page_changed)
        main_layout.addWidget(self.viewer, 1)

        # Right sidebar: 工具栏 (tool placeholders)
        right_sidebar = QFrame()
        right_sidebar.setFixedWidth(60)
        right_sidebar.setStyleSheet("background-color: #2d2d3f;")
        right_layout = QVBoxLayout(right_sidebar)
        right_layout.setContentsMargins(0, 0, 0, 0)
        self.tool_panel = ToolPanel()
        right_layout.addWidget(self.tool_panel)
        main_layout.addWidget(right_sidebar)

        build_menu(self)

        self.operation_widget.operation_triggered.connect(self._on_operation_triggered)
        self.page_info.anti_batch_changed.connect(self._on_anti_batch_toggled)
        self.batch_panel.batch_changed.connect(self._on_batch_toggled)

        self.setAcceptDrops(True)
        self._apply_shortcuts()

        self._undo_shortcut = QShortcut(QKeySequence("Ctrl+Z"), self)
        self._undo_shortcut.activated.connect(self._on_undo)
        self._redo_shortcut = QShortcut(QKeySequence("Ctrl+Y"), self)
        self._redo_shortcut.activated.connect(self._on_redo)

        QApplication.instance().installEventFilter(self)

        self._check_crash_recovery()

    def _on_page_changed(self, index):
        if self.engine.doc:
            self.page_info.update_page_info(index, self.engine.page_count)
            self.page_info.set_anti_batch(index in self._anti_batch_pages)

    def _on_anti_batch_toggled(self, checked):
        current = self.viewer.current_page()
        if checked:
            self._anti_batch_pages.add(current)
        else:
            self._anti_batch_pages.discard(current)

    def _on_batch_toggled(self, checked):
        self._batch_active = checked

    def _save_history_snapshot(self, description):
        if not self.engine.doc:
            return
        buf = self.engine.save_to_buffer()
        self.history.add_snapshot(buf, description)
        self._autosave_counter += 1
        self._check_autosave()
        self.history_panel.refresh(self.history.get_display_entries())

    def _on_undo(self):
        if not self.engine.doc or not self.history.can_undo():
            return
        current_buf = self.engine.save_to_buffer()
        restored = self.history.undo(current_buf)
        if restored is None:
            return
        restored.seek(0)
        self.engine.close()
        self.engine.open_from_bytes(restored.read())
        current = min(self.viewer.current_page(), self.engine.page_count - 1)
        self.viewer.show_page(current)
        self.history_panel.refresh(self.history.get_display_entries())

    def _on_redo(self):
        if not self.engine.doc or not self.history.can_redo():
            return
        current_buf = self.engine.save_to_buffer()
        restored = self.history.redo(current_buf)
        if restored is None:
            return
        restored.seek(0)
        self.engine.close()
        self.engine.open_from_bytes(restored.read())
        current = min(self.viewer.current_page(), self.engine.page_count - 1)
        self.viewer.show_page(current)
        self.history_panel.refresh(self.history.get_display_entries())

    def _on_history_navigate(self, rel_idx):
        if rel_idx == 0 or not self.engine.doc:
            return
        current_buf = self.engine.save_to_buffer()
        restored = self.history.navigate(rel_idx, current_buf)
        if restored is None:
            return
        restored.seek(0)
        self.engine.close()
        self.engine.open_from_bytes(restored.read())
        current = min(self.viewer.current_page(), self.engine.page_count - 1)
        self.viewer.show_page(current)
        self.history_panel.refresh(self.history.get_display_entries())

    def _check_autosave(self):
        if self._autosave_counter < self._autosave_threshold:
            return
        self._autosave_counter = 0
        import tempfile, os, hashlib, json
        temp_dir = self._autosave_dir or tempfile.gettempdir()
        hash_str = hashlib.md5(self._original_pdf_name.encode()).hexdigest()[:8]
        filename = f"unicolpdf_autosave_{hash_str}.unicolbak"
        filepath = os.path.join(temp_dir, filename)
        buf = self.engine.save_to_buffer()
        with open(filepath, "wb") as f:
            f.write(buf.read())
        meta_path = filepath + ".meta"
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump({"original_name": self._original_pdf_name}, f)
        self._autosave_path = filepath

    def _cleanup_autosave(self):
        import os
        if self._autosave_path:
            for p in (self._autosave_path, self._autosave_path + ".meta"):
                if os.path.exists(p):
                    try:
                        os.remove(p)
                    except OSError:
                        pass
        self._autosave_path = None

    def _check_crash_recovery(self):
        import tempfile, os, glob, json
        temp_dir = self._autosave_dir or tempfile.gettempdir()
        pattern = os.path.join(temp_dir, "unicolpdf_autosave_*.unicolbak")
        files = glob.glob(pattern)
        if not files:
            return
        from PyQt6.QtWidgets import QMessageBox
        for filepath in files:
            original_name = "恢复文件"
            meta_path = filepath + ".meta"
            if os.path.exists(meta_path):
                try:
                    with open(meta_path, "r", encoding="utf-8") as f:
                        meta = json.load(f)
                        original_name = meta.get("original_name", "恢复文件")
                except Exception:
                    pass
            reply = QMessageBox.question(
                self, "恢复文件",
                f"检测到未保存的自动备份文件:\n{os.path.basename(filepath)}\n\n是否恢复？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                with open(filepath, "rb") as f:
                    data = f.read()
                self.engine.close()
                self.engine.open_from_bytes(data)
                self._original_pdf_name = f"恢复的-{original_name}"
                self.viewer.show_page(0)
                self.operation_widget.set_buttons_enabled(True)
                self.page_info.update_page_info(0, self.engine.page_count)
            for p in (filepath, filepath + ".meta"):
                if os.path.exists(p):
                    try:
                        os.remove(p)
                    except OSError:
                        pass

    def _on_operation_triggered(self, action_id):
        if not self.engine.doc:
            return

        if self._batch_active:
            self._execute_batch(action_id)
        else:
            self._execute_single(action_id)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress and event.key() == Qt.Key.Key_Space:
            if not event.isAutoRepeat():
                self._batch_active = True
                self.batch_panel.set_batch_mode(True)
            return True
        if event.type() == QEvent.Type.KeyRelease and event.key() == Qt.Key.Key_Space:
            if not event.isAutoRepeat():
                self._batch_active = False
                self.batch_panel.set_batch_mode(False)
            return True
        return super().eventFilter(obj, event)

    def _apply_operation(self, action_id, index):
        if action_id == "insert_before":
            self.engine.insert_page_before(index)
        elif action_id == "insert_after":
            self.engine.insert_page_after(index)
        elif action_id == "delete":
            self.engine.delete_page(index)

    def _execute_single(self, action_id):
        current = self.viewer.current_page()
        if action_id == "delete":
            if self.engine.page_count <= 1:
                QMessageBox.warning(self, "警告", "至少保留一页")
                return
        desc = {"insert_before": "页面前增", "insert_after": "页面后增", "delete": "页面删除"}[action_id]
        self._save_history_snapshot(desc)
        self._apply_operation(action_id, current)
        if action_id == "insert_before":
            self._shift_anti_batch_after_insert(current)
        elif action_id == "insert_after":
            self._shift_anti_batch_after_insert(current + 1)
        elif action_id == "delete":
            self._shift_anti_batch_after_delete(current)
            current = max(0, min(current, self.engine.page_count - 1))
        self.viewer.show_page(current)

    def _execute_batch(self, action_id):
        pages = [i for i in range(self.engine.page_count) if i not in self._anti_batch_pages]
        if not pages:
            return
        if action_id == "delete" and len(pages) >= self.engine.page_count:
            QMessageBox.warning(self, "警告", "不能删除所有页面")
            return
        desc = "批处理-" + {"insert_before": "页面前增", "insert_after": "页面后增", "delete": "页面删除"}[action_id]
        self._save_history_snapshot(desc)
        for i in reversed(pages):
            self._apply_operation(action_id, i)
        if action_id == "delete":
            self._anti_batch_pages = {
                i for i in self._anti_batch_pages if i < self.engine.page_count
            }
        self.viewer.show_page(self.viewer.current_page())

    def on_import(self):
        result = show_import_dialog(self)
        if result:
            pdf_path = result["pdf_path"]
            self._original_pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
            self._cleanup_autosave()
            self._anti_batch_pages.clear()
            self.history.clear()
            self.history_panel.refresh(self.history.get_display_entries())
            self._autosave_counter = 0
            count = self.engine.open(pdf_path)
            if count > 0:
                self.viewer.show_page(0)
                self.operation_widget.set_buttons_enabled(True)
                self.page_info.update_page_info(0, count)

    def on_export(self):
        if not self.engine.doc:
            QMessageBox.warning(self, "警告", "没有打开的PDF")
            return
        result = show_export_dialog(self, self.engine, self._original_pdf_name)
        if result:
            self._cleanup_autosave()
            self._autosave_counter = 0
            QMessageBox.information(self, "导出成功", "PDF已导出")

    def on_background_settings(self):
        dlg = BackgroundDialog(self.engine.bg_image_path, self.engine.bg_mode, self)
        if dlg.exec():
            result = dlg.get_result()
            if result and result["path"]:
                self.engine.set_bg_image(result["path"], result["mode"])
            else:
                self.engine.set_bg_image(None)
            self._save_settings()
            if self.engine.doc:
                self.viewer.show_page(self.viewer.current_page())

    def _load_settings(self):
        settings = QSettings("UnicolPDF", "UnicolPDF")
        path = settings.value("bg_image_path", None)
        mode = settings.value("bg_mode", "fill")
        if path:
            self.engine.set_bg_image(path, mode)
        else:
            self.engine.set_bg_image(None)
        history_limit = settings.value("history_limit", "20")
        self.history.set_max_steps(int(history_limit))
        threshold = settings.value("autosave_threshold", "10")
        self._autosave_threshold = int(threshold)
        self._autosave_dir = settings.value("autosave_dir", None)
        if self._autosave_dir == "":
            self._autosave_dir = None

    def _save_settings(self):
        settings = QSettings("UnicolPDF", "UnicolPDF")
        settings.setValue("bg_image_path", self.engine.bg_image_path or "")
        settings.setValue("bg_mode", self.engine.bg_mode)
        settings.setValue("history_limit", self.history.max_steps)
        settings.setValue("autosave_threshold", self._autosave_threshold)
        settings.setValue("autosave_dir", self._autosave_dir or "")

    def on_page_settings(self):
        dlg = PageSettingsDialog(self.engine, self)
        if dlg.exec():
            result = dlg.get_result()
            self.engine.set_dpi(result["dpi"])
            self.engine.set_page_size(result["width"], result["height"])
            self.page_info.set_dpi(result["dpi"])
            if self.engine.doc:
                self.viewer.show_page(self.viewer.current_page())

    def on_shortcut_settings(self):
        dlg = ShortcutDialog(self)
        if dlg.exec():
            self._apply_shortcuts()

    def _apply_shortcuts(self):
        for sc in getattr(self, '_shortcut_refs', []):
            sc.setEnabled(False)
        self._shortcut_refs = []
        settings = QSettings("UnicolPDF", "UnicolPDF")
        mapping = {
            "insert_before": lambda: self._on_operation_triggered("insert_before"),
            "insert_after": lambda: self._on_operation_triggered("insert_after"),
            "delete": lambda: self._on_operation_triggered("delete"),
        }
        for action_id, callback in mapping.items():
            s = settings.value(f"shortcut_{action_id}", "")
            if s:
                ks = QKeySequence(s)
                if not ks.isEmpty():
                    sc = QShortcut(ks, self)
                    sc.activated.connect(callback)
                    self._shortcut_refs.append(sc)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.toLocalFile().lower().endswith('.pdf'):
                    event.acceptProposedAction()
                    return

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path.lower().endswith('.pdf'):
                self._open_pdf_direct(path)
                break

    def _shift_anti_batch_after_insert(self, inserted_index):
        shifted = set()
        for i in self._anti_batch_pages:
            if i >= inserted_index:
                shifted.add(i + 1)
            else:
                shifted.add(i)
        self._anti_batch_pages = shifted

    def _shift_anti_batch_after_delete(self, deleted_index):
        shifted = set()
        for i in self._anti_batch_pages:
            if i == deleted_index:
                continue
            if i > deleted_index:
                shifted.add(i - 1)
            else:
                shifted.add(i)
        self._anti_batch_pages = shifted

    def _open_pdf_direct(self, pdf_path):
        self._original_pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
        self._anti_batch_pages.clear()
        self.history.clear()
        self.history_panel.refresh(self.history.get_display_entries())
        self._autosave_counter = 0
        count = self.engine.open(pdf_path)
        if count > 0:
            self.viewer.show_page(0)
            self.operation_widget.set_buttons_enabled(True)
            self.page_info.update_page_info(0, count)

    def on_history_limit_settings(self):
        from PyQt6.QtWidgets import QInputDialog
        value, ok = QInputDialog.getInt(
            self, "历史操作上限", "设置最大历史操作步数:",
            value=self.history.max_steps, min=1, max=500
        )
        if ok:
            self.history.set_max_steps(value)
            self._save_settings()

    def on_autosave_settings(self):
        import tempfile
        from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                                      QLabel, QPushButton, QSpinBox,
                                      QFileDialog)
        from PyQt6.QtCore import Qt

        dlg = QDialog(self)
        dlg.setWindowTitle("自动保存设置")
        dlg.setFixedSize(420, 200)
        layout = QVBoxLayout(dlg)

        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("路径:"))
        path_label = QLabel(self._autosave_dir or tempfile.gettempdir())
        path_label.setWordWrap(True)
        path_layout.addWidget(path_label, 1)

        def _select_autosave_path():
            folder = QFileDialog.getExistingDirectory(dlg, "选择自动保存文件夹")
            if folder:
                self._autosave_dir = folder
                path_label.setText(folder)

        def _open_autosave_folder():
            import subprocess
            folder = self._autosave_dir or tempfile.gettempdir()
            subprocess.Popen(["explorer", folder])

        btn_browse = QPushButton("浏览")
        btn_browse.clicked.connect(_select_autosave_path)
        btn_open = QPushButton("打开文件夹")
        btn_open.clicked.connect(_open_autosave_folder)
        path_layout.addWidget(btn_browse)
        path_layout.addWidget(btn_open)
        layout.addLayout(path_layout)

        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel("自动保存阈值:"))
        threshold_spin = QSpinBox()
        threshold_spin.setRange(1, 1000)
        threshold_spin.setValue(self._autosave_threshold)
        threshold_layout.addWidget(threshold_spin)
        threshold_layout.addWidget(QLabel("次操作"))
        threshold_layout.addStretch()
        layout.addLayout(threshold_layout)

        btn_ok = QPushButton("确认")
        btn_ok.clicked.connect(dlg.accept)
        layout.addWidget(btn_ok, 0, Qt.AlignmentFlag.AlignCenter)

        if dlg.exec():
            self._autosave_threshold = threshold_spin.value()
            self._save_settings()

    def closeEvent(self, event):
        self.engine.close()
        event.accept()
