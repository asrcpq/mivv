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
		self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff);
		self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff);
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
			self.center[0] - w / 2,
			self.center[1] - h / 2,
			w,
			h,
		)

	def resizeEvent(self, event):
		self.render()

	def reload(self):
		self.pixmap = QPixmap(var.image_loader.filelist[var.current_idx])
		self.pixmap_item.setPixmap(self.pixmap)
		t = self.pixmap.size() / 2
		self.center = [t.width(), t.height()]
		scene = QGraphicsScene()
		scene.addItem(self.pixmap_item)
		self.setScene(scene)
	
	def render(self):
		rect = self.compute_rect()
		self.fitInView(rect)

	def key_handler_navigation(self, e: QKeyEvent):
		if e.key() == Qt.Key_Space or e.key() == Qt.Key_N:
			var.current_idx += 1
			if var.current_idx >= len(var.image_loader.filelist):
				var.current_idx = len(var.image_loader.filelist) - 1
		elif e.key() == Qt.Key_G:
			modifiers = QApplication.keyboardModifiers()
			if modifiers == Qt.ShiftModifier:
				var.current_idx = len(var.image_loader.filelist) - 1
				var.current_idx = 0
		elif e.key() == Qt.Key_Backspace or e.key() == Qt.Key_P:
			var.current_idx -= 1
			if var.current_idx < 0:
				var.current_idx = 0
		else:
			return False
		self.reload()
		self.render()
		return True

	def key_handler_transform(self, e: QKeyEvent):
		x_mod = False
		y_mod = False
		if e.key() == Qt.Key_H:
			self.center[0] -= var.delta_move
			x_mod = True
		elif e.key() == Qt.Key_L:
			self.center[0] += var.delta_move
			x_mod = True
		elif e.key() == Qt.Key_J:
			self.center[1] += var.delta_move
			y_mod = True
		elif e.key() == Qt.Key_K:
			self.center[1] -= var.delta_move
			y_mod = True
		elif e.key() == Qt.Key_O:
			self.scaling_factor /= self.scaling_mult
			x_mod = True
			y_mod = True
		elif e.key() == Qt.Key_I:
			self.scaling_factor *= self.scaling_mult
			x_mod = True
			y_mod = True
		elif e.key() == Qt.Key_0:
			self.scaling_factor = 0.99
			x_mod = True
			y_mod = True
		else:
			return False
		self.render()
		t = QRectF(
			self.mapToScene(0, 0),
			self.mapToScene(self.width(), self.height()),
		).center()
		if x_mod:
			self.center[0] = t.x()
		if y_mod:
			self.center[1] = t.y()
		return True

	def key_handler(self, e: QKeyEvent):
		if self.key_handler_navigation(e):
			return
		if self.key_handler_transform(e):
			return
