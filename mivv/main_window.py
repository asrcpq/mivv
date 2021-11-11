import sys

from PyQt5.QtWidgets import QLabel, QMainWindow
from PyQt5.QtGui import QFont, QFontMetrics
from PyQt5.QtCore import Qt

from grid_view import Gridview
from image_view import Imageview
import var

class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		self.setStyleSheet("background-color: black;")
		self.setWindowTitle("mivv")
		var.hidpi = self.devicePixelRatioF()
		self.setGeometry(0, 0, 640, 480)

		self.image_view = Imageview(self)
		self.grid_view = Gridview(self)

		labels = []
		font = QFont("monospace", var.bar_height - 1)
		for name in ["filename", "info"]:
			label = QLabel(name, self)
			label.setStyleSheet("color: #FFFFFF;")
			label.setFont(font)
			labels.append(label)
		self.fn_label = labels[0]
		self.info_label = labels[1]

		if var.start_in_grid_mode:
			self.grid_mode()
		else:
			self.image_mode()
		self.show()

	def set_label(self):
		if self.mode == 1:
			zoom_level_percent = 100 / \
				self.image_view.scaling_factor * \
				self.image_view.original_scaling_factor
			scaling_string = f"{zoom_level_percent:.1f}%"
		elif self.mode == 2:
			scaling_string = f"{var.grid_sizes[self.grid_view.grid_size_idx]}px"
		self.info_label.setText(
			f" {scaling_string} " \
			f"{1 + var.current_idx}/{len(var.image_loader.filelist)}" \
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
		self.image_view.hide()
		if not self.grid_view.reset_layout():
			self.grid_view.set_cursor(False)
		self.grid_view.resize(self.width(), self.height() - var.bar_height)
		self.grid_view.show()
		self.mode = 2
		self.set_label() # only for zoom level

	def image_mode(self):
		self.grid_view.hide()
		self.image_view.resize(self.width(), self.height() - var.bar_height)
		self.image_view.show()
		self.image_view.load()
		if self.isVisible():
			self.image_view.render()
		self.mode = 1
		self.set_label() # only for zoom level

	@staticmethod
	def keyReleaseEvent(e):
		if e.key() == Qt.Key_Shift:
			var.keymod_shift = False
		elif e.key() == Qt.Key_Control:
			var.keymod_control = False

	def keyPressEvent(self, e):
		if e.key() == Qt.Key_Shift:
			var.keymod_shift = True
		elif e.key() == Qt.Key_Control:
			var.keymod_control = True
		elif e.key() == Qt.Key_Return:
			if self.mode == 1:
				self.grid_mode()
			elif self.mode == 2:
				self.image_mode()
		elif e.key() == Qt.Key_Escape or e.key() == Qt.Key_Q:
			sys.exit()
		else:
			if self.mode == 1:
				self.image_view.key_handler(e)
			elif self.mode == 2:
				self.grid_view.key_handler(e)
			self.set_label()

	def resizeEvent(self, _e):
		if self.mode == 1:
			# put it in ImageView's resizeEvent will be too late for label set here
			self.image_view.set_original_scaling_factor()
			self.image_view.resize(self.width(), self.height() - var.bar_height)
		elif self.mode == 2:
			self.grid_view.resize(self.width(), self.height() - var.bar_height)
		# set label after apply scaling factor
		self.set_label()
