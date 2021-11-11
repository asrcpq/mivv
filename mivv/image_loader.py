import os
import sys
from glob import glob
from pathlib import Path

from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

import var

class ImageLoader():
	def __init__(self):
		self.filelist = []
		self.typelist = []
		self.cached_state = []
		self.pixmaps = []

	def preload(self, filelist_tmp, load_all = True):
		while filelist_tmp:
			# print(f"[2K{len(self.filelist)}:{len(filelist_tmp)}", end = "\r")
			file = filelist_tmp[-1]
			filelist_tmp.pop()
			if not os.access(file, os.R_OK):
				var.logger.warn(f"Permission denied: {file}")
				continue
			if os.path.isdir(file):
				if var.expand_dir:
					file_filtered = []
					for file in glob(os.path.join(file, "*")):
						if os.path.isfile(file):
							file_filtered.append(file)
					filelist_tmp += sorted(file_filtered, reverse = True)
				continue
			state, ty = self.validate(file)
			if state == 0:
				continue
			if state == 1:
				self.cached_state.append(True)
			elif state == 2:
				self.cached_state.append(False)
			else:
				sys.exit(127)
			self.filelist.append(file)
			self.typelist.append(ty)
			self.pixmaps.append(None)
		if load_all:
			self.load_all()
		if len(self.filelist) == 0:
			var.logger.error("No image file specified, exiting")
			sys.exit(1)

	def load_all(self):
		for idx in range(len(self.filelist)):
			pixmap = self.load_by_idx(idx)
			self.pixmaps[idx] = pixmap

	def load_by_idx(self, idx):
		file = self.filelist[idx]
		abspath = os.path.abspath(file)
		if self.cached_state[idx]:
			pixmap = self.load_cache(abspath)
		else:
			pixmap = self.create_cache(abspath)
		var.logger.debug(f"Loaded: {file}")
		return pixmap

	# return (status, ext_type)
	# 0: invalid file
	# 1: cache found
	# 2: no cache
	@staticmethod
	def validate(path):
		abspath = os.path.abspath(path)
		if not os.path.exists(abspath):
			# remove cache? maybe not
			return (0, 0)
		_filename, ext = os.path.splitext(abspath)
		if ext not in var.ext_type:
			return (0, 0)
		ty = var.ext_type[ext]
		if abspath.startswith(var.cache_path):
			return (1, ty)
		cached_path = var.cache_path + abspath + ".jpg"
		if os.path.exists(cached_path):
			return (1, ty)
		return (2, ty)

	# nocheck, abspath must exist
	@staticmethod
	def create_cache(abspath):
		pixmap = QPixmap(abspath)
		cached_path = var.cache_path + abspath + ".jpg"
		if pixmap.isNull():
			raise Exception(f"Read fail: {abspath}")
		elif pixmap.width() <= var.cache_size or \
			pixmap.height() <= var.cache_size:
			var.logger.info(f"Touch-cached: {abspath}")
			open(cached_path, "w").close()
			return
		dirname = os.path.dirname(cached_path)
		Path(dirname).mkdir(parents = True, exist_ok = True)
		pixmap_resize = pixmap.scaled(
			var.cache_size,
			var.cache_size,
			Qt.KeepAspectRatio,
			Qt.SmoothTransformation,
		)
		pixmap_resize.save(cached_path)
		var.logger.info(f"Cached: {abspath}")
		return pixmap_resize

	# nocheck, abspath, cached_path must exist
	def load_cache(self, abspath):
		cached_path = var.cache_path + abspath + ".jpg"
		if abspath.startswith(var.cache_path) or os.path.getsize(cached_path) == 0:
			var.logger.debug(f"Use original file for thumbnail: {abspath}")
			return QPixmap(abspath)
		if os.path.getmtime(abspath) > os.path.getmtime(cached_path):
			var.logger.info(f"Update: {abspath}")
			return self.create_cache(abspath)
		return QPixmap(cached_path)
