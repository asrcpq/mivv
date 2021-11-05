import sys
import argparse

from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QMainWindow
from PyQt5.QtGui import QPixmap, QKeyEvent
from PyQt5.QtCore import Qt

filelist = []
current_idx = 0

class Imageview(QWidget):
	def __init__(self, parent = None):
		super().__init__(parent)
		self.setStyleSheet("background-color: black;")
		self.label = QLabel("Imageview", self)
		self.label.setAlignment(Qt.AlignCenter)
		self.reload()
		self.render()

	def resizeEvent(self, event):
		self.render()

	def reload(self):
		global current_idx
		self.pixmap = QPixmap(filelist[current_idx])
	
	def render(self):
		pixmap_resize = self.pixmap.scaled(self.width(), self.height(), Qt.KeepAspectRatio)
		self.label.setPixmap(pixmap_resize)
		self.label.resize(self.width(), self.height())
		self.show()

class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		self.setWindowTitle("mivv")
		self.setGeometry(0, 0, 640, 480)
		self.image_view = Imageview(self)
		self.show()

	def keyPressEvent(self, e: QKeyEvent):
		global current_idx
		if e.key() == Qt.Key_Space or e.key() == Qt.Key_N:
			current_idx += 1
			if current_idx >= len(filelist):
				current_idx = len(filelist) - 1
		elif e.key() == Qt.Key_Backspace or e.key() == Qt.Key_P:
			current_idx -= 1
			if current_idx < 0:
				current_idx = 0
		elif e.key() == Qt.Key_Escape or e.key() == Qt.Key_Q:
			exit(0)
		else:
			return
		self.image_view.reload()
		self.image_view.render()

	def resizeEvent(self, event):
		self.image_view.resize(self.width(), self.height())

def build_parser():
	parser = argparse.ArgumentParser(description = "immv")
	parser.add_argument('-i', action = "store_true")
	return parser

if __name__ == '__main__':
	args, unknown_args = build_parser().parse_known_args()
	if args.i:
		filelist_string = sys.stdin.read()
		filelist = filelist_string.split()
		for file in filelist:
			print("Read", file)
	else:
		filelist = unknown_args
	if len(filelist) == 0:
		print("No image file specified, exiting")
		exit(1)
	app = QApplication([])
	main_window = MainWindow()
	app.exec_()

