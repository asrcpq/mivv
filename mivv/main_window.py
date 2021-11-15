from PyQt5.QtWidgets import QLabel, QMainWindow
from PyQt5.QtGui import QFont, QFontMetrics
from PyQt5.QtCore import Qt

from mivv.grid_view import Gridview
from mivv.image_display import ImageDisplay
from mivv import var

class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		self.setStyleSheet(f"background-color: {var.background};")
		self.setWindowTitle("mivv")
		var.hidpi = self.devicePixelRatioF()
		self.setGeometry(0, 0, 640, 480)

		self.mode = None
		self.image_display = ImageDisplay(self)
		self.grid_view = Gridview(self)

		labels = []
		font = QFont("monospace", var.bar_height - 1)
		for name in ["filename", "info"]:
			label = QLabel(name, self)
			label.setStyleSheet("color: white;")
			label.setFont(font)
			labels.append(label)
		self.fn_label = labels[0]
		self.info_label = labels[1]

	def initialize_view(self):
		if var.start_in_grid_mode:
			self.grid_mode()
		else:
			self.image_mode()
		self.show()

	def loader_callback(self):
		self.set_label()
		if self.mode == 2:
			self.grid_view.update_filelist()

	def label_busy(self, busy):
		if busy:
			self.fn_label.setStyleSheet("color: red;")
		else:
			self.fn_label.setStyleSheet("color: white;")

	def set_label(self):
		status_string = ""
		if var.lock_size:
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
		if not var.image_loader.finished:
			unfinished_indicator = "+"
		else:
			unfinished_indicator = ""
		self.info_label.setText(
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
		left = self.info_label.geometry().left()
		text = f"{var.image_loader.filelist[var.current_idx]}"
		metrics = QFontMetrics(self.fn_label.font())
		elidedText = metrics.elidedText(text, Qt.ElideLeft, left)
		self.fn_label.setText(elidedText)
		self.fn_label.setGeometry(
			0,
			self.height() - var.bar_height,
			left,
			var.bar_height,
		)

	def grid_mode(self):
		self.image_display.hide()
		if not self.grid_view.reset_layout():
			self.grid_view.set_cursor(False)
		self.grid_view.resize(self.width(), self.height() - var.bar_height)
		self.grid_view.show()
		self.mode = 2
		self.set_label() # only for zoom level

	def image_mode(self):
		# TODO no load if image not changed
		self.image_display.load()
		self.image_display.resize(self.width(), self.height() - var.bar_height)
		self.grid_view.hide()
		self.mode = 1
		self.set_label() # only for zoom level

	@staticmethod
	def keyReleaseEvent(e):
		k = e.key()
		if k == Qt.Key_Shift:
			var.keymod_shift = False
		elif k == Qt.Key_Control:
			var.keymod_control = False

	def keyPressEvent(self, e):
		k = e.key()
		if k == Qt.Key_Shift:
			var.keymod_shift = True
		elif k == Qt.Key_Control:
			var.keymod_control = True
		elif k == Qt.Key_Return or k == Qt.Key_Tab:
			if self.mode == 1:
				self.grid_mode()
			elif self.mode == 2:
				self.image_mode()
			else:
				raise Exception('Unknown mode')
		elif k == Qt.Key_Escape or k == Qt.Key_Q:
			var.app.quit()
		elif k == Qt.Key_W and var.keymod_shift:
			var.lock_size = not var.lock_size
			self.set_label()
		elif k == Qt.Key_T and var.keymod_shift:
			var.preload_thumbnail = not var.preload_thumbnail
			self.set_label()
		else:
			if self.mode == 1:
				self.image_display.key_handler(k)
			elif self.mode == 2:
				self.grid_view.key_handler(k)
			self.set_label()

	def resizeEvent(self, _e):
		var.logger.info(f"Resized to {self.width()} {self.height()}")
		if self.mode == 1:
			self.image_display.resize(self.width(), self.height() - var.bar_height)
		elif self.mode == 2:
			self.grid_view.resize(self.width(), self.height() - var.bar_height)
