from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtGui import QPixmap, QKeyEvent
from PyQt5.QtCore import Qt

import var

class Imageview(QWidget):
	def __init__(self, parent = None):
		super().__init__(parent)
		self.setStyleSheet("background-color: black;")
		self.label = QLabel("Imageview", self)
		self.label.setAlignment(Qt.AlignCenter)
		self.scaling_mult = 1.3
		self.initialize()

	def resizeEvent(self, event):
		self.render()

	def initialize(self):
		self.scaling_factor = 0.99
		self.reload()
		self.render()

	def reload(self):
		self.pixmap = QPixmap(var.image_loader.filelist[var.current_idx])
	
	def render(self):
		pixmap_resize = self.pixmap.scaled(
			int(self.width() * self.scaling_factor),
			int(self.height() * self.scaling_factor),
			Qt.KeepAspectRatio,
			Qt.SmoothTransformation,
		)
		self.label.setPixmap(pixmap_resize)
		self.label.resize(self.width(), self.height())

	def key_handler(self, e: QKeyEvent):
		if e.key() == Qt.Key_Space or e.key() == Qt.Key_N:
			var.current_idx += 1
			if var.current_idx >= len(var.image_loader.filelist):
				var.current_idx = len(var.image_loader.filelist) - 1
		elif e.key() == Qt.Key_Backspace or e.key() == Qt.Key_P:
			var.current_idx -= 1
			if var.current_idx < 0:
				var.current_idx = 0
		elif e.key() == Qt.Key_O:
			self.scaling_factor /= self.scaling_mult
		elif e.key() == Qt.Key_I:
			self.scaling_factor *= self.scaling_mult
		elif e.key() == Qt.Key_0:
			self.scaling_factor = 0.99
		else:
			return
		self.reload()
		self.render()
