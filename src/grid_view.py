from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QMainWindow
from PyQt5.QtGui import QPixmap, QKeyEvent, QFont
from PyQt5.QtCore import Qt

import var

class Gridview(QWidget):
	def __init__(self, parent = None):
		super().__init__(parent)
		self.setStyleSheet("background-color: black;")
		self.y_offset = 0
		self.grid_sizes = [32, 64, 128, 192, 256]
		self.grid_size_idx = 2
		self.grid_size_idx_default = 2
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
		self.cursor[0] = var.current_idx % self.count_h
		cy_plus_offset = var.current_idx // self.count_h
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
				if idx >= len(var.filelist):
					self.labels[j][i].hide()
				else:
					pixmap_resize = var.pixmaps[idx].scaled(
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
		old_idx = var.current_idx
		var.current_idx += offset
		if var.current_idx < 0:
			var.current_idx = old_idx
		elif var.current_idx >= len(var.filelist):
			if (self.cursor[1] + self.y_offset + 1) * self.count_h < len(var.filelist):
				var.current_idx = len(var.filelist) - 1
				self.__set_cursor(False)
			else:
				var.current_idx = old_idx
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
