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

	def draw(self, pos, pressure):
		self.hist_pos.append(pos)
		self.hist_pressure.append(pressure)
		# len can't be 0 or 2
		if len(self.hist_pos) == 1:
			return (None, None)
		s0 = pressure * self.size
		s1 = self.hist_pressure[-2] * self.size
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
		pixmap = QPixmap(draw_rect.size())
		pixmap.fill(Qt.transparent)
		painter = QPainter(pixmap)
		painter.setBrush(Qt.red)
		painter.setPen(Qt.NoPen)
		painter.setRenderHint(QPainter.Antialiasing)
		plist = [
			s0 * rnu_vec + p0,
			s1 * rnu_vec + p1,
			-s1 * rnu_vec + p1,
			-s0 * rnu_vec + p0,
		]
		painter.drawConvexPolygon(QPolygonF(plist))
		painter.drawEllipse(p1, s1, s1)
		return (pixmap, offset)

	def reset_draw(self):
		self.hist_pos = []
		self.hist_pressure = []
