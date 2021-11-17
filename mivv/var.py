import os

from PyQt5.QtCore import Qt

from mivv.logger import get_logger
from mivv.keydef import Keydef

# config values
ext_type = {
	".png": 1,
	".jpg": 1,
	".jpeg": 1,
	".bmp": 1,
	".gif": 2,
	".svg": 3,
}
cache_size = 256
grid_sizes = [32, 64, 128, 192, 256] # preview sizes
grid_size_idx_default = 2
k_move = 50 # relative to screen size
scaling_mult = 1.3 # image mode keyboard scaling factor
scaling_mult_mouse = 1.04 # image mode mouse scaling factor
zoom_level_limit = [0.01, 20.0] # note that scaling factor = 1 / zoom level
image_move_zoom = 5 # image mode pixels moved to trigger zoom
image_move_rotate = 5 # ... rotation(degree)
grid_move_zoom = 50 # grid mode pixels moved to trigger zoom
grid_move_pan = 50 # grid mode pixels moved to trigger navigation
guesture_move = 30
bar_height = 10
background = "rgb(0, 0, 0)"
border_color = "rgb(255, 255, 255)"
chessboard_background = False # startup value only

# modifier bit: shift 1, control 2
keymap_common = {
	(Qt.Key_Q, 0): Keydef.quit,
	(Qt.Key_Return, 0): Keydef.toggle_grid_mode,
	(Qt.Key_W, 1): Keydef.lock_size,
	(Qt.Key_T, 1): Keydef.preload_thumbnail,
	(Qt.Key_H, 0): Keydef.view_left,
	(Qt.Key_L, 0): Keydef.view_right,
	(Qt.Key_K, 0): Keydef.view_up,
	(Qt.Key_J, 0): Keydef.view_down,
	(Qt.Key_I, 0): Keydef.view_zoom_in,
	(Qt.Key_O, 0): Keydef.view_zoom_out,
	(Qt.Key_1, 0): Keydef.view_zoom_origin,
	(Qt.Key_N, 0): Keydef.view_next,
	(Qt.Key_P, 0): Keydef.view_prev,
	(Qt.Key_G, 0): Keydef.view_first,
	(Qt.Key_G, 1): Keydef.view_last,
}

keymap_image = {
	(Qt.Key_PageDown, 0): Keydef.view_next,
	(Qt.Key_PageUp, 0): Keydef.view_prev,
	(Qt.Key_W, 0): Keydef.image_view_zoom_fill,
	(Qt.Key_Greater, 1): Keydef.image_view_cw,
	(Qt.Key_Less, 1): Keydef.image_view_ccw,
	(Qt.Key_Bar, 0): Keydef.image_view_mirror_v,
	(Qt.Key_Underscore, 1): Keydef.image_view_mirror_h,
	(Qt.Key_R, 0): Keydef.image_navi_reload,
	(Qt.Key_Space, 0): Keydef.image_movie_pause_toggle,
	(Qt.Key_S, 0): Keydef.image_movie_frame_forward,
	(Qt.Key_E, 1): Keydef.image_canvas_eraser,
	(Qt.Key_A, 0): Keydef.image_canvas_pen,
	(Qt.Key_C, 0): Keydef.image_canvas_clear,
	(Qt.Key_B, 1): Keydef.image_chessboard,
}

keymap_grid = {
	(Qt.Key_0, 0): Keydef.grid_hol,
	(Qt.Key_Dollar, 1): Keydef.grid_eol,
	(Qt.Key_F, 2): Keydef.grid_page_down,
	(Qt.Key_B, 2): Keydef.grid_page_up,
	(Qt.Key_PageDown, 0): Keydef.grid_page_down,
	(Qt.Key_PageUp, 0): Keydef.grid_page_up,
	(Qt.Key_D, 2): Keydef.grid_page_down_half,
	(Qt.Key_U, 2): Keydef.grid_page_up_half,
}

# configurable but will also change at runtime
loglevel = "warn"
lock_size = False # on resize
preload_thumbnail = True

# global values
logger = get_logger()
hidpi = None
image_loader = None
main_window = None
app = None
private_mode = False
start_in_grid_mode = False
current_idx = 0
keymod_bit = False
keymod_control = False

if "XDG_CONFIG_HOME" in os.environ:
	config_path = f"{os.environ['XDG_CONFIG_HOME']}/mivv/config.py"
	if os.path.isfile(config_path):
		# pylint: disable=W0122
		exec(compile(open(config_path, "rb").read(), config_path, 'exec'))

# logger is used here, so after include user conf
if "XDG_CACHE_HOME" in os.environ:
	cache_path = f"{os.environ['XDG_CACHE_HOME']}/mivv/"
else:
	logger.warning("XDG_CACHE_HOME not set. Will not read/write cache.")
	cache_path = None
