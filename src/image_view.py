from PyQt5.QtWidgets import (
	QApplication, QWidget, QLabel, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
)
from PyQt5.QtGui import QPixmap, QKeyEvent
from PyQt5.QtCore import Qt, QRectF, QPointF

import var

class Imageview(QGraphicsView):
	def __init__(self, parent = None):
		super().__init__(parent)
		self.setStyleSheet("background-color: black;")
		#self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff);
		#self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff);
		self.pixmap = None
		self.pixmap_item = QGraphicsPixmapItem()
		self.scaling_factor = 1.0
		self.scaling_mult = 1.3
		self.reload()

	def compute_rect(self):
		img_size = self.pixmap.size()
		wk = img_size.width() / self.width()
		hk = img_size.height() / self.height()
		# w bound
		if wk > hk:
			w = img_size.width() * self.scaling_factor
			h = img_size.height() * wk / hk * self.scaling_factor
		else:
			w = img_size.width() * hk / wk * self.scaling_factor
			h = img_size.height() * self.scaling_factor
		# return QRectF(0, 0, 500, 100)
		return QRectF(
			(img_size.width() - w) / 2,
			(img_size.height() - h) / 2,
			w,
			h,
		)

	def resizeEvent(self, event):
		self.render()

	def reload(self):
		self.pixmap = QPixmap(var.image_loader.filelist[var.current_idx])
		self.pixmap_item.setPixmap(self.pixmap)
		scene = QGraphicsScene()
		scene.addItem(self.pixmap_item)
		self.setScene(scene)
	
	def render(self):
		rect = self.compute_rect()
		self.fitInView(rect)
		print(self.sceneRect())

	def key_handler(self, e: QKeyEvent):
		if e.key() == Qt.Key_Space or e.key() == Qt.Key_N:
			var.current_idx += 1
			if var.current_idx >= len(var.image_loader.filelist):
				var.current_idx = len(var.image_loader.filelist) - 1
			else:
				self.reload()
		elif e.key() == Qt.Key_G:
			modifiers = QApplication.keyboardModifiers()
			if modifiers == Qt.ShiftModifier:
				var.current_idx = len(var.image_loader.filelist) - 1
			else:
				var.current_idx = 0
			self.reload()
		elif e.key() == Qt.Key_Backspace or e.key() == Qt.Key_P:
			var.current_idx -= 1
			if var.current_idx < 0:
				var.current_idx = 0
			else:
				self.reload()
		elif e.key() == Qt.Key_O:
			self.scaling_factor /= self.scaling_mult
		elif e.key() == Qt.Key_I:
			self.scaling_factor *= self.scaling_mult
		elif e.key() == Qt.Key_0:
			self.scaling_factor = 0.99
		else:
			return
		self.render()
