from PyQt5.QtWidgets import QGraphicsItem
from PyQt5.QtGui import QPainter, QPen, QPixmap
from PyQt5.QtCore import Qt, QRectF, QSizeF

from mivv import var
from .common_brushes import DummyBrush

class Canvas(QPixmap):
	def __init__(self, size):
		super().__init__(size.width(), size.height())
		self.positions = [None, None] # last, new
		self.fill(Qt.transparent)
		self.pen = QPen(Qt.green)
		self.pen.setWidth(5)
		self.mb = DummyBrush()

	def draw(self, pos, pressure):
		pixmap_patch, p = self.mb.draw(self, pos, pressure)
		if not pixmap_patch:
			return None
		painter = QPainter(self)
		painter.setCompositionMode(QPainter.CompositionMode_Source)
		painter.drawPixmap(p, pixmap_patch)
		return QRectF(p, QSizeF(pixmap_patch.size()))

	def finish(self):
		self.mb.reset_draw()

class CanvasItem(QGraphicsItem):
	def __init__(self, size):
		super().__init__()
		self.on_draw = False
		self.canvas = Canvas(size)

	def boundingRect(self):
		return QRectF(self.canvas.rect())

	def paint(self, painter, option, _widget):
		painter.drawPixmap(option.rect, self.canvas)

	def draw(self, pos, pressure):
		if not self.boundingRect().contains(pos):
			self.canvas.finish()
			return
		update_rect = self.canvas.draw(pos, pressure)
		if update_rect:
			var.logger.debug(f"Update rect: {update_rect}")
			self.update(update_rect)

	def finish(self):
		self.canvas.finish()

	def set_operator(self, is_eraser):
		self.canvas.mb.erase_mode = is_eraser
