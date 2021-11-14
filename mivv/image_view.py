from math import atan2, pi
import sys

from PyQt5.QtWidgets import (
	QApplication, QLabel, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
)
from PyQt5.QtGui import QPixmap, QMovie, QTransform, QImageReader, QImage
from PyQt5.QtCore import (
	Qt, QRectF, QSizeF, QPointF, QEvent,
	pyqtSlot, pyqtSignal, QThread
)

from canvas import CanvasItem
import var

class Imageview(QGraphicsView):
	load_data = pyqtSignal(str, int)

	def __init__(self, parent = None):
		super().__init__(parent)
		self.setStyleSheet(f"background-color: {var.background};")
		self.setMouseTracking(True)
		self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.content_size = None
		self.content = None
		self.canvas_item = None
		self.last_mouse_pos = None
		self.last_angle = None
		self.scaling_factor = None
		self.flip = [1.0, 1.0]
		self.center = None
		self.original_scaling_factor = None
		self.original_scaling_limit = None
		self.mouse_mode = 0
		self.rotation = None
		self.move_dist = 10
		self.loader_thread = _ContentLoaderThread()
		self.loader_thread.result.connect(self.get_result)
		self.load_data.connect(self.loader_thread.feed_data)

	def _set_original_scaling_factor(self):
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
		self.original_scaling_limit = [
			osf / var.zoom_level_limit[1],
			osf / var.zoom_level_limit[0],
		]

	def _compute_view_size(self):
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
		# open failed
		if not self.content:
			self.parent().set_label()
			return
		# original scaling factor is set in main_window
		self._set_original_scaling_factor()
		self._scale_view(1.0, False) # prevent overflow
		self.parent().set_label()
		self.render()

	def get_result(self, content):
		scene = QGraphicsScene()
		if self.ty == 1:
			content = QPixmap.fromImage(content)
			self.content = content
			if content.isNull():
				var.logger.error(f"Load image error: {filename}")
				self.content = None
				return False
			item = QGraphicsPixmapItem()
			item.setPixmap(content)
			item.setTransformationMode(Qt.SmoothTransformation)
			scene.addItem(item)
		elif self.ty == 2:
			if not content.isValid():
				var.logger.error(f"Load movie error: {filename}")
				self.content = None
				return False
			content.start()
			self.content = content
			label = QLabel()
			label.resize(self.content_size)
			label.setMovie(content)
			scene.addWidget(label)
		else:
			var.logger.error(f"Unknown type: {ty}")
			return False
		self.canvas_item = CanvasItem(self.content_size)
		scene.addItem(self.canvas_item)
		scene.setSceneRect(QRectF(-5e6, -5e6, 1e7, 1e7))
		self.setScene(scene)

	def load(self):
		var.logger.info(f"Start loading id {var.current_idx}")
		self.setCursor(Qt.WaitCursor)
		self.flip = [1.0, 1.0]
		self.rotation = 0

		self.ty = var.image_loader.typelist[var.current_idx]
		filename = var.image_loader.filelist[var.current_idx]
		self.load_data.emit(filename, self.ty)
		self.content_size = QImageReader(filename).size()
		if self.content_size.width() == -1:
			var.logger.error(f"Load image size error: {filename}")
			self.content = None
			return False
		scene = QGraphicsScene()
		pixmap = var.image_loader.pixmaps[var.current_idx].scaled(self.content_size)
		self.content = pixmap
		item = QGraphicsPixmapItem()
		item.setPixmap(pixmap)
		scene.addItem(item)
		self._set_original_scaling_factor()
		self._scale_view(1.0, True)
		self._set_move_dist()
		self._set_content_center()
		scene.setSceneRect(QRectF(-5e6, -5e6, 1e7, 1e7))
		self.setScene(scene)
		self.setCursor(Qt.ArrowCursor)
		return True

	def render(self):
		if not self.content_size:
			return
		size = self._compute_view_size()
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

	def _scale_view(self, offset, abs_k = False):
		if abs_k:
			self.scaling_factor = offset
		else:
			self.scaling_factor *= offset
		if self.scaling_factor < self.original_scaling_limit[0]:
			self.scaling_factor = self.original_scaling_limit[0]
		if self.scaling_factor > self.original_scaling_limit[1]:
			self.scaling_factor = self.original_scaling_limit[1]
		self._set_move_dist()

	def _key_handler_navigation(self, k):
		if k == Qt.Key_N:
			if var.keymod_shift:
				self.navigate_image(-1, False)
			else:
				self.navigate_image(1, False)
		elif k == Qt.Key_P:
			self.navigate_image(-1, False)
		elif k == Qt.Key_G:
			if var.keymod_shift:
				self.navigate_image(len(var.image_loader.filelist) - 1, True)
			else:
				self.navigate_image(0, True)
		elif k == Qt.Key_R:
			self.load()
			self.render()
		else:
			return False
		return True

	def _set_content_center(self):
		t = self.content_size / 2
		self.center = [t.width() - 0.5, t.height() - 0.5]

	def _set_move_dist(self):
		self.move_dist = var.k_move * var.hidpi * self.scaling_factor / self.original_scaling_factor

	def _key_handler_transform(self, k):
		if k == Qt.Key_H or k == Qt.Key_Left:
			self.center[0] -= self.move_dist
		elif k == Qt.Key_L or k == Qt.Key_Right:
			self.center[0] += self.move_dist
		elif k == Qt.Key_J or k == Qt.Key_Down:
			self.center[1] += self.move_dist
		elif k == Qt.Key_K or k == Qt.Key_Up:
			self.center[1] -= self.move_dist
		elif k == Qt.Key_O:
			self._scale_view(var.scaling_mult, False)
		elif k == Qt.Key_I:
			self._scale_view(1 / var.scaling_mult, False)
		elif k == Qt.Key_1:
			self._scale_view(self.original_scaling_factor, True)
			self._set_move_dist()
		elif k == Qt.Key_Underscore:
			self.flip[1] *= -1
		elif k == Qt.Key_Bar:
			self.flip[0] *= -1
		elif k == Qt.Key_W:
			self._set_content_center()
			self._scale_view(1.0, True)
			self.rotation = 0
			self._set_move_dist()
		elif k == Qt.Key_Less:
			self.rotation -= 90
		elif k == Qt.Key_Greater:
			self.rotation += 90
		else:
			return False
		self.render()
		return True

	def _key_handler_movie(self, k):
		if not isinstance(self.content, QMovie):
			return False
		if k == Qt.Key_Space:
			s = self.content.state()
			if s == QMovie.Running:
				self.content.setPaused(True)
			elif s == QMovie.NotRunning or s == QMovie.Paused:
				self.content.setPaused(False)
			else:
				var.logger.error("Unknown state")
		if k == Qt.Key_S:
			n = self.content.currentFrameNumber()
			var.logger.debug(f"Frame before keypress: {n}")
			self.content.jumpToFrame(n + 1)
		else:
			return False
		return True

	def _key_handler_canvas(self, k):
		if k == Qt.Key_C:
			self.scene().removeItem(self.canvas_item)
			self.canvas_item = CanvasItem(self.content_size)
			self.scene().addItem(self.canvas_item)
		else:
			return False
		return True

	def key_handler(self, k):
		if self._key_handler_navigation(k):
			return
		if not self.content:
			var.logger.info("Key ignored, because content is invalid.")
			return
		if self._key_handler_transform(k):
			return
		if self._key_handler_movie(k):
			return
		if self._key_handler_canvas(k):
			return

	def _mouse_shift_rotate(self, pos):
		c = self.viewport().rect().center()
		p1 = pos - c
		angle = atan2(p1.x(), p1.y()) / pi * 180 * self.flip[0] * self.flip[1]
		if self.mouse_mode != 3:
			self.last_mouse_angle = angle
			self.mouse_mode = 3
			self.setCursor(Qt.ClosedHandCursor)
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

	def _mouse_ctrl_zoom(self, pos):
		if self.mouse_mode != 1:
			self.last_mouse_pos = pos
			self.mouse_mode = 1
			return
		self.setCursor(Qt.SizeVerCursor)
		dp = pos - self.last_mouse_pos
		if dp.y() > var.image_move_zoom:
			self._scale_view(var.scaling_mult_mouse, False)
			self.last_mouse_pos = pos
		elif dp.y() < -var.image_move_zoom:
			self._scale_view(1 / var.scaling_mult_mouse, False)
			self.last_mouse_pos = pos
		self.parent().set_label()
		self.render()

	def _mouse_pan(self, pos):
		pos = QTransform()\
			.rotate(-self.rotation)\
			.scale(self.flip[0], self.flip[1])\
			.map(pos)
		if self.mouse_mode != 2:
			self.last_mouse_pos = pos
			self.mouse_mode = 2
			return
		self.setCursor(Qt.CrossCursor)
		dp = pos - self.last_mouse_pos
		view_size_w = self._compute_view_size().width()
		dp *= -view_size_w / self.width()
		self.center[0] += dp.x()
		self.center[1] += dp.y()
		self.last_mouse_pos = pos
		self.render()
		self.mouse_mode = 2

	def tabletEvent(self, e):
		pos = e.posF()
		pos = self.mapToScene(pos.x(), pos.y())
		ty = e.type()
		if (
			not self.canvas_item.on_draw and \
			e.buttons() == Qt.LeftButton and \
			ty == QEvent.TabletPress
		):
			var.logger.debug("Tablet press")
			self.canvas_item.update_pos(pos)
			self.canvas_item.on_draw = True
			return
		if not self.canvas_item.on_draw:
			return
		if ty == QEvent.TabletRelease:
			var.logger.debug("Tablet release")
			self.canvas_item.update_pos(pos)
			self.canvas_item.draw()
			self.canvas_item.on_draw = False
			return
		if e.buttons() != Qt.LeftButton:
			self.canvas_item.on_draw = False
			False
		if ty == QEvent.TabletMove:
			self.canvas_item.update_pos(pos)
			self.canvas_item.draw()

	def mouseMoveEvent(self, e):
		pos = e.localPos()
		if e.buttons() & Qt.MiddleButton:
			if self.mouse_mode == 3:
				return self._mouse_shift_rotate(pos)
			elif self.mouse_mode == 1:
				return self._mouse_ctrl_zoom(pos)
			elif var.keymod_shift:
				return self._mouse_shift_rotate(pos)
			elif var.keymod_control:
				return self._mouse_ctrl_zoom(pos)
			else:
				return self._mouse_pan(pos)
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

class _ContentLoaderThread(QThread):
	result = pyqtSignal(object)

	def __init__(self):
		QThread.__init__(self)
		self.filenames = None
		self.run_flag = False
		self.tys = None

	def feed_data(self, filename, ty):
		self.filename = filename
		self.ty = ty
		self.run_flag = True
		self.start()

	def run(self):
		while self.run_flag:
			self.run_flag = False
			if self.ty == 1:
				result = QImage(self.filename)
			elif self.ty == 2:
				result = QMovie(self.filename)
			else:
				result = None
			if self.run_flag:
				continue
			self.result.emit(result)

	def stop(self):
		self.wait()
