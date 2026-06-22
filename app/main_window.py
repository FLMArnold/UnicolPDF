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

        QApplication.instance().installEventFilter(self)

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
            self._anti_batch_pages.clear()
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

    def _save_settings(self):
        settings = QSettings("UnicolPDF", "UnicolPDF")
        settings.setValue("bg_image_path", self.engine.bg_image_path or "")
        settings.setValue("bg_mode", self.engine.bg_mode)

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
        count = self.engine.open(pdf_path)
        if count > 0:
            self.viewer.show_page(0)
            self.operation_widget.set_buttons_enabled(True)
            self.page_info.update_page_info(0, count)

    def closeEvent(self, event):
        self.engine.close()
        event.accept()
