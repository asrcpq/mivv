from PyQt5.QtWidgets import (
	QApplication, QWidget, QLabel, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
)
from PyQt5.QtGui import QPixmap, QMovie
from PyQt5.QtCore import Qt, QRectF, QPointF

import var

class Imageview(QGraphicsView):
	def __init__(self, parent = None):
		super().__init__(parent)
		self.setStyleSheet("background-color: black;")
		self.setMouseTracking(True)
		self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff);
		self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff);
		self.content_size = None
		self.last_mouse_pos = None
		self.scaling_factor = 1.0
		self.original_scaling_factor = 9e999
		self.original_scaling_limit = [-9e999, 9e999]
		self.mouse_mode = 0
		self.move_dist = 10

	def set_original_scaling_factor(self):
		wk = self.width() / self.content_size.width()
		hk = self.height() / self.content_size.height()
		# w bound
		if hk >= wk:
			osf = wk * var.hidpi
		elif wk > hk:
			osf = hk * var.hidpi
		else:
			raise(Exception("wk or nk is not valid number"))
		self.original_scaling_factor = osf
		self.original_scaling_limit = [
			osf / var.zoom_level_limit[1],
			osf / var.zoom_level_limit[0],
		]

	def compute_rect(self):
		wk = self.width() / self.content_size.width()
		hk = self.height() / self.content_size.height()
		# w bound
		if hk >= wk:
			w = self.content_size.width() * self.scaling_factor
			h = self.content_size.height() * hk / wk * self.scaling_factor
		elif wk > hk:
			w = self.content_size.width() * wk / hk * self.scaling_factor
			h = self.content_size.height() * self.scaling_factor
		else:
			raise(Exception("wk or nk is not valid number"))
		# return QRectF(0, 0, 500, 100)
		return QRectF(
			self.center[0] - w / 2,
			self.center[1] - h / 2,
			w,
			h,
		)

	def resizeEvent(self, event):
		# original scaling factor is set in main_window
		self.render()

	def load(self):
		self.scaling_factor = 1.0
		self.set_move_dist()

		ty = var.image_loader.typelist[var.current_idx]
		filename = var.image_loader.filelist[var.current_idx]

		if ty == 1:
			pixmap = QPixmap(filename)
			self.content_size = pixmap.size()
			item = QGraphicsPixmapItem()
			item.setPixmap(pixmap)
			item.setTransformationMode(Qt.SmoothTransformation);
			scene = QGraphicsScene()
			scene.addItem(item)
		elif ty == 2:
			movie = QMovie(filename)
			movie.start()
			label = QLabel()
			self.content_size = movie.currentPixmap().size()
			label.resize(self.content_size)
			label.setMovie(movie)
			scene = QGraphicsScene()
			scene.addWidget(label)
		else:
			raise(Exception('Unreachable code.'))
		self.set_original_scaling_factor()
		t = self.content_size / 2
		self.center = [t.width(), t.height()]
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
		if self.scaling_factor < self.original_scaling_limit[0]:
			self.scaling_factor = self.original_scaling_limit[0]
		if self.scaling_factor > self.original_scaling_limit[1]:
			self.scaling_factor = self.original_scaling_limit[1]
		self.set_move_dist()

	def key_handler_navigation(self, e):
		modifiers = QApplication.keyboardModifiers()
		if e.key() == Qt.Key_N:
			if modifiers == Qt.ShiftModifier:
				self.navigate_image(-1, False)
			else:
				self.navigate_image(1, False)
		elif e.key() == Qt.Key_G:
			if modifiers == Qt.ShiftModifier:
				self.navigate_image(len(var.image_loader.filelist) - 1, True)
			else:
				self.navigate_image(0, True)
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
		pw = self.content_size.width()
		ph = self.content_size.height()
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

	def key_handler_transform(self, e):
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
		elif e.key() == Qt.Key_0:
			self.scale_view(self.original_scaling_factor, True)
			self.set_move_dist()
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

	def key_handler(self, e):
		if self.key_handler_navigation(e):
			return
		if self.key_handler_transform(e):
			return

	def mouseMoveEvent(self, e):
		if e.buttons() & Qt.MiddleButton:
			modifiers = QApplication.keyboardModifiers()
			# ctrl zoom
			if self.mouse_mode == 1 or modifiers == Qt.ControlModifier:
				if self.mouse_mode == 0:
					self.last_mouse_pos = e.localPos()
					self.mouse_mode = 1
					return
				self.setCursor(Qt.SizeVerCursor)
				dp = e.localPos() - self.last_mouse_pos
				if dp.y() > var.image_move_zoom:
					self.scale_view(var.scaling_mult_mouse, False)
					self.last_mouse_pos = e.localPos()
				elif dp.y() < -var.image_move_zoom:
					self.scale_view(1 / var.scaling_mult_mouse, False)
					self.last_mouse_pos = e.localPos()
				self.parent().set_label()
				self.render()
			# pan
			else:
				if self.mouse_mode == 0:
					self.last_mouse_pos = e.localPos()
					self.mouse_mode = 2
					return
				self.setCursor(Qt.CrossCursor)
				dp = e.localPos() - self.last_mouse_pos
				dp *= var.mouse_factor * self.scaling_factor
				self.center[0] += dp.x()
				self.center[1] += dp.y()
				self.last_mouse_pos = e.localPos()
				self.calibrate_center()
				self.render()
				self.mouse_mode = 2
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
