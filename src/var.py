import os

cache_path = f"{os.environ['XDG_CACHE_HOME']}/mivv/"
valid_ext = {".png", ".PNG", ".jpg", ".JPG", ".jpeg", ".JPEG", ".bmp", ".BMP", ".gif", ".GIF"}
filelist = []
cached_state = []
pixmaps = [] # thumbnails
current_idx = 0
cache_size = 256
start_in_grid_mode = False
