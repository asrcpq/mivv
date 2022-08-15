from PySide6.QtGui import QImage
from PySide6.QtCore import Signal, QThread
import time
from kra2qimage import kra2qimage

class _ContentLoaderThread(QThread):
	result = Signal(object, str)

	def __init__(self):
		QThread.__init__(self)
		self.filename = None
		self.run_flag = False
		self.ty = None

	def feed_data(self, filename, ty):
		self.filename = filename
		self.ty = ty
		self.run_flag = True
		self.start()

	def run(self):
		while self.run_flag:
			self.run_flag = False
			time.sleep(0.001)
			if self.ty == 1:
				result = QImage(self.filename)
			elif self.ty == 2:
				result = self.filename
			elif self.ty == 3:
				result = self.filename
			elif self.ty == 4:
				result = kra2qimage(self.filename)
			else:
				result = None
			if self.run_flag:
				continue
			self.result.emit(result, self.filename)

	def stop(self):
		self.wait()
