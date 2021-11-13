import os
import sys
from glob import glob
from pathlib import Path

from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal, QThread

import var

class ImageLoader():
	def __init__(self, callback):
		self.typelist = []
		self.filelist = []
		self.pixmaps = []
		self.has_image = False
		self.finished = False
		self.has_image_callback = callback

	# None None None => finished
	def get_result(self, pixmap, file, ty):
		if not pixmap:
			self.finished = True
			return
		var.logger.debug(f"Received: {file}")
		self.pixmaps.append(pixmap)
		self.filelist.append(file)
		self.typelist.append(ty)
		if not self.has_image:
			self.has_image = True
			self.has_image_callback()

	def load(self, filelist):
		self.loader_thread = ImageLoaderThread(filelist)
		self.loader_thread.result.connect(self.get_result)
		self.loader_thread.start()

	def stop(self):
		var.logger.debug("Stopping loader thread.")
		self.loader_thread.stop()

class ImageLoaderThread(QThread):
	result = pyqtSignal(object, str, int)

	def __init__(self, filelist):
		QThread.__init__(self)
		self.filelist = filelist
		self.alive = True

	def run(self):
		filelist = self.filelist
		while filelist:
			if not self.alive:
				return
			file = filelist[-1]
			filelist.pop()
			var.logger.debug(f"Preprocessing: {file}")
			if not file or file.isspace():
				continue
			if not os.access(file, os.R_OK):
				var.logger.error(f"Permission denied: {file}")
				continue
			if os.path.isdir(file):
				if var.expand_dir:
					file_filtered = []
					for file in glob(os.path.join(file, "*")):
						if os.path.isfile(file):
							file_filtered.append(file)
					filelist += sorted(file_filtered, reverse = True)
				continue
			if not os.path.exists(file):
				continue
			_filename, ext = os.path.splitext(file)
			if ext not in var.ext_type:
				continue
			ty = var.ext_type[ext]
			abspath = os.path.abspath(file)
			pixmap = self._load_cache(abspath)
			var.logger.debug(f"Loaded: {file}")
			if pixmap is None:
				var.logger.error(f"Load fail: {file}")
				continue
			self.result.emit(pixmap, file, ty)
		self.result.emit(None, None, None)

	def stop(self):
		self.alive = False
		self.wait()

	@staticmethod
	def _save_cache(pixmap, path):
		if var.private_mode or not var.cache_path:
			var.logger.debug(f"No cache(private mode): {path}")
			return
		cached_path = var.cache_path + path + ".jpg"
		dirname = os.path.dirname(cached_path)
		Path(dirname).mkdir(parents = True, exist_ok = True)
		if pixmap:
			var.logger.info(f"Cached: {cached_path}")
			pixmap.save(cached_path)
		else:
			var.logger.info(f"Touch-cached: {cached_path}")
			open(cached_path, "w").close()

	# nocheck, abspath must exist
	def _create_cache(self, abspath):
		var.logger.info(f"Generating cache: {abspath}")
		pixmap = QPixmap(abspath)
		if pixmap.isNull():
			var.logger.warning(f"Create cache read fail: {abspath}")
			return None
		if pixmap.width() <= var.cache_size or \
			pixmap.height() <= var.cache_size:
			self._save_cache(None, abspath)
			return pixmap
		pixmap_resize = pixmap.scaled(
			var.cache_size,
			var.cache_size,
			Qt.KeepAspectRatio,
			Qt.SmoothTransformation,
		)
		self._save_cache(pixmap_resize, abspath)
		return pixmap_resize

	# nocheck, abspath, cached_path must exist
	def _load_cache(self, abspath):
		cached_path = var.cache_path + abspath + ".jpg"
		if not var.cache_path or abspath.startswith(var.cache_path):
			var.logger.debug(f"Original file as cache: {abspath}")
			return QPixmap(abspath)
		cached_path = var.cache_path + abspath + ".jpg"
		if not os.path.exists(cached_path):
			var.logger.info(f"Generate cache: {abspath}")
			return self._create_cache(abspath)
		if os.path.getmtime(abspath) > os.path.getmtime(cached_path):
			var.logger.info(f"Update cache: {abspath}")
			return self._create_cache(abspath)
		if os.path.getsize(cached_path) == 0:
			var.logger.debug(f"Original file as cache: {abspath}")
			return QPixmap(abspath)
		return QPixmap(cached_path)
