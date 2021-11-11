import os, sys
from image_loader import ImageLoader
import logging

logger = logging.getLogger()
logger.setLevel(logging.WARN)
log_format = '%(levelname)s: %(message)s'
formatter = logging.Formatter(log_format)
handler = logging.StreamHandler(sys.stderr)
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)
logger.addHandler(handler)

cache_path = f"{os.environ['XDG_CACHE_HOME']}/mivv/"
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
zoom_level_limit = [0.1, 20.0] # note that scaling factor = 1 / zoom level
image_move_zoom = 5 # image mode pixels moved to trigger zoom
image_move_rotate = 5 # ... rotation(degree)
grid_move_zoom = 50 # grid mode pixels moved to trigger zoom
grid_move_pan = 50 # grid mode pixels moved to trigger navigation
guesture_move = 30
bar_height = 10

# values change at runtime
hidpi = None
load_all = True # argv
expand_dir = True # argv
start_in_grid_mode = False
current_idx = 0
image_loader = ImageLoader()
keymod_shift = False
keymod_control = False

config_path = f"{os.environ['XDG_CONFIG_HOME']}/mivv/config.py"
if os.path.isfile(config_path):
	# pylint: disable=W0122
	exec(compile(open(config_path, "rb").read(), config_path, 'exec'))
