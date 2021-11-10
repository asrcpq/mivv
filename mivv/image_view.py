from PyQt5.QtWidgets import (
	QApplication, QLabel, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
)
from PyQt5.QtGui import QPixmap, QMovie, QTransform
from PyQt5.QtCore import Qt, QRectF, QSizeF, QPointF

from math import atan2, pi
import var

class Imageview(QGraphicsView):
	def __init__(self, parent = None):
		super().__init__(parent)
		self.setStyleSheet("background-color: black;")
		self.setMouseTracking(True)
		self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.content_size = None
		self.last_mouse_pos = None
		self.last_angle = None
		self.scaling_factor = 1.0
		self.flip = [1.0, 1.0]
		self.center = None
		self.original_scaling_factor = None
		self.original_scaling_limit = None
		self.mouse_mode = 0
		self.rotation = None
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
			raise Exception("wk or nk is not valid number")
		self.original_scaling_factor = osf
		self.set_move_dist()
		self.original_scaling_limit = [
			osf / var.zoom_level_limit[1],
			osf / var.zoom_level_limit[0],
		]

	def compute_view_size(self):
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
			raise Exception("wk or nk is not valid number")
		return QSizeF(w, h)

	def resizeEvent(self, _e):
		# original scaling factor is set in main_window
		self.render()

	def load(self):
		self.setCursor(Qt.WaitCursor)
		self.scaling_factor = 1.0
		self.flip = [1.0, 1.0]
		self.rotation = 0

		ty = var.image_loader.typelist[var.current_idx]
		filename = var.image_loader.filelist[var.current_idx]
		if ty == 1:
			pixmap = QPixmap(filename)
			self.content_size = pixmap.size()
			item = QGraphicsPixmapItem()
			item.setPixmap(pixmap)
			item.setTransformationMode(Qt.SmoothTransformation)
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
			raise Exception('Unreachable code.')
		self.set_original_scaling_factor()
		t = self.content_size / 2
		self.center = [t.width(), t.height()]
		scene.setSceneRect(QRectF(-5e6, -5e6, 1e7, 1e7))
		self.setScene(scene)
		self.setCursor(Qt.ArrowCursor)

	def render(self):
		if not self.content_size:
			return
		size = self.compute_view_size()
		sx = self.viewport().width() / size.width()
		sy = self.viewport().height() / size.height()
		if sx <= sy:
			k = sx
		elif sx > sy:
			k = sy
		else:
			raise Exception('Float error')
		qtrans = QTransform()
		qtrans.scale(k * self.flip[0], k * self.flip[1])
		qtrans.rotate(self.rotation)
		qtrans.translate(self.center[0], self.center[1])
		self.setTransform(qtrans)
		self.centerOn(self.center[0], self.center[1])

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
		if e.key() == Qt.Key_N:
			if var.keymod_shift:
				self.navigate_image(-1, False)
			else:
				self.navigate_image(1, False)
		elif e.key() == Qt.Key_G:
			if var.keymod_shift:
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
		self.move_dist = var.k_move * var.hidpi * self.scaling_factor / self.original_scaling_factor

	def key_handler_transform(self, e):
		if e.key() == Qt.Key_H:
			self.center[0] -= self.move_dist
		elif e.key() == Qt.Key_L:
			self.center[0] += self.move_dist
		elif e.key() == Qt.Key_J:
			self.center[1] += self.move_dist
		elif e.key() == Qt.Key_K:
			self.center[1] -= self.move_dist
		elif e.key() == Qt.Key_O:
			self.scale_view(var.scaling_mult, False)
		elif e.key() == Qt.Key_I:
			self.scale_view(1 / var.scaling_mult, False)
		elif e.key() == Qt.Key_1:
			self.scale_view(self.original_scaling_factor, True)
			self.set_move_dist()
		elif e.key() == Qt.Key_Underscore:
			self.flip[1] *= -1
		elif e.key() == Qt.Key_Bar:
			self.flip[0] *= -1
		elif e.key() == Qt.Key_W:
			t = self.content_size / 2
			self.center = [t.width(), t.height()]
			self.scale_view(1.0, True)
			self.rotation = 0
			self.set_move_dist()
		elif e.key() == Qt.Key_Less:
			self.rotation -= 90
		elif e.key() == Qt.Key_Greater:
			self.rotation += 90
		else:
			return False
		self.render()
		return True

	def key_handler(self, e):
		if self.key_handler_navigation(e):
			return
		if self.key_handler_transform(e):
			return

	def mouse_shift_rotate(self, pos):
		c = self.viewport().rect().center()
		p1 = pos - c
		angle = atan2(p1.x(), p1.y()) / pi * 180 * self.flip[0] * self.flip[1]
		if self.mouse_mode == 0:
			self.last_mouse_angle = angle
			self.mouse_mode = 3
			return
		d_angle = angle - self.last_mouse_angle
		if d_angle > var.image_move_rotate:
			k = int(d_angle / var.image_move_rotate)
			self.rotation -= var.image_move_rotate * k
			self.last_mouse_angle += var.image_move_rotate * k
		elif d_angle < -var.image_move_rotate:
			k = int(-d_angle / var.image_move_rotate)
			self.rotation += var.image_move_rotate * k
			self.last_mouse_angle -= var.image_move_rotate * k
		self.render()

	def mouse_ctrl_zoom(self, pos):
		if self.mouse_mode == 0:
			self.last_mouse_pos = pos
			self.mouse_mode = 1
			return
		self.setCursor(Qt.SizeVerCursor)
		dp = pos - self.last_mouse_pos
		if dp.y() > var.image_move_zoom:
			self.scale_view(var.scaling_mult_mouse, False)
			self.last_mouse_pos = pos
		elif dp.y() < -var.image_move_zoom:
			self.scale_view(1 / var.scaling_mult_mouse, False)
			self.last_mouse_pos = pos
		self.parent().set_label()
		self.render()

	def mouse_pan(self, pos):
		pos = QTransform()\
			.rotate(-self.rotation)\
			.scale(self.flip[0], self.flip[1])\
			.map(pos)
		if self.mouse_mode == 0:
			self.last_mouse_pos = pos
			self.mouse_mode = 2
			return
		self.setCursor(Qt.CrossCursor)
		dp = pos - self.last_mouse_pos
		view_size_w = self.compute_view_size().width()
		dp *= -view_size_w / self.width()
		self.center[0] += dp.x()
		self.center[1] += dp.y()
		self.last_mouse_pos = pos
		self.render()
		self.mouse_mode = 2

	def mouseMoveEvent(self, e):
		pos = e.localPos()
		if e.buttons() & Qt.MiddleButton:
			if self.mouse_mode == 3 or var.keymod_shift:
				return self.mouse_shift_rotate(pos)
			elif self.mouse_mode == 1 or var.keymod_control:
				return self.mouse_ctrl_zoom(pos)
			else:
				return self.mouse_pan(pos)
		elif e.buttons() & Qt.RightButton:
			pos = e.localPos()
			if self.mouse_mode == 0:
				self.last_mouse_pos = pos
				self.mouse_mode = 4
				self.setCursor(Qt.CrossCursor)
				return
			if self.mouse_mode != 4:
				return
			dp = pos - self.last_mouse_pos
			if dp.y() < -var.guesture_move:
				self.parent().grid_mode()
			elif dp.x() < -var.guesture_move:
				self.navigate_image(-1, False)
			elif dp.x() > var.guesture_move:
				self.navigate_image(1, False)
			else:
				return
			self.setCursor(Qt.ArrowCursor)
			self.mouse_mode = 5 # not 4
		else:
			self.setCursor(Qt.ArrowCursor)
			self.mouse_mode = 0
