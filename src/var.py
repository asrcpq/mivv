import os
from image_loader import ImageLoader

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
current_idx = 0
cache_size = 256
grid_sizes = [32, 64, 128, 192, 256] # preview sizes
grid_size_idx_default = 2
start_in_grid_mode = False
load_all = True
image_loader = ImageLoader()
expand_dir = True
k_move = 100 # relative to screen size
mouse_factor = -5 # image mode panning accelarator
scaling_mult = 1.3 # image mode keyboard scaling factor
scaling_mult_mouse = 1.05 # image mode mouse scaling factor
image_move_zoom = 5 # image mode pixels moved to trigger zoom
grid_move_zoom = 50 # grid mode pixels moved to trigger zoom
grid_move_pan = 50 # grid mode pixels moved to trigger navigation

config_path = f"{os.environ['XDG_CONFIG_HOME']}/mivv/config.py"
if os.path.isfile(config_path):
	exec(compile(open(config_path, "rb").read(), config_path, 'exec'))
