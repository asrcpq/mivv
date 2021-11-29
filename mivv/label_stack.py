from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QFont, QColor, QPainter
from PyQt5.QtCore import Qt

from mivv import var

class LabelStack(QWidget):
	def __init__(self, parent = None):
		super().__init__(parent)
		self.labels = []

	def set_text(self, idx, text):
		pass

	def push(self):
		self.labels.append(LSLabel(self))

	def pop(self):
		self.labels.pop()

class LSLabel(QWidget):
	def __init__(self, parent = None):
		super().__init__(parent)
		self._font = QFont("monospace", var.bar_height - 1)
		self.text = ""

	def font(self):
		return self._font

	def set_text(self, string):
		self.text = string
		self.update()

	def set_geom(self, rect):
		self.rect = rect

	def paintEvent(self, _e):
		# todo check paint time here
		bgc = QColor(var.background)
		bgc.setAlpha(100)
		p = QPainter(self);
		p.fillRect(self.rect(), bgc);
		p.setPen(Qt.white)
		p.setFont(self._font)
		p.drawText(self.rect(), Qt.AlignLeft, self.text)
