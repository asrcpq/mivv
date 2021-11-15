from PyQt5.QtWidgets import QLabel

from mivv.image_view.image_view import Imageview

class ImageDisplay(QLabel):
	def __init__(self, parent = None):
		super().__init__(parent)
		self.image_view = Imageview(self)

	def get_zoom_level(self):
		return self.image_view.get_zoom_level()

	def load(self):
		self.image_view.load()

	def resizeEvent(self, e):
		self.image_view.resize(self.size())

	def key_handler(self, k):
		return self.image_view.key_handler(k)
