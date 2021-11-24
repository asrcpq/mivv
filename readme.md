# mivv

PyQt5 simple image viewer.

![demo](https://asrcpq.github.io/resources/2111/mivv_demo.gif)

## features

* async image/thumbnail loading

* free rotation

* annotate image(wip)

## usage

1. have pyqt5 installed

2. `PYTHONPATH=. python3 mivv --help`

see `mivv/var.py` for keybind

## known limitations

* pdf/complete svg support

	* qtsvg only support svg tiny

	* qtsvg poor performance

	* qtpdf does not have a pyqt version,
	poppler-qt5 is broken(cannot install in venv)

* Loading all thumbnails use too much memory

	see `memory_management.md`

## todo(maybe)

* allow autorepeat

* add test

* measure tool

* left up align

* more draw: paintbrush, save, redo, colorpicker, fill, select, transform...

* strikes that cross the border are not continuous

* rotation + fill?

* memory management

	* more image cache(next prev)

	* prevent artificial huge image from being loaded

	* load thumbnails dynamically
