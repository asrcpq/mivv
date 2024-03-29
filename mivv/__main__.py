import logging
import sys
import os
import argparse

from PySide6.QtWidgets import QApplication

from mivv.main_window import MainWindow
from mivv.thumbnail_loader import ThumbnailLoader
from mivv import var

def build_parser():
	parser = argparse.ArgumentParser(description = "mivv")
	parser.add_argument('-i', action = "store_true", help = "filelist from stdin")
	parser.add_argument('-t', action = "store_true", help = "start in grid mode")
	parser.add_argument('-c', action = "store_true", help = "gc cache and exit")
	parser.add_argument('-f', action = "store_true", help = "fullscreen")
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
	parser.add_argument(
		'--bg-color',
		type = str,
		help = "set bg color(qt stylesheet color format)",
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

def main():
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
	if args.f:
		var.fullscreen = True
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
	if args.bg_color:
		var.background = args.bg_color
	var.logger.info(f"Expand level: {expand_level}")
	app = QApplication([])
	var.logger.debug("Application created")
	filelist_raw = list(reversed(filelist))
	var.logger.debug("Generated filelist")
	thumbnail_loader = ThumbnailLoader(loader_callback)
	var.thumbnail_loader = thumbnail_loader
	var.logger.debug("Initialized image loader")
	thumbnail_loader.preload(filelist_raw, expand_level, args.sort)
	var.logger.debug("Preload okay")
	var.app = app
	var.logger.debug("Starting app")
	app.exec()
	var.thumbnail_loader.stop()

if __name__ == '__main__':
	main()
