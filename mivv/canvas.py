from PyQt5.QtWidgets import QGraphicsItem
from PyQt5.QtGui import QPainter, QPen, QPixmap
from PyQt5.QtCore import Qt, QRectF

class Canvas(QPixmap):
	def __init__(self, size):
		super().__init__(size)
		self.positions = [None, None] # last, new
		self.fill(Qt.transparent);
		self.pen = QPen(Qt.green)
		self.pen.setWidth(5)

	def draw(self) -> QRectF:
		if self.positions[0] == None or self.positions[1] == None:
			return
		painter = QPainter(self)
		painter.setBrush(Qt.green)
		painter.setPen(self.pen)
		painter.drawLine(self.positions[0], self.positions[1])
		x0 = self.positions[0].x()
		y0 = self.positions[0].y()
		x1 = self.positions[1].x()
		y1 = self.positions[1].y()
		self.positions[0] = self.positions[1]
		return QRectF(min(x0, x1), min(y0, y1), abs(x0 - x1), abs(y0 - y1))\
			.adjusted(-5, -5, 5, 5)

	def update_pos(self, pos):
		self.positions[0] = self.positions[1]
		self.positions[1] = pos

class CanvasItem(QGraphicsItem):
	def __init__(self, size):
		super().__init__()
		self.on_draw = False
		self.canvas = Canvas(size)

	def boundingRect(self):
		return QRectF(self.canvas.rect())

	def paint(self, painter, option, widget):
		painter.drawPixmap(option.rect, self.canvas)

	def draw(self):
		update_rect = self.canvas.draw()
		self.update(update_rect)

	def update_pos(self, pos):
		self.canvas.update_pos(pos)
