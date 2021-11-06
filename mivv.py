import sys
import os
import argparse
from glob import glob
from pathlib import Path

from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QMainWindow
from PyQt5.QtGui import QPixmap, QKeyEvent, QFont
from PyQt5.QtCore import Qt

class Config():
	def __init__(self):
		# reference size for cache
		self.cache_size = 256
		self.overwrite_cache = False
		self.start_in_grid_mode = False
config = Config()

cache_path = f"{os.environ['XDG_CACHE_HOME']}/mivv/"
valid_ext = {".png", ".PNG", ".jpg", ".JPG", ".jpeg", ".JPEG", ".bmp", ".BMP", ".gif", ".GIF"}
filelist = []
pixmaps = [] # thumbnails
current_idx = 0

class Gridview(QWidget):
	def __init__(self, config, parent = None):
		super().__init__(parent)
		self.setStyleSheet("background-color: black;")
		self.y_offset = 0
		self.grid_sizes = [32, 64, 144, 192, 256]
		self.grid_size_idx = 2
		self.grid_size_idx_default = 2
		self.config = config
		self.grid_space = 10
		self.count_h = 0
		self.count_v = 0
		self.cursor = [0, 0]
		self.labels = []
		self.reset_layout()

	def get_idx(self, i, j):
		return (j + self.y_offset) * self.count_h + i

	def toggle_highlight(self, up):
		try:
			if up:
				self.labels[self.cursor[1]][self.cursor[0]].setStyleSheet("border: 1px solid red;")
			else:
				self.labels[self.cursor[1]][self.cursor[0]].setStyleSheet("border: none;")
		except IndexError:
			pass

	def __set_cursor(self, scaled = True):
		self.toggle_highlight(False)
		if self.count_h == 0:
			return
		self.cursor[0] = current_idx % self.count_h
		cy_plus_offset = current_idx // self.count_h
		# scaled: row as close as possible
		# keymove: scroll as little as possible
		if scaled:
			# y shrink, never overflow
			if self.cursor[1] >= self.count_v:
				self.cursor[1] = self.count_v - 1
			if cy_plus_offset >= self.cursor[1]:
				self.y_offset = cy_plus_offset - self.cursor[1]
			else:
				self.y_offset = 0
				self.cursor[1] = cy_plus_offset
			self.refresh()
		else:
			if cy_plus_offset < self.y_offset:
				self.cursor[1] = 0
				self.y_offset = cy_plus_offset
				self.refresh()
			elif cy_plus_offset >= self.y_offset + self.count_v:
				self.cursor[1] = self.count_v - 1
				self.y_offset = cy_plus_offset - self.cursor[1]
				self.refresh()
			else:
				self.cursor[1] = cy_plus_offset - self.y_offset
		self.toggle_highlight(True) # after refresh all labels are initialized

	def xreset_layout(self):
		for label_row in self.labels:
			for label in label_row:
				label.close()
		self.labels = []
		self.reset_layout()

	# layout = a x b images in screen
	def reset_layout(self):
		self.grid_offset = self.grid_sizes[self.grid_size_idx] + self.grid_space
		count_h = (self.width() - self.grid_space) // self.grid_offset
		count_v = (self.height() - self.grid_space) // self.grid_offset
		if self.count_h == count_h and self.count_v == count_v:
			return
		for j in range(0, count_v):
			try:
				self.labels[j][count_h].hide()
			except IndexError:
				pass
		for i in range(0, count_h + 1):
			try:
				self.labels[count_v][i].hide()
			except IndexError:
				pass
		self.count_h = count_h
		self.count_v = count_v
		self.__set_cursor(True)
	
	def refresh(self):
		grid_size = self.grid_sizes[self.grid_size_idx]
		for j in range(self.count_v):
			if j >= len(self.labels):
				self.labels.append([])
			for i in range(self.count_h):
				if i >= len(self.labels[j]):
					label = QLabel(f"Thumbview_{j}_{i}", self)
					label.setAlignment(Qt.AlignCenter)
					label.setGeometry(
						i * self.grid_offset + self.grid_space,
						j * self.grid_offset + self.grid_space,
						grid_size,
						grid_size,
					)
					self.labels[j].append(label)
				else:
					label = self.labels[j][i]
				idx = self.get_idx(i, j)
				if idx >= len(filelist):
					self.labels[j][i].hide()
				else:
					pixmap_resize = pixmaps[idx].scaled(
						grid_size,
						grid_size,
						Qt.KeepAspectRatio,
						Qt.SmoothTransformation,
					)
					label.setPixmap(pixmap_resize)
					label.show()

	def resizeEvent(self, event):
		self.reset_layout()

	def offset_cursor(self, offset, abs_pos = False):
		global current_idx
		old_idx = current_idx
		current_idx += offset
		if current_idx < 0:
			current_idx = old_idx
		elif current_idx >= len(filelist):
			if (self.cursor[1] + self.y_offset + 1) * self.count_h < len(filelist):
				current_idx = len(filelist) - 1
				self.__set_cursor(False)
			else:
				current_idx = old_idx
		else:
			self.__set_cursor(False)

	def set_zoom_level(self, dz, abs_zoom = False):
		old_idx = self.grid_size_idx
		if abs_zoom:
			if self.grid_size_idx != dz:
				self.grid_size_idx = dz
			else:
				return
		else:
			self.grid_size_idx += dz
		if self.grid_size_idx < 0:
			self.grid_size_idx = 0
		elif self.grid_size_idx >= len(self.grid_sizes):
			self.grid_size_idx = len(self.grid_sizes) - 1
		if old_idx == self.grid_size_idx:
			return
		self.xreset_layout()

	def key_handler(self, e: QKeyEvent):
		global current_idx
		if e.key() == Qt.Key_L:
			self.offset_cursor(1, False)
		elif e.key() == Qt.Key_H:
			self.offset_cursor(-1, False)
		elif e.key() == Qt.Key_J:
			self.offset_cursor(self.count_h, False)
		elif e.key() == Qt.Key_K:
			self.offset_cursor(-self.count_h, False)
		elif e.key() == Qt.Key_O:
			self.set_zoom_level(-1, False)
		elif e.key() == Qt.Key_I:
			self.set_zoom_level(1, False)
		elif e.key() == Qt.Key_0:
			self.set_zoom_level(self.grid_size_idx_default, True)

