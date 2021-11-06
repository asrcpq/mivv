from PyQt5.QtWidgets import QLabel, QMainWindow
from PyQt5.QtGui import QKeyEvent, QFont
from PyQt5.QtCore import Qt

from grid_view import Gridview
from image_view import Imageview

import var

class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		self.setStyleSheet("background-color: black;")
		self.setWindowTitle("mivv")
		self.setGeometry(0, 0, 640, 480)

		self.image_view = Imageview(self)
		self.grid_view = Gridview(self)
		self.bar_height = 10

		label = QLabel("filename", self)
		label.setStyleSheet("color: #FFFFFF;")
		label.setFont(QFont("monospace"))
		self.fn_label = label
		label = QLabel("info", self)
		label.setStyleSheet("color: #FFFFFF;")
		label.setFont(QFont("monospace"))
		self.info_label = label
		self.set_label()

		if var.start_in_grid_mode:
			self.grid_mode()
		else:
			self.image_mode()
		self.show()

	def set_label(self):
		self.info_label.setText(f"({1 + var.current_idx}/{len(var.filelist)})")
		self.info_label.adjustSize()
		width = self.info_label.geometry().width()
		self.info_label.setGeometry(
			self.width() - width,
			self.height() - self.bar_height,
			width,
			self.bar_height,
		)
		left = self.info_label.geometry().left()
		self.fn_label.setText(f"{var.image_loader.filelist[var.current_idx]}")
		self.fn_label.setGeometry(
			0,
			self.height() - self.bar_height,
			left,
			self.bar_height,
		)

	def grid_mode(self):
		self.image_view.hide()
		self.grid_view.show()
		self.grid_view.resize(self.width(), self.height())
		self.grid_view.reset_layout()
		self.mode = 2

	def image_mode(self):
		self.grid_view.hide()
		self.image_view.reload()
		self.image_view.show()
		self.image_view.resize(self.width(), self.height())
		self.mode = 1

	def keyPressEvent(self, e: QKeyEvent):
		if e.key() == Qt.Key_Return:
			if self.mode == 1:
				self.grid_mode()
			elif self.mode == 2:
				self.image_mode()
		elif e.key() == Qt.Key_Escape or e.key() == Qt.Key_Q:
			exit(0)
		else:
			if self.mode == 1:
				self.image_view.key_handler(e)
			elif self.mode == 2:
				self.grid_view.key_handler(e)
			self.set_label()

	def resizeEvent(self, event):
		self.set_label()
		if self.mode == 1:
			self.image_view.resize(self.width(), self.height() - self.bar_height)
		elif self.mode == 2:
			self.grid_view.resize(self.width(), self.height() - self.bar_height)
