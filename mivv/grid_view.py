from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt

from thumbnail import Thumbnail
import var

class Gridview(QWidget):
	def __init__(self, parent = None):
		super().__init__(parent)
		self.setMouseTracking(True)
		self.setStyleSheet("background-color: black;")
		self.y_offset = 0
		self.grid_size_idx = 2
		self.grid_space = 10
		self.grid_offset = None
		self.count_h = 0
		self.count_v = 0
		self.cursor = [0, 0]
		self.labels = []
		self.mouse_mode = 0
		self.last_mouse_pos = None

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

	def set_cursor(self, scaled = True):
		self.toggle_highlight(False)
		if self.count_h == 0:
			return
		self.cursor[0] = var.current_idx % self.count_h
		cy_plus_offset = var.current_idx // self.count_h
		total_row = (len(var.image_loader.filelist) - 1) // self.count_h + 1
		# scaled: row as close as possible
		# keymove: scroll as little as possible(but no extra whitespace)
		if scaled:
			# y shrink, never overflow
			if self.cursor[1] >= self.count_v:
				self.cursor[1] = self.count_v - 1
			# eliminate extra whitespace
			if cy_plus_offset >= self.cursor[1]: # not bottom
				#       <----count_v---->
				# <min1>+---------------+
				# ------+-----^---+<min2>
				# <-off0-><-cur^>
				# <-cy_pls_off->
				# <----totl------->
				off0 = cy_plus_offset - self.cursor[1]
				min1 = off0
				min2 = off0 + self.count_v - total_row
				scroll_up = max(0, min(min1, min2))
				self.y_offset = off0 - scroll_up
				self.cursor[1] += scroll_up
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
		self.grid_offset = var.grid_sizes[self.grid_size_idx] + self.grid_space
		count_h = (self.width() - self.grid_space) // self.grid_offset
		count_h = max(count_h, 1)
		count_v = (self.height() - self.grid_space) // self.grid_offset
		count_v = max(count_v, 1)
		if self.count_h == count_h and self.count_v == count_v:
			return False
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
		self.set_cursor(True)
		return True

	def refresh(self):
		grid_size = var.grid_sizes[self.grid_size_idx]
		for j in range(self.count_v):
			if j >= len(self.labels):
				self.labels.append([])
			for i in range(self.count_h):
				if i >= len(self.labels[j]):
					label = Thumbnail(self, i, j)
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
				if idx >= len(var.image_loader.filelist):
					self.labels[j][i].hide()
				else:
					if not var.image_loader.pixmaps[idx]:
						var.image_loader.pixmaps[idx] = var.image_loader.load_by_idx(idx)
					pixmap_resize = var.image_loader.pixmaps[idx].scaled(
						grid_size,
						grid_size,
						Qt.KeepAspectRatio,
						Qt.SmoothTransformation,
					)
					label.setPixmap(pixmap_resize)
					label.show()

	def resizeEvent(self, _e):
		self.reset_layout()

	def cursor_select(self, x, y):
		new_idx = (self.y_offset + y) * self.count_h + x
		if new_idx == var.current_idx:
			self.parent().image_mode()
			return
		var.current_idx = new_idx
		self.set_cursor(False)

	def offset_cursor(self, offset, abs_pos = False):
		old_idx = var.current_idx
		if abs_pos:
			var.current_idx = offset
		else:
			var.current_idx += offset
		if var.current_idx < 0:
			var.current_idx = old_idx
		elif var.current_idx >= len(var.image_loader.filelist):
			if (self.cursor[1] + self.y_offset + 1) * self.count_h < \
					len(var.image_loader.filelist):
				var.current_idx = len(var.image_loader.filelist) - 1
				self.set_cursor(False)
			else:
				var.current_idx = old_idx
		else:
			self.set_cursor(False)

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
		elif self.grid_size_idx >= len(var.grid_sizes):
			self.grid_size_idx = len(var.grid_sizes) - 1
		if old_idx == self.grid_size_idx:
			return
		self.parent().set_label()
		self.xreset_layout()

	def key_handler(self, e):
		if e.key() == Qt.Key_L:
			self.offset_cursor(1, False)
		elif e.key() == Qt.Key_H:
			self.offset_cursor(-1, False)
		elif e.key() == Qt.Key_J:
			self.offset_cursor(self.count_h, False)
		elif e.key() == Qt.Key_K:
			self.offset_cursor(-self.count_h, False)
		elif e.key() == Qt.Key_G:
			if var.keymod_shift:
				self.offset_cursor(len(var.image_loader.filelist) - 1, True)
			else:
				self.offset_cursor(0, True)
		elif e.key() == Qt.Key_O:
			self.set_zoom_level(-1, False)
		elif e.key() == Qt.Key_I:
			self.set_zoom_level(1, False)
		elif e.key() == Qt.Key_0:
			self.set_zoom_level(var.grid_size_idx_default, True)

	def mouseMoveEvent(self, e):
		if e.buttons() & Qt.MiddleButton:
			if self.mouse_mode != 1:
				self.last_mouse_pos = e.localPos()
				self.mouse_mode = 1
				return

			# ctrl zoom
			if var.keymod_control:
				self.setCursor(Qt.SizeVerCursor)
				dp = e.localPos() - self.last_mouse_pos
				if dp.y() > var.grid_move_zoom:
					self.set_zoom_level(-1, False)
					self.last_mouse_pos = e.localPos()
				elif dp.y() < -var.grid_move_zoom:
					self.set_zoom_level(1, False)
					self.last_mouse_pos = e.localPos()
			# pan
			else:
				self.setCursor(Qt.CrossCursor)
				dp = e.localPos() - self.last_mouse_pos
				if dp.y() > var.grid_move_pan:
					self.offset_cursor(self.count_h, False)
					self.last_mouse_pos = e.localPos()
				elif dp.y() < -var.grid_move_pan:
					self.offset_cursor(-self.count_h, False)
					self.last_mouse_pos = e.localPos()
				if dp.x() > var.grid_move_pan:
					self.offset_cursor(1, False)
					self.last_mouse_pos = e.localPos()
				elif dp.x() < -var.grid_move_pan:
					self.offset_cursor(-1, False)
					self.last_mouse_pos = e.localPos()
				self.parent().set_label()
		elif e.buttons() & Qt.LeftButton:
			if self.mouse_mode != 3:
				self.mouse_mode = 3
				et = e.localPos()
				cx = int((et.x() - self.grid_space / 2) / self.grid_offset)
				cy = int((et.y() - self.grid_space / 2) / self.grid_offset)
				if cx < self.count_h and cx >= 0 and \
					cy < self.count_v and cy >= 0:
					self.cursor_select(cx, cy)
		else:
			self.setCursor(Qt.ArrowCursor)
			self.mouse_mode = 0
