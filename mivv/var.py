import os

from logger import get_logger

# config values
ext_type = {
	".png": 1,
	".PNG": 1,
	".jpg": 1,
	".JPG": 1,
	".jpeg": 1,
	".JPEG": 1,
	".bmp": 1,
	".BMP": 1,
	".gif": 2,
	".GIF": 2,
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

# global values
logger = get_logger()
hidpi = None
image_loader = None
main_window = None
app = None
private_mode = False
start_in_grid_mode = False
current_idx = 0
keymod_shift = False
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
	logger.warn("XDG_CACHE_HOME not set. Will not read/write cache.")
	cache_path = None
