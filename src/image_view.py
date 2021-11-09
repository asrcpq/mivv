from PyQt5.QtWidgets import (
	QApplication, QWidget, QLabel, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
)
from PyQt5.QtGui import QPixmap, QKeyEvent, QMouseEvent
from PyQt5.QtCore import Qt, QRectF, QPointF

import var

class Imageview(QGraphicsView):
	def __init__(self, parent = None):
		super().__init__(parent)
		self.setStyleSheet("background-color: black;")
		self.setMouseTracking(True)
		self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff);
		self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff);
		self.size = None
		self.last_mouse_pos = None
		self.scaling_factor = 1.0
		self.mouse_mode = 0
		self.move_dist = 10
		self.load()

	def compute_rect(self):
		img_size = self.size
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

	def load(self):
		self.scaling_factor = 1.0
		self.set_move_dist()

		pixmap = QPixmap(var.image_loader.filelist[var.current_idx])
		self.size = pixmap.size()
		t = self.size / 2
		self.center = [t.width(), t.height()]

		item = QGraphicsPixmapItem()
		item.setPixmap(pixmap)
		item.setTransformationMode(Qt.SmoothTransformation);

		scene = QGraphicsScene()
		scene.addItem(item)
		self.setScene(scene)
	
	def render(self):
		rect = self.compute_rect()
		self.fitInView(rect)

	def navigate_image(self, offset, abs_pos = False):
		old_idx = var.current_idx
		if abs_pos:
			var.current_idx = offset
		else:
			var.current_idx += offset
		if var.current_idx >= len(var.image_loader.filelist):
			var.current_idx = len(var.image_loader.filelist) - 1
		if var.current_idx < 0:
			var.current_idx = 0
		if old_idx == var.current_idx:
			return
		self.load()
		self.render()

	def scale_view(self, offset, abs_k = False):
		if abs_k:
			self.scaling_factor = offset
		else:
			self.scaling_factor *= offset
		self.set_move_dist()

	def key_handler_navigation(self, e: QKeyEvent):
		if e.key() == Qt.Key_Space or e.key() == Qt.Key_N:
			self.navigate_image(1, False)
		elif e.key() == Qt.Key_G:
			modifiers = QApplication.keyboardModifiers()
			if modifiers == Qt.ShiftModifier:
				self.navigate_image(len(var.image_loader.filelist) - 1, True)
			else:
				self.navigate_image(0, True)
		elif e.key() == Qt.Key_Backspace or e.key() == Qt.Key_P:
			self.navigate_image(-1, False)
		elif e.key() == Qt.Key_R:
			self.load()
			self.render()
		else:
			return False
		return True

	def set_move_dist(self):
		self.move_dist = var.k_move * self.scaling_factor

	def calibrate_center(self, x_mod = True, y_mod = True):
		t = QRectF(
			self.mapToScene(0, 0),
			self.mapToScene(self.width(), self.height()),
		)
		swh = t.width() / 2
		shh = t.height() / 2
		pw = self.size.width()
		ph = self.size.height()
		if t.width() > pw:
			self.center[0] = pw / 2
		elif self.center[0] < swh:
			self.center[0] = swh
		elif self.center[0] > pw - swh:
			self.center[0] = pw - swh
		if t.height() > ph:
			self.center[1] = ph / 2
		elif self.center[1] < shh:
			self.center[1] = shh
		elif self.center[1] > ph - shh:
			self.center[1] = ph - shh
		return

	def key_handler_transform(self, e: QKeyEvent):
		x_mod = False
		y_mod = False
		if e.key() == Qt.Key_H:
			self.center[0] -= self.move_dist
			x_mod = True
		elif e.key() == Qt.Key_L:
			self.center[0] += self.move_dist
			x_mod = True
		elif e.key() == Qt.Key_J:
			self.center[1] += self.move_dist
			y_mod = True
		elif e.key() == Qt.Key_K:
			self.center[1] -= self.move_dist
			y_mod = True
		elif e.key() == Qt.Key_O:
			self.scale_view(var.scaling_mult, False)
			x_mod = True
			y_mod = True
		elif e.key() == Qt.Key_I:
			self.scale_view(1 / var.scaling_mult, False)
			x_mod = True
			y_mod = True
		elif e.key() == Qt.Key_W:
			self.scale_view(1.0, True)
			self.set_move_dist()
			x_mod = True
			y_mod = True
		else:
			return False
		self.calibrate_center(x_mod, y_mod)
		self.render()
		return True

	def key_handler(self, e: QKeyEvent):
		if self.key_handler_navigation(e):
			return
		if self.key_handler_transform(e):
			return

	def mouseMoveEvent(self, e: QMouseEvent):
		if e.buttons() & Qt.MiddleButton:
			if self.mouse_mode != 1:
				self.last_mouse_pos = e.localPos()
				self.mouse_mode = 1
				return
			modifiers = QApplication.keyboardModifiers()
			# ctrl zoom
			if modifiers == Qt.ControlModifier:
				self.setCursor(Qt.SizeVerCursor)
				dp = e.localPos() - self.last_mouse_pos
				if dp.y() > var.image_move_zoom:
					self.scale_view(var.scaling_mult_mouse, False)
					self.last_mouse_pos = e.localPos()
				elif dp.y() < -var.image_move_zoom:
					self.scale_view(1 / var.scaling_mult_mouse, False)
					self.last_mouse_pos = e.localPos()
				self.render()
			# pan
			else:
				self.setCursor(Qt.CrossCursor)
				dp = e.localPos() - self.last_mouse_pos
				dp *= var.mouse_factor * self.scaling_factor
				self.center[0] += dp.x()
				self.center[1] += dp.y()
				self.last_mouse_pos = e.localPos()
				self.calibrate_center()
				self.render()
		elif e.buttons() & Qt.RightButton:
			self.parent().grid_mode()
		elif e.buttons() & Qt.LeftButton:
			if self.mouse_mode != 3:
				self.mouse_mode = 3
				if e.localPos().x() > self.width() / 2:
					self.navigate_image(1, False)
				else:
					self.navigate_image(-1, False)
				self.parent().set_label()
		else:
			if e.localPos().x() > self.width() / 2:
				self.setCursor(Qt.ArrowCursor)
			else:
				self.setCursor(Qt.PointingHandCursor)
			self.mouse_mode = 0
