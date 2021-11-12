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
			file = filelist_tmp[-1]
			filelist_tmp.pop()
			var.logger.debug(f"Preprocessing: {file}")
			if not file or file.isspace():
				continue
			if not os.access(file, os.R_OK):
				var.logger.warning(f"Permission denied: {file}")
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
			var.logger.error("Nothing loaded, exiting")
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
		if not var.cache_path:
			return (2, ty)
		if abspath.startswith(var.cache_path):
			return (1, ty)
		cached_path = var.cache_path + abspath + ".jpg"
		if os.path.exists(cached_path):
			return (1, ty)
		return (2, ty)

	@staticmethod
	def save_cache(pixmap, path):
		if var.private_mode or not var.cache_path:
			var.logger.debug(f"No cache(private mode): {path}")
			return
		cached_path = var.cache_path + path + ".jpg"
		dirname = os.path.dirname(path)
		Path(dirname).mkdir(parents = True, exist_ok = True)
		if pixmap:
			var.logger.info(f"Cached: {path}")
			pixmap.save(path)
		else:
			var.logger.info(f"Touch-cached: {path}")
			open(path, "w").close()

	# nocheck, abspath must exist
	def create_cache(self, abspath):
		var.logger.info(f"Generating cache: {abspath}")
		pixmap = QPixmap(abspath)
		if pixmap.isNull():
			var.logger.warning(f"Create cache read fail: {abspath}")
			return None
		if pixmap.width() <= var.cache_size or \
			pixmap.height() <= var.cache_size:
			self.save_cache(None, abspath)
			return pixmap
		pixmap_resize = pixmap.scaled(
			var.cache_size,
			var.cache_size,
			Qt.KeepAspectRatio,
			Qt.SmoothTransformation,
		)
		self.save_cache(pixmap_resize, abspath)
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
