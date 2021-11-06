import os
from image_loader import ImageLoader

cache_path = f"{os.environ['XDG_CACHE_HOME']}/mivv/"
valid_ext = {".png", ".PNG", ".jpg", ".JPG", ".jpeg", ".JPEG", ".bmp", ".BMP", ".gif", ".GIF"}
current_idx = 0
cache_size = 256
start_in_grid_mode = False
load_all = True
image_loader = ImageLoader()
expand_dir = True
delta_move = 50