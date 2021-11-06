import sys
import os
import argparse

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

from main_window import MainWindow
from image_loader import *

import var

def build_parser():
	parser = argparse.ArgumentParser(description = "immv")
	parser.add_argument('-l', action = "store_true", help = "load thumbnail on need")
	parser.add_argument('-i', action = "store_true", help = "filelist from stdin")
	parser.add_argument('-t', action = "store_true", help = "start in grid mode")
	return parser

if __name__ == '__main__':
	args, unknown_args = build_parser().parse_known_args()
	if args.l:
		var.load_all = False
	if args.t:
		var.start_in_grid_mode = True
	if args.i:
		var.expand_dir = False
		filelist_string = sys.stdin.read()
		var.filelist = filelist_string.split('\n')
	else:
		var.filelist = unknown_args
	app = QApplication([])
	filelist_tmp = list(reversed(var.filelist))
	var.image_loader.preload(filelist_tmp, var.load_all)
	main_window = MainWindow()
	app.exec_()
