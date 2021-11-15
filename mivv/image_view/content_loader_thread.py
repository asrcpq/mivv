from PyQt5.QtGui import QImage
from PyQt5.QtCore import pyqtSignal, QThread

class _ContentLoaderThread(QThread):
	result = pyqtSignal(object)

	def __init__(self):
		QThread.__init__(self)
		self.filenames = None
		self.run_flag = False
		self.tys = None

	def feed_data(self, filename, ty):
		self.filename = filename
		self.ty = ty
		self.run_flag = True
		self.start()

	def run(self):
		while self.run_flag:
			self.run_flag = False
			if self.ty == 1:
				result = QImage(self.filename)
			elif self.ty == 2:
				result = self.filename
				# result = QMovie(self.filename)
			else:
				result = None
			if self.run_flag:
				continue
			self.result.emit(result)

	def stop(self):
		self.wait()
