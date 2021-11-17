from enum import Enum

Keydef = Enum('Keydef', [
	# main
	'quit',
	'toggle_grid_mode',
	'lock_size',
	'preload_thumbnail',
	# common
	'view_left',
	'view_right',
	'view_up',
	'view_down',
	'view_zoom_in',
	'view_zoom_out',
	'view_zoom_origin',
	'view_next',
	'view_prev',
	'view_first',
	'view_last',
	# image_mode
	'image_view_zoom_fill',
	'image_view_cw',
	'image_view_ccw',
	'image_view_mirror_v',
	'image_view_mirror_h',
	'image_navi_reload',
	'image_movie_pause_toggle',
	'image_movie_frame_forward',
	'image_canvas_eraser',
	'image_canvas_pen',
	'image_canvas_clear',
	# grid_mode
	'grid_hol',
	'grid_eol',
	'grid_page_up',
	'grid_page_up_half',
	'grid_page_down',
	'grid_page_down_half',
])
