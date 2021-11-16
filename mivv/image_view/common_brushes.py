# brush method
# draw()
# input: point sequence
# output: update patch, offset

from PyQt5.QtGui import QPainter, QPen, QPixmap
from PyQt5.QtCore import Qt, QPoint, QPointF, QRectF
from scipy import interpolate

class DummyBrush():
	def __init__(self):
		self.size = 5
		self.hist_pos = []
		self.hist_pressure = []
		self.s = 0
		self.spacing = 1

	def draw(self, pos, pressure):
		s = self.size
		self.hist_pos.append(pos)
		self.hist_pressure.append(pressure)
		# len can't be 0 or 2
		if len(self.hist_pos) == 1:
			# double initial point
			self.hist_pos.append(pos)
			self.hist_pressure.append(pressure)
			return (None, None)
		if len(self.hist_pos) == 3:
			return (None, None)
		draw_rect = QRectF(self.hist_pos[-3], self.hist_pos[-2]) \
			.normalized() \
			.adjusted(-s, -s, s, s) \
			.toAlignedRect()
		offset = draw_rect.topLeft()
		pixmap = QPixmap(draw_rect.size())
		pixmap.fill(Qt.transparent)
		length = (lambda l: (l.x() ** 2 + l.y() ** 2) ** 0.5)(self.hist_pos[-3] - self.hist_pos[-2])
		sax = [x * length for x in [-1, 0, 1, 2]]
		splrep_x = interpolate.splrep(
			sax,
			[
				self.hist_pos[-4].x(),
				self.hist_pos[-3].x(),
				self.hist_pos[-2].x(),
				self.hist_pos[-1].x(),
			],
		)
		splrep_y = interpolate.splrep(
			sax,
			[
				self.hist_pos[-4].y(),
				self.hist_pos[-3].y(),
				self.hist_pos[-2].y(),
				self.hist_pos[-1].y(),
			],
		)
		s_list = []
		while self.s < length:
			self.s += self.spacing
			s_list.append(self.s)
		self.s -= length
		try:
			x_list = interpolate.splev(s_list, splrep_x)
			y_list = interpolate.splev(s_list, splrep_y)
		except ValueError: # all zero
			return (None, None)
		painter = QPainter(pixmap)
		painter.setRenderHint(QPainter.Antialiasing)
		painter.setBrush(Qt.red)
		painter.setPen(Qt.NoPen)
		for x, y in zip(x_list, y_list):
			painter.drawEllipse(x - offset.x(), y - offset.y(), self.size, self.size)
		return (pixmap, offset)

	def reset_draw(self):
		self.hist_pos = []
		self.hist_pressure = []
