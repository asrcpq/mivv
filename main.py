import argparse

from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtGui import QPixmap, QKeyEvent
from PyQt5.QtCore import Qt

filelist = []
current_idx = 0

class Imageview(QWidget):
	def __init__(self):
		super().__init__()
		self.setStyleSheet("background-color: black;")
		self.setWindowTitle("mivv")
		self.setGeometry(0, 0, 640, 480)
		self.label = QLabel("Black", self)
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
		self.reload()
		self.render()

def build_parser():
	parser = argparse.ArgumentParser(description = "immv")
	parser.add_argument('-i', dest = "filelist_from_stdin")
	return parser

if __name__ == '__main__':
	args, unknown_args = build_parser().parse_known_args()
	filelist = unknown_args
	if len(filelist) == 0:
		print("No image file specified, exiting")
		exit(1)
	app = QApplication([])
	image_view = Imageview()
	app.exec_()

