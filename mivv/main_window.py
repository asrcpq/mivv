from time import time

from PyQt5.QtWidgets import QLabel, QMainWindow
from PyQt5.QtGui import QFont, QFontMetrics
from PyQt5.QtCore import Qt

from mivv import var
from mivv.label_stack import LSLabel
from mivv.grid_view import Gridview
from mivv.image_display import ImageDisplay
from mivv.keydef import Keydef

class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		self.setStyleSheet(f"background-color: {var.background}")
		self.setWindowTitle("mivv")
		if var.fullscreen:
			self.setWindowState(Qt.WindowFullScreen)
		var.hidpi = self.devicePixelRatioF()
		self.setGeometry(0, 0, 640, 480)

		self.mode = None
		self.image_display = ImageDisplay(self)
		self.grid_view = Gridview(self)

		labels = []
		for name in ["filename", "info"]:
			label = LSLabel(self)
			labels.append(label)
		self.fn_label = labels[0]
		self.info_label = labels[1]

	def initialize_view(self):
		if var.start_in_grid_mode:
			self.grid_mode()
		else:
			self.image_mode()
		self.show()
		var.logger.info(f"Startup time: {time() - var.startup_time:.03f} secs")

	def loader_callback(self):
		self.set_label()
		if self.mode == 2:
			self.grid_view.update_filelist()

	def label_busy(self, busy):
		return
		if busy:
			self.fn_label.setStyleSheet("QLabel{background-color: black;color: red;}")
		else:
			self.fn_label.setStyleSheet("QLabel{background-color: black;color: white;}")

	def set_fn_label_string(self, string):
		left = self.info_label.geometry().left()
		metrics = QFontMetrics(self.fn_label.font())
		elidedText = metrics.elidedText(string, Qt.ElideLeft, left)
		self.fn_label.set_text(elidedText)
		self.fn_label.setGeometry(
			0,
			self.height() - var.bar_height,
			left,
			var.bar_height,
		)

	def set_fn_label_filename(self):
		text = f"{var.image_loader.filelist[var.current_idx]}"
		self.set_fn_label_string(text)

	def set_label(self):
		status_string = ""
		if var.preserve_viewport:
			status_string += "W"
		if var.preload_thumbnail:
			status_string += "T"
		if status_string:
			status_string = f"[{status_string}]"
		if self.mode == 1:
			try:
				zoom_level_percent = 100 * self.image_display.get_zoom_level()
				scaling_string = f"{zoom_level_percent:.1f}%"
			except TypeError:
				scaling_string = "?%"
		elif self.mode == 2:
			scaling_string = f"{var.grid_sizes[self.grid_view.grid_size_idx]}px"
		else:
			scaling_string = "?%"
		if not var.image_loader.finished:
			unfinished_indicator = "+"
		else:
			unfinished_indicator = ""
		self.info_label.set_text(
			f" {status_string} " \
			f"{scaling_string} " \
			f"{1 + var.current_idx}/{len(var.image_loader.filelist)}" \
			f"{unfinished_indicator}" \
		)
		self.info_label.adjustSize()
		width = self.info_label.geometry().width()
		self.info_label.setGeometry(
			self.width() - width,
			self.height() - var.bar_height,
			width,
			var.bar_height,
		)
		self.set_fn_label_filename()

	def grid_mode(self):
		self.image_display.hide()
		if not self.grid_view.reset_layout():
			self.grid_view.set_cursor(False)
		self.grid_view.update_filelist()
		self.grid_view.resize(self.width(), self.height())
		self.grid_view.show()
		self.mode = 2
		self.set_label() # only for zoom level

	def image_mode(self):
		self.image_display.load()
		self.image_display.resize(self.width(), self.height())
		self.grid_view.hide()
		self.mode = 1
		self.set_label() # only for zoom level

	def prockey(self, e):
		bit = int(var.keymod_control) * 2 + int(var.keymod_shift)
		k = var.keymap_common.get((e.key(), bit))
		if not k:
			if self.mode == 1:
				k = var.keymap_image.get((e.key(), bit))
			elif self.mode == 2:
				k = var.keymap_grid.get((e.key(), bit))
		if not k:
			var.logger.debug("Key ignored")
			return None
		var.logger.debug(k)
		return k

	def keyReleaseEvent(self, e):
		if e.key() == Qt.Key_Shift:
			var.logger.debug("Shift release")
			var.keymod_shift = False
			return
		if e.key() == Qt.Key_Control:
			var.logger.debug("Control release")
			var.keymod_control = False
			return
		k = self.prockey(e)
		if self.mode == 1:
			self.image_display.key_handler(k, True, e.isAutoRepeat())

	def keyPressEvent(self, e):
		if e.key() == Qt.Key_Shift:
			var.logger.debug("Shift pressed")
			var.keymod_shift = True
			return
		if e.key() == Qt.Key_Control:
			var.logger.debug("Control pressed")
			var.keymod_control = True
			return
		k = self.prockey(e)
		if not k:
			return
		if k == Keydef.toggle_grid_mode:
			if self.mode == 1:
				self.grid_mode()
			elif self.mode == 2:
				self.image_mode()
			else:
				raise Exception('Unknown mode')
		elif k == Keydef.quit:
			var.app.quit()
		elif k == Keydef.preserve_viewport:
			var.preserve_viewport = not var.preserve_viewport
			self.set_label()
		elif k == Keydef.preload_thumbnail:
			var.preload_thumbnail = not var.preload_thumbnail
			self.set_label()
		else:
			if self.mode == 1:
				ret = self.image_display.key_handler(k, False, e.isAutoRepeat())
			elif self.mode == 2:
				ret = self.grid_view.key_handler(k)
			else:
				var.logger.error(f"Unknown mode {self.mode}")
			if ret is None:
				var.logger.error("key handler return none!")
			if ret: # processed
				self.set_label()

	def resizeEvent(self, _e):
		var.logger.info(f"Resized to {self.width()} {self.height()}")
		if self.mode == 1:
			self.image_display.resize(self.width(), self.height())
		elif self.mode == 2:
			self.grid_view.resize(self.width(), self.height())

		# bug: randomly modifier keyreleaseevent not triggered during resize
		# when wm resize involves shift key to be pressed, like in i3wm.
		# This can be fixed after wayland key modifier works
		# during mouse event(see QTBUG-61488)
		# then we don't need to implement our own modifier tracker
		var.keymod_shift = False
		var.keymod_control = False
		self.set_label()
