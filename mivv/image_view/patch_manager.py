from collections import deque

from mivv import var

class PatchManager():
	def __init__(self):
		# patch is old images so older patch should cover newer one
		self.tmp_patches = []
		self.undo_stack = deque()
		self.max_undo = 100

	def add_patch(self, pos, pixmap):
		self.tmp_patches.append((pos, pixmap))

	def finish_add_patch(self):
		if len(self.undo_stack) >= self.max_undo:
			self.undo_stack.popleft()
		self.undo_stack.append(self.tmp_patches)
		var.logger.debug(f"Current undo queue length: {len(self.undo_stack)}")
		self.tmp_patches = []

	def undo(self):
		if self.undo_stack:
			return self.undo_stack.pop()
		return None
