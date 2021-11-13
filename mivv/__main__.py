from time import time
startup_time = time()

import logging
import sys
import os
import argparse

from PyQt5.QtWidgets import QApplication

from main_window import MainWindow
import var

def build_parser():
	parser = argparse.ArgumentParser(description = "mivv")
	parser.add_argument('-l', action = "store_true", help = "lazy loading mode")
	parser.add_argument('-i', action = "store_true", help = "filelist from stdin")
	parser.add_argument('-t', action = "store_true", help = "start in grid mode")
	parser.add_argument('-c', action = "store_true", help = "gc cache and exit")
	parser.add_argument('-p', action = "store_true", help = "never write")
	parser.add_argument(
		'--loglevel',
		type = str,
		default = "warn",
		help = "set log level(default: warn)",
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

if __name__ == '__main__':
	args = build_parser().parse_args()
	if args.c:
		gc_cache()
		sys.exit()
	if args.l:
		var.load_all = False
	if args.t:
		var.start_in_grid_mode = True
	if args.p:
		var.private_mode = True
	set_loglevel(args.loglevel)
	if args.i:
		var.expand_dir = False
		filelist_string = sys.stdin.read()
		filelist = filelist_string.split('\n')
	else:
		filelist = args.path
	app = QApplication([])
	filelist_tmp = list(reversed(filelist))
	var.image_loader.preload(filelist_tmp, var.load_all)
	main_window = MainWindow()
	var.logger.info(f"Elapsed: {time() - startup_time:.03f} secs")
	app.exec()
