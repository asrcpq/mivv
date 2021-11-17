import logging
import sys
import os
import argparse
from time import time

from PyQt5.QtWidgets import QApplication

from mivv.main_window import MainWindow
from mivv.image_loader import ImageLoader
from mivv import var

startup_time = time()

def build_parser():
	parser = argparse.ArgumentParser(description = "mivv")
	parser.add_argument('-i', action = "store_true", help = "filelist from stdin")
	parser.add_argument('-t', action = "store_true", help = "start in grid mode")
	parser.add_argument('-c', action = "store_true", help = "gc cache and exit")
	parser.add_argument('-p', "--private", action = "store_true", help = "never write")
	parser.add_argument(
		'-l',
		'--loglevel',
		type = str,
		help = "set log level(debug, info, warn, error, critical)",
	)
	parser.add_argument(
		"--expand-level",
		type = int,
		default = 0,
		help = "expand level: 1(ignore dir), 2, 3(recursive)",
	)
	parser.add_argument('-r', action = "store_true", help = "recursive(set expand-level to 3)")
	parser.add_argument(
		"--sort",
		type = int,
		default = 2,
		help = "sort method: 0(disable), 1(dict), 2(default, natural)",
	)
	parser.add_argument(
		'--preload-thumbnail',
		action = "store_true",
		help = "display scaled thumbnail while loading",
	)
	parser.add_argument('path', type = str, nargs='*')
	return parser

def gc_cache():
	for root, _directories, filenames in os.walk(var.cache_path):
		for filename in filenames:
			cache = f"{root}/{filename}"
			root_path = "/" + os.path.relpath(cache, var.cache_path)[:-4]
			if not os.path.isfile(root_path):
				print("clean", root_path)
				os.remove(cache)

def set_loglevel(loglevel):
	if loglevel == "debug":
		var.logger.setLevel(logging.DEBUG)
	elif loglevel == "info":
		var.logger.setLevel(logging.INFO)
	elif loglevel == "warn":
		var.logger.setLevel(logging.WARN)
	elif loglevel == "error":
		var.logger.setLevel(logging.ERROR)
	elif loglevel == "critical":
		var.logger.setLevel(logging.CRITICAL)
	else:
		raise Exception("Unknown log level:", loglevel)

def loader_callback():
	if not var.main_window:
		var.main_window = MainWindow()
		# initialize_view use var.main_window, thus needs to be split
		var.main_window.initialize_view()
	var.main_window.loader_callback()

if __name__ == '__main__':
	args = build_parser().parse_args()
	if args.c:
		gc_cache()
		sys.exit()
	if args.t:
		var.start_in_grid_mode = True
	if args.private:
		var.private_mode = True
	if args.loglevel:
		var.loglevel = args.loglevel
	set_loglevel(var.loglevel)
	if args.i:
		filelist_string = sys.stdin.read()
		filelist = filelist_string.split('\n')
	else:
		filelist = args.path
	if args.expand_level == 0:
		if args.i:
			expand_level = 1
		else:
			expand_level = 2
	else:
		expand_level = args.expand_level
	if args.r:
		expand_level = 3
	if args.preload_thumbnail:
		var.preload_thumbnail = True
	var.logger.info(f"Expand level: {expand_level}")
	app = QApplication([])
	filelist_raw = list(reversed(filelist))
	image_loader = ImageLoader(loader_callback)
	image_loader.load(filelist_raw, expand_level, args.sort)
	var.image_loader = image_loader
	var.logger.info(f"Elapsed: {time() - startup_time:.03f} secs")
	var.app = app
	app.exec()
	var.image_loader.stop()
