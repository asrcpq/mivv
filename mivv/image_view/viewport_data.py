from PyQt5.QtGui import QTransform

from mivv import var

class _ViewportData():
	def __init__(self):
		self.scaling_factor = None
		self.zoom_level = None
		self.flip = [1.0, 1.0]
		self.content_center = None
		self.original_scaling_factor = None
		self.original_scaling_limit = None
		self.rotation: float = 0

	def scale_view(self, offset, abs_k = False):
		if abs_k:
			self.scaling_factor = offset
		else:
			self.scaling_factor *= offset
		if self.scaling_factor < self.original_scaling_limit[0]:
			self.scaling_factor = self.original_scaling_limit[0]
		if self.scaling_factor > self.original_scaling_limit[1]:
			self.scaling_factor = self.original_scaling_limit[1]
		self.zoom_level = self.original_scaling_factor / self.scaling_factor

	def set_original_scaling_factor(self, wk, hk):
		# w bound
		if hk >= wk:
			osf = wk * var.hidpi
		elif wk > hk:
			osf = hk * var.hidpi
		else:
			raise Exception("wk or nk is not valid number")
		self.original_scaling_factor = osf
		self.original_scaling_limit = [
			osf / var.zoom_level_limit[1],
			osf / var.zoom_level_limit[0],
		]

	def get_move_dist(self):
		return var.k_move * var.hidpi * self.scaling_factor / self.original_scaling_factor

	# whether invert rotation angle
	def rotate_multiplier(self):
		return self.flip[0] * self.flip[1]

	def set_flip(self, axis: int):
		self.flip[axis] = -self.flip[axis]

	def get_transform(self, k):
		qtrans = QTransform()
		qtrans.scale(k * self.flip[0], k * self.flip[1])
		qtrans.rotate(self.rotation)
		qtrans.translate(self.content_center[0], self.content_center[1])
		return qtrans

	def get_mouse_transform(self):
		qtrans = QTransform()
		qtrans.rotate(-self.rotation)
		qtrans.scale(self.flip[0], self.flip[1])
		return qtrans

	def new_image_initialize(self):
		self.flip = [1.0, 1.0]
		self.rotation = 0

	def set_rotation(self, degree):
		self.rotation = degree

	def rotate(self, degree):
		self.rotation += degree

	def move(self, dx, dy):
		self.content_center[0] += dx
		self.content_center[1] += dy
