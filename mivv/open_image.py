from PySide6.QtGui import QImage
from jxlpy import JXLImagePlugin
from PIL import Image
from PIL.ImageQt import ImageQt

def open_image(filename):
	if filename.endswith(".jxl"):
		result = Image.open(filename)
		result = ImageQt(result)
	else:
		result = QImage(filename)
	return result
