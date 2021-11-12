from PyQt5.QtGui import QPainter, QPen, QPixmap
from PyQt5.QtCore import Qt

class Canvas(QPixmap):
	def __init__(self, size):
		super().__init__(size)
		self.positions = [None, None] # last, new
		self.fill(Qt.transparent);
		self.pen = QPen(Qt.green)
		self.pen.setWidth(5)
		self.on_draw = False

	def draw(self):
		if self.positions[0] == None or self.positions[1] == None:
			return
		painter = QPainter(self)
		painter.setBrush(Qt.green)
		painter.setPen(self.pen)
		painter.drawLine(self.positions[0], self.positions[1])
		self.positions[0] = self.positions[1]

	def update_pos(self, pos):
		self.positions[0] = self.positions[1]
		self.positions[1] = pos
