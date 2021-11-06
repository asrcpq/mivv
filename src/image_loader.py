import os
from glob import glob
from pathlib import Path

from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

import var

class ImageLoader():
	def __init__(self):
		self.filelist = []
		self.cached_state = []
		self.pixmaps = []

	def preload(self, filelist_tmp, load_all = True):
		while filelist_tmp:
			print(f"[2K{len(self.filelist)}:{len(filelist_tmp)}", end = "\r")
			file = filelist_tmp[-1]
			filelist_tmp.pop()
			if os.path.isdir(file):
				if var.expand_dir:
					filelist_tmp += sorted(glob(os.path.join(file, "*")), reverse = True)
				continue
			# TODO: async load
			state = self.validate(file)
			if state == 0:
				continue
			elif state == 1:
				self.cached_state.append(True)
			elif state == 2:
				self.cached_state.append(False)
			else:
				exit(127)
			# print("Read", file)
			self.filelist.append(file)
			self.pixmaps.append(None)
		if load_all:
			for idx in range(len(self.filelist)):
				pixmap = self.load_by_idx(idx)
				self.pixmaps[idx] = pixmap
		if len(self.filelist) == 0:
			print("No image file specified, exiting")
			exit(1)

	def load_by_idx(self, idx):
		file = self.filelist[idx]
		abspath = os.path.abspath(file)
		if self.cached_state[idx]:
			pixmap = self.load_cache(abspath)
		else:
			pixmap = self.create_cache(abspath)
		return pixmap

	# return
	# 0: invalid file
	# 1: cache found
	# 2: no cache
	def validate(self, path):
		abspath = os.path.abspath(path)
		if not os.path.exists(abspath):
			# remove cache? maybe not
			return 0
		if abspath.startswith(var.cache_path):
			return 1
		cached_path = var.cache_path + abspath + ".jpg"
		if os.path.exists(cached_path):
			return 1
		_filename, ext = os.path.splitext(abspath)
		if ext not in var.valid_ext:
			return 0
		return 2
	
	# nocheck
	def create_cache(self, abspath):
		pixmap = QPixmap(abspath)
		if pixmap.isNull():
			print("Read fail:", abspath)
			return None
		print("Cached:", abspath)
		cached_path = var.cache_path + abspath + ".jpg"
		dirname = os.path.dirname(cached_path)
		Path(dirname).mkdir(parents = True, exist_ok = True)
		pixmap_resize = pixmap.scaled(
			var.cache_size,
			var.cache_size,
			Qt.KeepAspectRatio,
			Qt.SmoothTransformation,
		)
		pixmap_resize.save(cached_path)
		return pixmap_resize
	
	# nocheck
	def load_cache(self, abspath):
		if abspath.startswith(var.cache_path):
			return QPixmap(abspath)
		cached_path = var.cache_path + abspath + ".jpg"
		if os.path.getmtime(abspath) > os.path.getmtime(cached_path):
			print("Update cache:", abspath)
			return create_cache(path)
		else:
			return QPixmap(cached_path)
