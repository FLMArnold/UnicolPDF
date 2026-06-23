import os
import io
import fitz
from PyQt6.QtGui import QImage, QPainter, QColor
from PyQt6.QtCore import QRect


class PDFEngine:
    def __init__(self):
        self.doc = None
        self._dpi = 300
        self._page_width = 595
        self._page_height = 842
        self._bg_color = QColor(255, 255, 255)
        self._bg_image = None
        self._bg_image_path = None
        self._bg_mode = "fill"

    def open(self, path):
        self.doc = fitz.open(path)
        if self.doc.page_count > 0:
            rect = self.doc[0].rect
            self._page_width = round(rect.width)
            self._page_height = round(rect.height)
        return self.page_count

    @classmethod
    def calc_no_loss_size(cls, orig_w, orig_h, ratio_w, ratio_h):
        new_w1 = orig_w
        new_h1 = int(orig_w * ratio_h / ratio_w)
        new_h2 = orig_h
        new_w2 = int(orig_h * ratio_w / ratio_h)
        if new_h1 >= orig_h:
            return new_w1, new_h1
        else:
            return new_w2, new_h2

    @property
    def page_count(self):
        return self.doc.page_count if self.doc else 0

    @property
    def current_dpi(self):
        return self._dpi

    def set_dpi(self, dpi):
        self._dpi = max(72, min(dpi, 1200))

    @property
    def page_width(self):
        return self._page_width

    @property
    def page_height(self):
        return self._page_height

    def set_page_size(self, width, height):
        self._page_width = max(1, width)
        self._page_height = max(1, height)

    def set_bg_image(self, image_path=None, mode=None):
        if image_path:
            self._bg_image = QImage(image_path)
            self._bg_image_path = image_path
            if mode:
                self._bg_mode = mode
        else:
            self._bg_image = None
            self._bg_image_path = None

    @property
    def bg_image_path(self):
        return self._bg_image_path

    @property
    def bg_mode(self):
        return self._bg_mode

    def get_page(self, index, dpi=None):
        if not self.doc:
            return None
        dpi = dpi or self._dpi
        page = self.doc[index]
        zoom = dpi / 72
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=True)

        pw, ph = pix.width, pix.height
        src = QImage(pix.samples, pw, ph, pix.stride, QImage.Format.Format_RGBA8888)

        target_w = int(self._page_width * zoom)
        target_h = int(self._page_height * zoom)

        canvas = QImage(target_w, target_h, QImage.Format.Format_ARGB32)
        self._draw_bg(canvas, target_w, target_h)

        if pw == target_w and ph == target_h:
            painter = QPainter(canvas)
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
            painter.drawImage(0, 0, src)
            painter.end()
        else:
            src_aspect = pw / ph
            dst_aspect = target_w / target_h
            if src_aspect > dst_aspect:
                draw_w = target_w
                draw_h = int(target_w / src_aspect)
            else:
                draw_h = target_h
                draw_w = int(target_h * src_aspect)
            x = (target_w - draw_w) // 2
            y = (target_h - draw_h) // 2
            painter = QPainter(canvas)
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
            painter.drawImage(QRect(x, y, draw_w, draw_h), src)
            painter.end()

        return canvas

    def _draw_bg(self, canvas, w, h):
        if not self._bg_image or self._bg_image.isNull():
            canvas.fill(self._bg_color)
            return

        painter = QPainter(canvas)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        bw = self._bg_image.width()
        bh = self._bg_image.height()

        if self._bg_mode == "fill":
            aspect = bw / bh
            if aspect > w / h:
                draw_w = w
                draw_h = int(w / aspect)
            else:
                draw_h = h
                draw_w = int(h * aspect)
            x = (w - draw_w) // 2
            y = (h - draw_h) // 2
            painter.fillRect(0, 0, w, h, self._bg_color)
            painter.drawImage(QRect(x, y, draw_w, draw_h), self._bg_image)

        elif self._bg_mode == "crop":
            target_aspect = w / h
            bg_aspect = bw / bh
            if bg_aspect > target_aspect:
                src_h = bh
                src_w = int(bh * target_aspect)
            else:
                src_w = bw
                src_h = int(bw / target_aspect)
            src_x = (bw - src_w) // 2
            src_y = (bh - src_h) // 2
            painter.drawImage(QRect(0, 0, w, h), self._bg_image, QRect(src_x, src_y, src_w, src_h))

        elif self._bg_mode == "stretch":
            painter.drawImage(QRect(0, 0, w, h), self._bg_image)

        elif self._bg_mode == "dense":
            dpi = self._dpi
            scale = dpi / 72
            tile_w = int(bw * scale)
            tile_h = int(bh * scale)
            for ty in range(0, h, tile_h):
                for tx in range(0, w, tile_w):
                    painter.drawImage(QRect(tx, ty, tile_w, tile_h), self._bg_image)

        painter.end()

    def insert_page_before(self, index):
        if not self.doc:
            return
        self.doc.new_page(pno=index, width=self._page_width, height=self._page_height)

    def insert_page_after(self, index):
        if not self.doc:
            return
        self.doc.new_page(pno=index + 1, width=self._page_width, height=self._page_height)

    def delete_page(self, index):
        if not self.doc or self.doc.page_count == 0:
            return
        self.doc.delete_page(index)

    def save(self, path):
        if self.doc:
            if os.path.exists(path):
                os.remove(path)
            self.doc.save(path, garbage=4, deflate=True)

    def save_to_buffer(self):
        buf = io.BytesIO()
        if self.doc:
            self.doc.save(buf, garbage=4, deflate=True)
        buf.seek(0)
        return buf

    def open_from_bytes(self, data: bytes):
        self.doc = fitz.open(stream=data, filetype="pdf")
        if self.doc.page_count > 0:
            rect = self.doc[0].rect
            self._page_width = round(rect.width)
            self._page_height = round(rect.height)
        return self.page_count

    def close(self):
        if self.doc:
            self.doc.close()
            self.doc = None
