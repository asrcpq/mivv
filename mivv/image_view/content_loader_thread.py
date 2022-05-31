from PySide6.QtGui import QImage
from PySide6.QtCore import Signal, QThread

class _ContentLoaderThread(QThread):
	result = Signal(object)

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
			if self.ty == 1:
				result = QImage(self.filename)
			elif self.ty == 2:
				result = self.filename
			elif self.ty == 3:
				result = self.filename
			else:
				result = None
			if self.run_flag:
				continue
			self.result.emit(result)

	def stop(self):
		self.wait()
