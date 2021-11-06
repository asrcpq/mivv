from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt

class Thumbnail(QLabel):
	def __init__(self, parent, x, y):
		super().__init__(parent)
		self.setMouseTracking(True)
		self.setAlignment(Qt.AlignCenter)
		self.coord = [x, y]

	def mousePressEvent(self, e):
		if e.buttons() & Qt.LeftButton:
			self.parent().cursor_select(self.coord[0], self.coord[1])
