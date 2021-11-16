# brush method
# draw()
# input: point sequence
# output: update patch, offset

from PyQt5.QtGui import QPainter, QPen, QPixmap
from PyQt5.QtCore import Qt, QPoint, QPointF, QRectF

class DummyBrush():
	def __init__(self):
		self.tan = QPointF()
		self.size = 5
		self.reset_draw()

	def draw(self, pos, pressure):
		s = self.size
		self.hist_pos.append(pos)
		self.hist_pressure.append(pressure)
		if len(self.hist_pos) <= 1:
			return (None, None)
		if len(self.hist_pos) == 2:
			self.tan = pos - self.hist_pos[0]
		draw_rect = QRectF(self.hist_pos[-2], pos) \
			.normalized() \
			.adjusted(-s, -s, s, s) \
			.toAlignedRect()
		pixmap = QPixmap(draw_rect.size())
		pixmap.fill(Qt.green)
		return (pixmap, draw_rect.topLeft())

	def reset_draw(self):
		# tan no need reset
		self.hist_pos = []
		self.hist_pressure = []
