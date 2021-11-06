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
	return parser

# return
# 0: invalid file
# 1: cache found
# 2: no cache
def validate(path):
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
def create_cache(path):
	abspath = os.path.abspath(path)
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

# nocheck
def load_cache(path):
	abspath = os.path.abspath(path)
	if abspath.startswith(var.cache_path):
		return QPixmap(abspath)
	cached_path = var.cache_path + abspath + ".jpg"
	return QPixmap(cached_path)

if __name__ == '__main__':
	args, unknown_args = build_parser().parse_known_args()
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
		print(f"[2K{len(var.filelist)}:{len(filelist_tmp)}", end = "\r")
		file = filelist_tmp[-1]
		filelist_tmp.pop()
		if os.path.isdir(file):
			if not args.i:
				filelist_tmp += sorted(glob(os.path.join(file, "*")), reverse = True)
			continue
		# TODO: async load
		state = validate(file)
		if state == 0:
			continue
		elif state == 1:
			var.cached_state.append(True)
		elif state == 2:
			var.cached_state.append(False)
		else:
			exit(127)
		# print("Read", file)
		var.filelist.append(file)
		#print(file)
	for idx, file in enumerate(var.filelist):
		if var.cached_state[idx] == 1:
			pixmap = load_cache(file)
		elif var.cached_state[idx] == 2:
			pixmap = create_cache(file)
		else:
			exit(127)
		var.pixmaps.append(pixmap)
	if len(var.filelist) == 0:
		print("No image file specified, exiting")
		exit(1)
	main_window = MainWindow()
	app.exec_()
