# brush method
# draw()
# input: point sequence
# output: update patch, offset

from PyQt5.QtGui import QPainter, QPen, QPixmap, QColor, QPolygonF
from PyQt5.QtCore import Qt, QPoint, QPointF, QRectF, QLineF
class DummyBrush():
	def __init__(self):
		self.hist_pos = []
		self.hist_pressure = []
		self.s = 0
		self.spacing = 1
		self.size = 5
		self.erase_mode = False

	def draw(self, canvas_pixmap, pos, pressure):
		self.hist_pos.append(pos)
		self.hist_pressure.append(pressure)
		# len can't be 0 or 2
		if len(self.hist_pos) == 1:
			return (None, None)
		if self.erase_mode:
			size = 3 * self.size # larger eraser
		else:
			size = self.size
		s0 = pressure * size
		s1 = self.hist_pressure[-2] * size
		s = max(s0, s1)
		draw_rect = QRectF(self.hist_pos[-2], self.hist_pos[-1]) \
			.normalized() \
			.adjusted(-s, -s, s, s) \
			.toAlignedRect()
		offset = draw_rect.topLeft()
		p0 = pos - offset
		p1 = self.hist_pos[-2] - offset
		rnu_line = QLineF(p0, p1).unitVector()
		rnu_vec = QPointF(rnu_line.dy(), -rnu_line.dx())
		plist = [
			s0 * rnu_vec + p0,
			s1 * rnu_vec + p1,
			-s1 * rnu_vec + p1,
			-s0 * rnu_vec + p0,
		]
		pixmap = canvas_pixmap.copy(draw_rect)
		painter = QPainter(pixmap)
		if self.erase_mode:
			painter.setBrush(Qt.transparent)
			painter.setCompositionMode(QPainter.CompositionMode_Clear)
		else:
			painter.setBrush(Qt.red)
		painter.setPen(Qt.NoPen)
		painter.setRenderHint(QPainter.Antialiasing)
		painter.drawConvexPolygon(QPolygonF(plist))
		painter.drawEllipse(p1, s1, s1)
		return (pixmap, offset)

	def reset_draw(self):
		self.hist_pos = []
		self.hist_pressure = []
