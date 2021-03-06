from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt

class Thumbnail(QLabel):
	def __init__(self, parent, x, y):
		super().__init__(parent)
		self.setAlignment(Qt.AlignCenter)
		self.coord = [x, y]
		self.setAttribute(Qt.WA_TransparentForMouseEvents)
