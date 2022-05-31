from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtGui import QPainter, QPen, QPixmap
from PySide6.QtCore import Qt, QRectF, QSizeF, QRect

from mivv import var
from .patch_manager import PatchManager
from .common_brushes import DummyBrush

class Canvas(QPixmap):
	def __init__(self, size):
		super().__init__(size.width(), size.height())
		self.positions = [None, None] # last, new
		self.fill(Qt.transparent)
		self.pen = QPen(Qt.green)
		self.pen.setWidth(5)
		self.patch_manager = PatchManager()
		self.mb = DummyBrush()

	def draw(self, pos, pressure):
		pixmap_patch, p = self.mb.draw(self, pos, pressure)
		if not pixmap_patch:
			return None
		old_pixmap = self.copy(QRect(p, pixmap_patch.size()))
		self.patch_manager.add_patch(p, old_pixmap)
		painter = QPainter(self)
		painter.setCompositionMode(QPainter.CompositionMode_Source)
		painter.drawPixmap(p, pixmap_patch)
		return QRectF(p, QSizeF(pixmap_patch.size()))

	def undo(self, parent):
		patch_list = self.patch_manager.undo()
		if not patch_list:
			var.logger.info("Empty undo stack, ignore")
			return
		painter = QPainter(self)
		painter.setCompositionMode(QPainter.CompositionMode_Source)
		for p, patch in reversed(patch_list):
			painter.drawPixmap(p, patch)
			parent.update(QRectF(p, QSizeF(patch.size())))

	def finish(self):
		self.mb.reset_draw()
		self.patch_manager.finish_add_patch()

class CanvasItem(QGraphicsItem):
	def __init__(self, size):
		super().__init__()
		self.on_draw = False
		self.canvas = Canvas(size)

	def boundingRect(self):
		return QRectF(self.canvas.rect())

	def paint(self, painter, option, _widget):
		painter.drawPixmap(option.rect, self.canvas)

	def draw(self, pos, pressure):
		if not self.boundingRect().contains(pos):
			self.canvas.finish()
			return
		update_rect = self.canvas.draw(pos, pressure)
		if update_rect:
			var.logger.debug(f"Update rect: {update_rect}")
			self.update(update_rect)

	def undo(self):
		self.canvas.undo(self)

	def finish(self):
		self.canvas.finish()

	def set_operator(self, is_eraser):
		self.canvas.mb.erase_mode = is_eraser
