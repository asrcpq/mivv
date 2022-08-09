# mivv

PySide6 simple image viewer.

<img src="https://asrcpq.github.io/resources/2111/mivv_demo.gif" width="100%">

## features

* async image/thumbnail loading

* free rotation

* annotate image(crappy)

* configurable(via `$XDG_CONFIG_HOME/mivv/config.py`)

## usage

1. have pyside6 installed

2. goto project root and type `PYTHONPATH=. python3 mivv --help`

I don't want to use python's buggy packaging tools.

see `mivv/var.py` for keybind

## known limitations

* no basic-svg, pdf support(lib limitation)

* Loading all thumbnails(~10k images level) use too much memory

	I have a better solution(dynamic thumbnail (un)loading),
	but it is too complicated for a simple image viewer.

* annotate feature is not working well/looking good

	I'm too lazy to implement better drawing.
	Currently I only use this tool for screen annotation by scripting
	(screenshot -> open image -> draw).

## todo(maybe)

* canvas default resolution same as screen

* modular design

* in-place mirror

* video module

* add test

* measure tool

* left up align

* draw

	* brush size

	* paintbrush

	* save, redo, colorpicker, select, transform

* strikes that cross the border are not continuous

* rotation + fill?

* memory management

	* more image cache(next prev)

	* prevent artificial huge image from being loaded

	* load thumbnails dynamically
