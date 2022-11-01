from math import atan2, pi

from PySide6.QtWidgets import (
	QLabel, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
)
from PySide6.QtGui import QPixmap, QMovie, QImageReader
from PySide6.QtCore import Qt, QRectF, QSizeF, QEvent, Signal, QPointF
from PySide6.QtSvgWidgets import QGraphicsSvgItem

from mivv import var
from mivv.keydef import Keydef
from .canvas import CanvasItem
from .viewport_data import _ViewportData
from .content_loader_thread import _ContentLoaderThread

class Imageview(QGraphicsView):
	load_data = Signal(str, int)

	def __init__(self, parent = None):
		super().__init__(parent)
		#self.setStyleSheet(f"background-color: {var.background};")
		self.setAttribute(Qt.WA_TranslucentBackground)
		self.setMouseTracking(True)
		self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.setFocusPolicy(Qt.NoFocus)
		self.content_size: QSizeF = QSizeF()
		self.old_content_size: QSizeF = QSizeF()
		self.content = None
		self.ty = None
		self.canvas_item = None
		self.canvas_scaling_factor = 1.0
		self.last_mouse_pos = None
		self.last_mouse_angle = None
		self.last_angle = None
		self.mouse_mode = 0
		self.viewport_data = _ViewportData()
		self.move_dist = 10
		self.loader_thread = _ContentLoaderThread()
		self.loader_thread.result.connect(self.update_content)
		self.load_data.connect(self.loader_thread.feed_data)
		self.last_content_item = None # thumbnail or image(gif mode)

		# initialize again, because main_window is not yet visible,
		# the geometry is default to 100x30
		# default fill is implemented by scale 1x which will be restricted by scaling range
		self.setGeometry(var.default_geom)

	def _set_original_scaling_factor(self):
		wk = self.width() / self.content_size.width()
		hk = self.height() / self.content_size.height()
		self.viewport_data.set_original_scaling_factor(wk, hk)

	def _compute_view_size(self):
		wk = self.width() / self.content_size.width()
		hk = self.height() / self.content_size.height()
		scaling_factor = self.viewport_data.scaling_factor
		# w bound
		if hk >= wk:
			w = self.content_size.width() * scaling_factor
			h = self.content_size.height() * hk / wk * scaling_factor
		elif wk > hk:
			w = self.content_size.width() * wk / hk * scaling_factor
			h = self.content_size.height() * scaling_factor
		else:
			raise Exception("wk or nk is not valid number")
		return QSizeF(w, h)

	def resizeEvent(self, _e):
		# open failed
		if not self.content:
			return
		# original scaling factor is set in main_window
		o_osf = self.viewport_data.original_scaling_factor
		self._set_original_scaling_factor()
		osf = self.viewport_data.original_scaling_factor
		if not var.preserve_viewport:
			self._scale_view(1.0, False)
		else:
			self._scale_view(osf / o_osf, False) # prevent overflow
		self.render()

	def update_content_size(self, new_size: QSizeF):
		self.old_content_size = self.content_size
		self.content_size = new_size

	def update_content(self, content, filename):
		if filename != var.thumbnail_loader.filelist[var.current_idx]:
			var.logger.info(f"Skip {filename}")
			return False
		if self.last_content_item:
			self.scene().removeItem(self.last_content_item)
		if not var.preload_thumbnail:
			self._reset_scene()
		if self.ty == 1:
			content = QPixmap.fromImage(content)
			self.content = content
			self.update_content_size(content.size())
			if self.content.isNull():
				var.logger.error("Load image error")
				self.content = None
				return False
			item = QGraphicsPixmapItem()
			item.setPixmap(content)
			if var.no_interpolation:
				item.setTransformationMode(Qt.FastTransformation)
			else:
				item.setTransformationMode(Qt.SmoothTransformation)
			self.scene().addItem(item)
		elif self.ty == 2:
			self.content = QMovie(content)
			# don't use content size, gif image identified as movie breaks
			self.update_content_size(QImageReader(content).size())
			if not self.content.isValid():
				var.logger.error("Load movie error")
				self.content = None
				return False
			self.content.start()
			label = QLabel()
			label.resize(self.content_size)
			label.setMovie(self.content)
			self.scene().addWidget(label)
		elif self.ty == 3:
			item = QGraphicsSvgItem(content)
			self.content = item
			self.update_content_size(item.boundingRect().size())
			self.scene().addItem(item)
		else:
			var.logger.error(f"Unknown type: {self.ty}")
			return False
		if not var.preload_thumbnail:
			self._finish_loading()
		var.main_window.label_stack.unset_label("loading")
		self.setCursor(Qt.CrossCursor)
		return True

	def _finish_loading(self):
		self._set_original_scaling_factor()
		if not var.preserve_viewport or not self.viewport_data.zoom_level:
			self._scale_view(1.0, True)
			self._set_content_center()
		else:
			self._scale_view(
				self.viewport_data.original_scaling_factor / self.viewport_data.zoom_level,
				True,
			)
			self._set_content_center(True)
		self._set_move_dist()
		self.render()
		var.main_window.image_display.show()
		var.main_window.set_basic_label()

	def _reset_scene(self):
		scene = QGraphicsScene()
		scene.setSceneRect(QRectF(-5e6, -5e6, 1e7, 1e7))
		self.setScene(scene)

	def load(self):
		var.logger.info(f"Start loading id {var.current_idx}")
		self.viewport_data.new_image_initialize()
		self.setCursor(Qt.WaitCursor)
		var.main_window.label_stack.set_label("loading", "loading")
		# if size not locked, zoom_level is unknown
		if not var.preserve_viewport:
			self.viewport_data.zoom_level = None
			# else, zoom level won't change

		self.last_content_item = None
		self.canvas_item = None
		self.ty = var.thumbnail_loader.typelist[var.current_idx]
		filename = var.thumbnail_loader.filelist[var.current_idx]
		if var.preload_thumbnail:
			self._reset_scene()
			self.update_content_size(QImageReader(filename).size())
			if self.content_size.width() == -1:
				var.logger.error(f"Load image size error: {filename}")
				self.content = None
				return False
			pixmap = var.thumbnail_loader.pixmaps[var.current_idx].scaled(self.content_size)
			self.content = pixmap
			item = QGraphicsPixmapItem()
			self.last_content_item = item
			item.setPixmap(pixmap)
			self.scene().addItem(item)
			self._finish_loading()
		self.load_data.emit(filename, self.ty)
		return True

	def render(self):
		size = self._compute_view_size()
		sx = self.viewport().width() / size.width()
		sy = self.viewport().height() / size.height()
		if sx <= sy:
			k = sx
		elif sx > sy:
			k = sy
		else:
			raise Exception('Float error')
		self.setTransform(self.viewport_data.get_transform(k))
		self.centerOn(self.viewport_data.content_center.x(), self.viewport_data.content_center.y())

	def navigate_image(self, offset, abs_pos = False):
		old_idx = var.current_idx
		if abs_pos:
			var.current_idx = offset
		else:
			var.current_idx += offset
		if var.current_idx >= len(var.thumbnail_loader.filelist):
			var.current_idx = len(var.thumbnail_loader.filelist) - 1
		if var.current_idx < 0:
			var.current_idx = 0
		if old_idx == var.current_idx:
			return
		self.load()

	def _scale_view(self, offset, abs_k = False):
		self.viewport_data.scale_view(offset, abs_k)
		self._set_move_dist()

	def _key_press_handler_navigation(self, k):
		if k == Keydef.image_view_next:
			self.navigate_image(1, False)
		elif k == Keydef.image_view_prev:
			self.navigate_image(-1, False)
		elif k == Keydef.image_view_last:
			self.navigate_image(len(var.thumbnail_loader.filelist) - 1, True)
		elif k == Keydef.image_view_first:
			self.navigate_image(0, True)
		elif k == Keydef.image_navi_reload:
			self.load()
		else:
			return False
		return True

	def _set_content_center(self, preserve_center = False):
		if preserve_center and self.viewport_data.content_center:
			tmp = self.content_size / 2
			self.viewport_data.content_center += QPointF(tmp.width(), tmp.height())
			tmp = self.old_content_size / 2
			self.viewport_data.content_center -= QPointF(tmp.width(), tmp.height())
			return
		t = self.content_size / 2
		self.viewport_data.content_center = QPointF(t.width(), t.height())
		self.viewport_data.scale_view(1.0, True)

	def _set_move_dist(self):
		self.move_dist = self.viewport_data.get_move_dist()

	def _key_press_handler_transform(self, k):
		if k == Keydef.image_view_left:
			self.viewport_data.move(QPointF(-self.move_dist, 0))
		elif k == Keydef.image_view_right:
			self.viewport_data.move(QPointF(self.move_dist, 0))
		elif k == Keydef.image_view_down:
			self.viewport_data.move(QPointF(0, self.move_dist))
		elif k == Keydef.image_view_up:
			self.viewport_data.move(QPointF(0, -self.move_dist))
		elif k == Keydef.image_view_zoom_out:
			self._scale_view(var.scaling_mult, False)
		elif k == Keydef.image_view_zoom_in:
			self._scale_view(1 / var.scaling_mult, False)
		elif k == Keydef.image_view_zoom_origin:
			self._scale_view(self.viewport_data.original_scaling_factor, True)
			var.preserve_viewport = True
			self._set_move_dist()
		elif k == Keydef.image_view_mirror_h:
			self.viewport_data.set_flip(1)
		elif k == Keydef.image_view_mirror_v:
			self.viewport_data.set_flip(0)
		elif k == Keydef.image_view_zoom_fill:
			if not var.keymod_shift:
				var.preserve_viewport = False
				self._set_content_center()
				self._scale_view(1.0, True)
				self.viewport_data.set_rotation(0)
				self._set_move_dist()
		elif k == Keydef.image_view_ccw:
			self.viewport_data.rotate90(-1)
		elif k == Keydef.image_view_cw:
			self.viewport_data.rotate90(1)
		else:
			return False
		self.render()
		return True

	def _key_press_handler_movie(self, k):
		if not isinstance(self.content, QMovie):
			return False
		if k == Keydef.image_movie_pause_toggle:
			s = self.content.state()
			if s == QMovie.Running:
				self.content.setPaused(True)
			elif s == QMovie.NotRunning or s == QMovie.Paused:
				self.content.setPaused(False)
			else:
				var.logger.error("Unknown state")
		if k == Keydef.image_movie_frame_forward:
			n = self.content.currentFrameNumber()
			var.logger.debug(f"Frame before keypress: {n}")
			self.content.jumpToFrame(n + 1)
		else:
			return False
		return True

	def _set_canvas(self):
		scaling = self.canvas_scaling_factor
		size = self.content_size * scaling
		var.logger.info(f"Create canvas {size}")
		self.canvas_item = CanvasItem(size)
		self.canvas_item.setScale(1 / scaling)
		self.canvas_item.setZValue(1)
		self.scene().addItem(self.canvas_item)

	def _key_release_handler_canvas(self, k, is_auto_repeat):
		if is_auto_repeat:
			return False
		if k == Keydef.image_canvas_clear:
			self.mouse_mode = 0
			self.parent().override_label("")
			self._set_canvas()
			return True
		return False

	def _key_press_handler_canvas(self, k, is_auto_repeat):
		if is_auto_repeat:
			return False
		if k == Keydef.image_canvas_clear:
			if self.canvas_item:
				self.scene().removeItem(self.canvas_item)
			self.mouse_mode = 6
		elif k == Keydef.image_canvas_undo:
			if self.canvas_item:
				self.canvas_item.undo()
		elif k == Keydef.image_canvas_eraser:
			if self.canvas_item:
				self.canvas_item.set_operator(True)
		elif k == Keydef.image_canvas_pen:
			if self.canvas_item:
				self.canvas_item.set_operator(False)
		else:
			return False
		return True

	def key_handler(self, k, is_release, is_auto_repeat):
		if is_release:
			if self._key_release_handler_canvas(k, is_auto_repeat):
				return True
			return False

		if self._key_press_handler_navigation(k):
			return True
		if not self.content:
			var.logger.info("Key ignored, because content is invalid.")
			return True
		if self._key_press_handler_transform(k):
			return True
		if self._key_press_handler_movie(k):
			return True
		if self._key_press_handler_canvas(k, is_auto_repeat):
			return True
		return False

	def _mouse_shift_rotate(self, pos):
		c = self.viewport().rect().center()
		p1 = pos - c
		angle = atan2(p1.x(), p1.y()) / pi * 180 * self.viewport_data.rotate_multiplier()
		if self.mouse_mode == 0:
			self.last_mouse_angle = angle
			self.mouse_mode = 3
			self.setCursor(Qt.ClosedHandCursor)
			return
		if self.mouse_mode != 3:
			return
		d_angle = angle - self.last_mouse_angle
		if d_angle > var.image_move_rotate:
			k = int(d_angle / var.image_move_rotate)
			self.viewport_data.rotate(-var.image_move_rotate * k)
			self.last_mouse_angle += var.image_move_rotate * k
		elif d_angle < -var.image_move_rotate:
			k = int(-d_angle / var.image_move_rotate)
			self.viewport_data.rotate(var.image_move_rotate * k)
			self.last_mouse_angle -= var.image_move_rotate * k
		self.render()

	def _mouse_ctrl_zoom(self, pos):
		if self.mouse_mode == 0:
			self.last_mouse_pos = pos
			self.mouse_mode = 1
			return
		if self.mouse_mode != 1:
			return
		self.setCursor(Qt.SizeVerCursor)
		dp = pos - self.last_mouse_pos
		if dp.y() > var.image_move_zoom:
			self._scale_view(var.scaling_mult_mouse, False)
			self.last_mouse_pos = pos
		elif dp.y() < -var.image_move_zoom:
			self._scale_view(1 / var.scaling_mult_mouse, False)
			self.last_mouse_pos = pos
		var.main_window.set_basic_label()
		self.render()

	def _mouse_pan(self, pos):
		if self.mouse_mode == 0:
			self.last_mouse_pos = pos
			self.mouse_mode = 2
			return
		if self.mouse_mode != 2:
			return
		self.setCursor(Qt.OpenHandCursor)
		dp = pos - self.last_mouse_pos
		view_size_w = self._compute_view_size().width()
		dp *= -view_size_w / self.width()
		self.viewport_data.move(dp)
		self.last_mouse_pos = pos
		self.render()

	def tabletEvent(self, e):
		pos = e.posF()
		pressure = e.pressure()
		pos = self.mapToScene(int(pos.x()), int(pos.y())) * self.canvas_scaling_factor
		ty = e.type()
		if ty == QEvent.TabletPress:
			if not self.canvas_item:
				return
			if (
				not self.canvas_item.on_draw and \
				e.buttons() == Qt.LeftButton
			):
				var.logger.debug("Tablet press")
				self.canvas_item.draw(pos, pressure)
				self.canvas_item.on_draw = True
				return
		if not self.canvas_item or not self.canvas_item.on_draw:
			return
		if ty == QEvent.TabletRelease:
			var.logger.debug("Tablet release")
			self.canvas_item.finish()
			# generate undo patch here
			self.canvas_item.on_draw = False
			return
		if e.buttons() != Qt.LeftButton:
			self.canvas_item.on_draw = False
			return
		if ty == QEvent.TabletMove:
			self.canvas_item.draw(pos, pressure)

	def mouseMoveEvent(self, e):
		pos = e.localPos()
		if e.buttons() & Qt.MiddleButton:
			if self.mouse_mode == 3:
				self._mouse_shift_rotate(pos)
				return
			if self.mouse_mode == 1:
				self._mouse_ctrl_zoom(pos)
				return
			if var.keymod_shift:
				self._mouse_shift_rotate(pos)
				return
			if var.keymod_control:
				self._mouse_ctrl_zoom(pos)
				return
			self._mouse_pan(pos)
			return
		if e.buttons() & Qt.RightButton:
			pos = e.localPos()
			self.setCursor(Qt.ArrowCursor)
			if self.mouse_mode == 0:
				self.last_mouse_pos = pos
				self.mouse_mode = 4
				self.setCursor(Qt.CrossCursor)
				return
			if self.mouse_mode != 4:
				return
			dp = pos - self.last_mouse_pos
			if dp.y() < -var.guesture_move:
				var.main_window.grid_mode()
			elif dp.x() < -var.guesture_move:
				self.navigate_image(-1, False)
			elif dp.x() > var.guesture_move:
				self.navigate_image(1, False)
			else:
				return
			self.mouse_mode = 5 # not 4
			return
		if self.mouse_mode == 6:
			if e.buttons() & Qt.LeftButton and self.last_mouse_pos:
				dp = pos - self.last_mouse_pos
				self.canvas_scaling_factor += dp.y() / 100
				scaling = self.canvas_scaling_factor
				size = self.content_size * self.canvas_scaling_factor
				var.main_window.label_stack.set_label("canvas_size",
					"Creating canvas:" \
					f"{scaling:.2f} " \
					f"{size.width():.0f} x {size.height():.0f}" \
				)
			else:
				var.main_window.label_stack.unset_label("canvas_size")
			self.last_mouse_pos = pos
		else:
			self.setCursor(Qt.CrossCursor)
			self.mouse_mode = 0

	def get_zoom_level(self):
		return self.viewport_data.zoom_level
