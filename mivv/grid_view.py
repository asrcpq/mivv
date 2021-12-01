from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt

from mivv.thumbnail import Thumbnail
from mivv.keydef import Keydef
from mivv import var

class Gridview(QWidget):
	def __init__(self, parent = None):
		super().__init__(parent)
		self.setMouseTracking(True)
		self.setStyleSheet(f"background-color: {var.background};")
		self.y_offset = 0
		self.grid_size_idx = 2
		self.grid_offset = None
		self.count_h = 0
		self.count_v = 0
		self.cursor = [0, 0]
		self.labels = []
		self.mouse_mode = 0
		self.filelist_len = len(var.image_loader.filelist) # cached length for update check
		self.last_mouse_pos = None

	def _get_idx(self, i, j):
		return (j + self.y_offset) * self.count_h + i

	def toggle_highlight(self, up):
		try:
			if up:
				self.labels[self.cursor[1]][self.cursor[0]]\
					.setStyleSheet(f"border: 3px double {var.border_color};")
			else:
				self.labels[self.cursor[1]][self.cursor[0]]\
					.setStyleSheet("border: none;")
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

	# xreset is for thumbnail resize
	# reset is for window resize
	def _xreset_layout(self):
		for label_row in self.labels:
			for label in label_row:
				label.close()
		self.labels = []
		self.reset_layout()

	def update_filelist(self):
		var_flen = len(var.image_loader.filelist)
		if self.filelist_len == var_flen:
			return
		if self.filelist_len > var_flen:
			raise Exception("Global filelist shrinked, This is a bug.")
		var.logger.debug("Update grid view filelist")
		if (
			self.y_offset * self.count_h <= self.filelist_len and \
			self.filelist_len < (self.y_offset + self.count_v) * self.count_h \
		):
			self.refresh()
		self.filelist_len = var_flen

	def reset_layout(self):
		self.grid_offset = var.grid_sizes[self.grid_size_idx] + var.grid_space
		count_h = (self.width() - var.grid_space) // self.grid_offset
		count_h = max(count_h, 1)
		count_v = (self.height() - var.grid_space) // self.grid_offset
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

	# no_update means don't change existing thumbnail
	# used for filelist update
	def refresh(self):
		var.logger.debug('Grid mode refresh')
		grid_size = var.grid_sizes[self.grid_size_idx]
		for j in range(self.count_v):
			if j >= len(self.labels):
				self.labels.append([])
			for i in range(self.count_h):
				if i >= len(self.labels[j]):
					label = Thumbnail(self, i, j)
					label.setGeometry(
						i * self.grid_offset + var.grid_space,
						j * self.grid_offset + var.grid_space,
						grid_size,
						grid_size,
					)
					self.labels[j].append(label)
				else:
					label = self.labels[j][i]
				idx = self._get_idx(i, j)
				if idx >= len(var.image_loader.filelist):
					self.labels[j][i].hide()
				else:
					if not var.image_loader.pixmaps[idx]:
						var.logger.warning(f"Not loaded {idx}")
					else:
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

	def _cursor_select(self, x, y):
		new_idx = (self.y_offset + y) * self.count_h + x
		if new_idx == var.current_idx:
			self.setCursor(Qt.WaitCursor)
			self.parent().image_mode()
			return
		var.current_idx = new_idx
		self.set_cursor(False)

	def _offset_cursor(self, offset, abs_pos = False):
		old_idx = var.current_idx
		if abs_pos:
			var.current_idx = offset
		else:
			var.current_idx += offset
		if var.current_idx < 0:
			if offset + self.count_h < 0:
				var.logger.debug("scroll overflow restrict 0%")
				var.current_idx %= self.count_h
			else:
				var.logger.debug("scroll overflow restrict 0=")
				var.current_idx = 0
			self.set_cursor(False)
		elif var.current_idx >= len(var.image_loader.filelist):
			if (self.cursor[1] + self.y_offset + 1) * self.count_h < \
					len(var.image_loader.filelist):
				var.logger.debug("scroll overflow restrict")
				var.current_idx = len(var.image_loader.filelist) - 1
				self.set_cursor(False)
			else:
				var.logger.debug("scroll overflow cancel max")
				var.current_idx = old_idx
		else:
			self.set_cursor(False)

	def _set_zoom_level(self, dz, abs_zoom = False):
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
		self._xreset_layout()

	def key_handler(self, k):
		if k == Keydef.grid_view_right:
			self._offset_cursor(1, False)
		elif k == Keydef.grid_view_left:
			self._offset_cursor(-1, False)
		elif k == Keydef.grid_view_down:
			self._offset_cursor(self.count_h, False)
		elif k == Keydef.grid_view_up:
			self._offset_cursor(-self.count_h, False)
		elif k == Keydef.grid_view_last:
			self._offset_cursor(len(var.image_loader.filelist) - 1, True)
		elif k == Keydef.grid_view_first:
			self._offset_cursor(0, True)
		elif k == Keydef.grid_view_zoom_out:
			self._set_zoom_level(-1, False)
		elif k == Keydef.grid_view_zoom_in:
			self._set_zoom_level(1, False)
		elif k == Keydef.grid_view_zoom_origin:
			self._set_zoom_level(var.grid_size_idx_default, True)
		elif k == Keydef.grid_hol:
			self._offset_cursor(-self.cursor[0], False)
		elif k == Keydef.grid_eol:
			self._offset_cursor(self.count_h - self.cursor[0] - 1, False)
		elif k == Keydef.grid_page_up:
			self._offset_cursor(-self.count_h * self.count_v)
		elif k == Keydef.grid_page_down:
			self._offset_cursor(self.count_h * self.count_v)
		elif k == Keydef.grid_page_up_half:
			self._offset_cursor(-self.count_h * (1 + (self.count_v - 1) // 2))
		elif k == Keydef.grid_page_down_half:
			self._offset_cursor(self.count_h * (1 + (self.count_v - 1) // 2))
		return True

	def wheelEvent(self, e):
		ang = e.angleDelta()
		if ang.y() < 0:
			self._offset_cursor(self.count_h)
		elif ang.y() > 0:
			self._offset_cursor(-self.count_h)
		if ang.x() < 0:
			self._offset_cursor(-1)
		elif ang.x() > 0:
			self._offset_cursor(1)

	def mousePressEvent(self, e):
		if e.buttons() & Qt.LeftButton:
			if self.mouse_mode != 3:
				self.mouse_mode = 3
			et = e.localPos()
			cx = int((et.x() - var.grid_space / 2) / self.grid_offset)
			cy = int((et.y() - var.grid_space / 2) / self.grid_offset)
			if cx < self.count_h and cx >= 0 and \
				cy < self.count_v and cy >= 0:
				self._cursor_select(cx, cy)

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
					self._set_zoom_level(-1, False)
					self.last_mouse_pos = e.localPos()
				elif dp.y() < -var.grid_move_zoom:
					self._set_zoom_level(1, False)
					self.last_mouse_pos = e.localPos()
				var.main_window.set_basic_label()
			# pan
			else:
				self.setCursor(Qt.CrossCursor)
				dp = e.localPos() - self.last_mouse_pos
				if dp.y() > var.grid_move_pan:
					self._offset_cursor(self.count_h, False)
					self.last_mouse_pos = e.localPos()
				elif dp.y() < -var.grid_move_pan:
					self._offset_cursor(-self.count_h, False)
					self.last_mouse_pos = e.localPos()
				if dp.x() > var.grid_move_pan:
					self._offset_cursor(1, False)
					self.last_mouse_pos = e.localPos()
				elif dp.x() < -var.grid_move_pan:
					self._offset_cursor(-1, False)
					self.last_mouse_pos = e.localPos()
				var.main_window.set_basic_label()
		else:
			self.setCursor(Qt.ArrowCursor)
			self.mouse_mode = 0
