import zipfile
from PySide6.QtGui import QImage
import var

def kra2qimage(path):
	try:
		f = zipfile.ZipFile(path)
		s = f.read("mergedimage.png")
		img = QImage()
		img.loadFromData(s)
		return img
	except Exception as e:
		var.logger.error(str(e))
		return None
