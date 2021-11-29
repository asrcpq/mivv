from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPixmap, QPainter, QColor
from PyQt5.QtCore import Qt

from mivv.image_view.image_view import Imageview
from mivv.keydef import Keydef
from mivv import var

class ImageDisplay(QLabel):
	def __init__(self, parent = None):
		super().__init__(parent)
		self.image_view = Imageview(self)
		self.background = None
		if var.chessboard_background:
			self.set_background()

	def get_zoom_level(self):
		return self.image_view.get_zoom_level()

	def load(self):
		self.image_view.load()

	def set_background(self):
		background = QPixmap(self.size())
		block_size = 25
		painter = QPainter(background)
		painter.setPen(Qt.NoPen)
		for i in range(self.width() // block_size + 1):
			for j in range(self.height() // block_size + 1):
				if (i + j) % 2 == 0:
					painter.setBrush(QColor(255, 255, 255))
				else:
					painter.setBrush(QColor(192, 192, 192))
				painter.drawRect(
					i * block_size, j * block_size,
					block_size, block_size,
				)
		self.setPixmap(background)
		self.background = background

	# if string is empty, reset with filename
	def override_label(self, string):
		if not string:
			self.parent().set_fn_label_filename()
		else:
			self.parent().set_fn_label_string(string)

	def resizeEvent(self, _e):
		if self.background:
			self.set_background()
		self.image_view.resize(self.size())

	def key_handler(self, k, is_release, is_auto_repeat):
		if k == Keydef.image_chessboard and not is_release:
			if self.background:
				self.background = None
				self.clear()
			else:
				self.set_background()
			return True
		return self.image_view.key_handler(k, is_release, is_auto_repeat)
