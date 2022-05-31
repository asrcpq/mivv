from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage
import sys
from time import sleep

#class MainWindow(QMainWindow):
#	def __init__(self):
#		super().__init__()
#		self.show()

def getter(i):
	print(i)

class TestThread(QThread):
	result = Signal(object)

	def __init__(self):
		QThread.__init__(self)

	def run(self):
		while True:
			self.result.emit(QImage())
			sleep(1)


app = QApplication(sys.argv)
thread = TestThread()
thread.result.connect(getter)
thread.start()
#w = MainWindow()
#w.hide()
app.exec()
