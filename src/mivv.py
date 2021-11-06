import sys
import os
import argparse
from glob import glob
from pathlib import Path

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

from main_window import MainWindow

import var

def build_parser():
	parser = argparse.ArgumentParser(description = "immv")
	parser.add_argument('-i', action = "store_true", help = "var.filelist from stdin")
	parser.add_argument('-t', action = "store_true", help = "start in grid mode")
	parser.add_argument('-c', action = "store_true", help = "overwrite cache")
	return parser

def cached_read(path):
	abspath = os.path.abspath(path)
	if not os.path.exists(abspath):
		# remove cache? maybe not
		return None
	if abspath.startswith(var.cache_path):
		return QPixmap(abspath)
	cached_path = var.cache_path + abspath + ".jpg"
	if os.path.exists(cached_path) and not var.overwrite_cache:
		return QPixmap(cached_path)
	_filename, ext = os.path.splitext(abspath)
	if ext not in var.valid_ext:
		return None
	pixmap = QPixmap(abspath)
	if pixmap.isNull():
		print("Read fail:", abspath)
		return None
	print("Gen cache:", abspath)
	dirname = os.path.dirname(cached_path)
	Path(dirname).mkdir(parents = True, exist_ok = True)
	pixmap_resize = pixmap.scaled(
		var.grid_size,
		var.grid_size,
		Qt.KeepAspectRatio,
		Qt.SmoothTransformation,
	)
	pixmap_resize.save(cached_path)
	return pixmap_resize

if __name__ == '__main__':
	args, unknown_args = build_parser().parse_known_args()
	if args.c:
		var.overwrite_cache = True
	if args.t:
		var.start_in_grid_mode = True
	if args.i:
		filelist_string = sys.stdin.read()
		var.filelist = filelist_string.split()
	else:
		var.filelist = unknown_args
	app = QApplication([])
	filelist_tmp = list(reversed(var.filelist))
	var.filelist = []
	while filelist_tmp:
		file = filelist_tmp[-1]
		filelist_tmp.pop()
		if os.path.isdir(file):
			filelist_tmp += sorted(glob(os.path.join(file, "*")), reverse = True)
			continue
		# TODO: async load
		pixmap = cached_read(file)
		if not pixmap:
			print("Skip", file)
			continue
		# print("Read", file)
		var.pixmaps.append(pixmap)
		var.filelist.append(file)
	if len(var.filelist) == 0:
		print("No image file specified, exiting")
		exit(1)
	main_window = MainWindow()
	app.exec_()
