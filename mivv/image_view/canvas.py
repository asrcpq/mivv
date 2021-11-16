from PyQt5.QtWidgets import QGraphicsItem
from PyQt5.QtGui import QPainter, QPen, QPixmap
from PyQt5.QtCore import Qt, QRectF

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
		pixmap_patch, p = self.mb.draw(pos, pressure)
		if not pixmap_patch:
			return
		painter = QPainter(self)
		painter.drawPixmap(p, pixmap_patch)

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
		self.canvas.draw(pos, pressure)

	def finish(self):
		self.canvas.finish()