class Imageview(QWidget):
	def __init__(self, parent = None):
		super().__init__(parent)
		self.setStyleSheet("background-color: black;")
		self.label = QLabel("Imageview", self)
		self.label.setAlignment(Qt.AlignCenter)
		self.scaling_mult = 1.3
		self.initialize()

	def resizeEvent(self, event):
		self.render()

	def initialize(self):
		self.scaling_factor = 0.99
		self.reload()
		self.render()

	def reload(self):
		global current_idx, pixmaps
		self.pixmap = QPixmap(filelist[current_idx])
	
	def render(self):
		pixmap_resize = self.pixmap.scaled(
			int(self.width() * self.scaling_factor),
			int(self.height() * self.scaling_factor),
			Qt.KeepAspectRatio,
			Qt.SmoothTransformation,
		)
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
		elif e.key() == Qt.Key_O:
			self.scaling_factor /= self.scaling_mult
		elif e.key() == Qt.Key_I:
			self.scaling_factor *= self.scaling_mult
		elif e.key() == Qt.Key_0:
			self.scaling_factor = 0.99
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

		if config.start_in_grid_mode:
			self.grid_mode()
		else:
			self.image_mode()
		self.show()

	def set_label(self):
		self.info_label.setText(f"({current_idx}/{len(filelist)})")
		self.info_label.adjustSize()
		width = self.info_label.geometry().width()
		self.info_label.setGeometry(
			self.width() - width,
			self.height() - self.bar_height,
			width,
			self.bar_height,
		)
		left = self.info_label.geometry().left()
		self.fn_label.setText(f"{filelist[current_idx]}")
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
		self.image_view.initialize()
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

def build_parser():
	parser = argparse.ArgumentParser(description = "immv")
	parser.add_argument('-i', action = "store_true", help = "filelist from stdin")
	parser.add_argument('-t', action = "store_true", help = "start in grid mode")
	parser.add_argument('-c', action = "store_true", help = "overwrite cache")
	return parser

def cached_read(path):
	global cache_path
	abspath = os.path.abspath(path)
	if not os.path.exists(abspath):
		# remove cache? maybe not
		return None
	if abspath.startswith(cache_path):
		return QPixmap(abspath)
	cached_path = cache_path + abspath + ".jpg"
	if os.path.exists(cached_path) and not config.overwrite_cache:
		return QPixmap(cached_path)
	_filename, ext = os.path.splitext(abspath)
	if ext not in valid_ext:
		return None
	pixmap = QPixmap(abspath)
	if pixmap.isNull():
		print("Read fail:", abspath)
		return None
	print("Gen cache:", abspath)
	dirname = os.path.dirname(cached_path)
	Path(dirname).mkdir(parents = True, exist_ok = True)
	pixmap_resize = pixmap.scaled(
		config.grid_size,
		config.grid_size,
		Qt.KeepAspectRatio,
		Qt.SmoothTransformation,
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
	app = QApplication([])
	filelist_tmp = list(reversed(filelist))
	filelist = []
	while filelist_tmp:
		file = filelist_tmp[-1]
		filelist_tmp.pop()
		if os.path.isdir(file):
			filelist_tmp += glob(os.path.join(file, "*"))
			continue
		# TODO: async load
		pixmap = cached_read(file)
		if not pixmap:
			print("Skip", file)
			continue
		# print("Read", file)
		pixmaps.append(pixmap)
		filelist.append(file)
	if len(filelist) == 0:
		print("No image file specified, exiting")
		exit(1)
	main_window = MainWindow()
	app.exec_()
