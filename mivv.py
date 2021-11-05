import sys
import os
import argparse
from pathlib import Path

from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QMainWindow
from PyQt5.QtGui import QPixmap, QKeyEvent
from PyQt5.QtCore import Qt

class Config():
	def __init__(self):
		self.grid_size = 120
		self.overwrite_cache = False
		self.start_in_grid_mode = False
config = Config()

filelist = []
pixmaps = [] # thumbnails
current_idx = 0

class Gridview(QWidget):
	def __init__(self, config, parent = None):
		super().__init__(parent)
		self.setStyleSheet("background-color: black;")
		self.idx_offset = 0
		self.grid_size = config.grid_size
		self.grid_space = 10
		self.grid_offset = self.grid_size + self.grid_space
		self.count_h = 0
		self.count_v = 0
		self.labels = []
		self.reset_layout()

	def get_idx(self, i, j):
		return j * self.count_h + i + self.idx_offset 

	def reset_layout(self):
		count_h = (self.width() - self.grid_space) // self.grid_offset
		count_v = (self.height() - self.grid_space) // self.grid_offset
		if self.count_h == count_h and self.count_v == count_v:
			return
		if self.count_h > count_h or self.count_v > count_v:
			for j in range(0, count_v):
				try:
					self.labels[j][count_h].hide()
				except IndexError:
					pass
			for i in range(0, count_h +1):
				try:
					self.labels[count_v][i].hide()
				except IndexError:
					pass
		self.count_h = count_h
		self.count_v = count_v
		for j in range(self.count_v):
			if j >= len(self.labels):
				self.labels.append([])
			for i in range(self.count_h):
				if i >= len(self.labels[j]):
					label = QLabel(f"Thumbview_{j}_{i}", self)
					label.setAlignment(Qt.AlignCenter)
					label.setStyleSheet("border: 1px solid red;")
					label.setGeometry(
						i * self.grid_offset + self.grid_space,
						j * self.grid_offset + self.grid_space,
						self.grid_size,
						self.grid_size,
					)
					self.labels[j].append(label)
				else:
					label = self.labels[j][i]
				idx = self.get_idx(i, j)
				if idx >= len(filelist):
					self.labels[j][i].hide()
				else:
					pixmap_resize = pixmaps[idx].scaled(
						self.grid_size,
						self.grid_size,
						Qt.KeepAspectRatio,
						transformMode=Qt.SmoothTransformation,
					)
					label.setPixmap(pixmap_resize)
					label.show()

	def resizeEvent(self, event):
		self.reset_layout()

	def key_handler(self, e: QKeyEvent):
		pass

class Imageview(QWidget):
	def __init__(self, parent = None):
		super().__init__(parent)
		self.setStyleSheet("background-color: black;")
		self.label = QLabel("Imageview", self)
		self.label.setAlignment(Qt.AlignCenter)
		self.reload()
		self.render()

	def resizeEvent(self, event):
		self.render()

	def reload(self):
		global current_idx, pixmaps
		self.pixmap = QPixmap(filelist[current_idx])
	
	def render(self):
		pixmap_resize = self.pixmap.scaled(self.width(), self.height(), Qt.KeepAspectRatio)
		self.label.setPixmap(pixmap_resize)
		self.label.resize(self.width(), self.height())

	def key_handler(self, e: QKeyEvent):
		global current_idx
		if e.key() == Qt.Key_Space or e.key() == Qt.Key_N:
			current_idx += 1
			if current_idx >= len(filelist):
				current_idx = len(filelist) - 1
		elif e.key() == Qt.Key_Backspace or e.key() == Qt.Key_P:
			current_idx -= 1
			if current_idx < 0:
				current_idx = 0
		else:
			return
		self.reload()
		self.render()

class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		self.setStyleSheet("background-color: black;")
		self.setWindowTitle("mivv")
		self.setGeometry(0, 0, 640, 480)
		self.image_view = Imageview(self)
		self.grid_view = Gridview(config, self)
		if config.start_in_grid_mode:
			self.grid_mode()
		else:
			self.image_mode()
		self.show()

	def grid_mode(self):
		self.image_view.hide()
		self.grid_view.show()
		self.grid_view.resize(self.width(), self.height())
		self.grid_view.reset_layout()
		self.mode = 2

	def image_mode(self):
		self.grid_view.hide()
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

	def resizeEvent(self, event):
		if self.mode == 1:
			self.image_view.resize(self.width(), self.height())
		elif self.mode == 2:
			self.grid_view.resize(self.width(), self.height())

def build_parser():
	parser = argparse.ArgumentParser(description = "immv")
	parser.add_argument('-i', action = "store_true")
	parser.add_argument('-t', action = "store_true")
	parser.add_argument('-c', action = "store_true")
	return parser

def cached_read(path):
	abspath = os.path.abspath(path)
	# add an extra dot to prevent possible contamination
	cached_path = f"{os.environ['XDG_CACHE_HOME']}/mivv/.{abspath}"
	if os.path.exists(cached_path) and not config.overwrite_cache:
		return QPixmap(cached_path)
	print("Generating cache for:", abspath)
	dirname = os.path.dirname(cached_path)
	Path(dirname).mkdir(parents = True, exist_ok = True)
	pixmap = QPixmap(abspath)
	pixmap_resize = pixmap.scaled(
		config.grid_size,
		config.grid_size,
		Qt.KeepAspectRatio,
		transformMode=Qt.SmoothTransformation,
	)
	pixmap_resize.save(cached_path)
	return pixmap_resize

if __name__ == '__main__':
	args, unknown_args = build_parser().parse_known_args()
	if args.c:
		config.overwrite_cache = True
	if args.t:
		config.start_in_grid_mode = True
	if args.i:
		filelist_string = sys.stdin.read()
		filelist = filelist_string.split()
	else:
		filelist = unknown_args
	if len(filelist) == 0:
		print("No image file specified, exiting")
		exit(1)
	app = QApplication([])
	for file in filelist:
		# TODO: async load
		pixmaps.append(cached_read(file))
		print("Read", file)
	main_window = MainWindow()
	app.exec_()
