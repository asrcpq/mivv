from PySide6.QtWidgets import QWidget, QLabel
from PySide6.QtGui import QFont, QFontMetrics, QColor, QPainter
from PySide6.QtCore import Qt, QRect

from mivv import var

class LabelStack(QWidget):
	def __init__(self, parent):
		super().__init__(parent)
		self.setAttribute(Qt.WA_TranslucentBackground)
		self.setAttribute(Qt.WA_TransparentForMouseEvents)
		self._labels = []
		self._labels_dict = {}
		font = QFont("monospace", var.font_size)
		self.bar_height = QFontMetrics(font).height()
		self._font = font
		self.w = 0
		self.h = 0
		self.update_size()

	def toggle_visible(self):
		if self.isVisible():
			self.hide()
		else:
			self.show()

	def set_label(self, keyword, string):
		if keyword not in self._labels_dict:
			idx = len(self._labels)
			self._labels_dict[keyword] = idx
			self._labels.append(string)
		else:
			idx = self._labels_dict[keyword]
			self._labels[idx] = string
		self.update()

	# ignore nonexistent
	def unset_label(self, keyword):
		idx = self._labels_dict.pop(keyword, None)
		if idx:
			del self._labels[idx]
		self.update()

	def _compute_geom(self, idx):
		l = 0
		t = self.h - self.bar_height * (idx + 1) - 1
		w = self.h
		h = self.bar_height
		return QRect(l, t, w, h)

	def update_size(self):
		r = self.parent().rect()
		self.w = r.width()
		self.h = r.height()
		for idx, label in enumerate(self._labels):
			rect = self._compute_geom(idx)
		self.update()

	def paintEvent(self, _e):
		for idx, _label in enumerate(self._labels):
			self.paint(idx)

	def paint(self, idx):
		text = self._labels[idx]
		p = QPainter(self);
		rect = self._compute_geom(idx)
		p.setFont(self._font)
		true_rect = p.boundingRect(rect, Qt.AlignLeft, text)
		w = true_rect.width() + 5
		true_rect = QRect(rect.left(), rect.top(), w, self.bar_height)
		p.setPen(Qt.NoPen)
		bgc = QColor(var.background)
		bgc.setAlpha(128)
		p.fillRect(true_rect, bgc);
		p.setPen(Qt.white)
		p.drawText(true_rect, Qt.AlignVCenter, text)
