from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPainter, QPixmap
from PyQt6.QtWidgets import QWidget


class ViewerWidget(QWidget):
    page_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.engine = None
        self._page = 0
        self._pixmap = None
        self.setMinimumSize(400, 500)
        self.setMouseTracking(True)

    def set_engine(self, engine):
        self.engine = engine

    def show_page(self, index):
        if not self.engine:
            return
        if 0 <= index < self.engine.page_count:
            self._page = index
            img = self.engine.get_page(index)
            if img:
                scaled = img.scaled(
                    self.width() - 20, self.height() - 20,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self._pixmap = QPixmap.fromImage(scaled)
            else:
                self._pixmap = None
            self.update()
            self.page_changed.emit(index)

    def current_page(self):
        return self._page

    def paintEvent(self, event):
        if self._pixmap:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
            x = (self.width() - self._pixmap.width()) // 2
            y = (self.height() - self._pixmap.height()) // 2
            painter.drawPixmap(x, y, self._pixmap)

    def wheelEvent(self, event):
        if not self.engine:
            return
        delta = event.angleDelta().y()
        if delta > 0 and self._page > 0:
            self.show_page(self._page - 1)
        elif delta < 0 and self._page < self.engine.page_count - 1:
            self.show_page(self._page + 1)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._pixmap:
            self.show_page(self._page)
