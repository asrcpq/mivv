# mivv

PyQt5 simple image viewer.

(obsolete demo, too lazy to record a new one)

<img src="https://asrcpq.github.io/resources/2111/mivv_demo.gif" width="100%">

## features

* async image/thumbnail loading

* free rotation

* annotate image(wip)

* configurable(via `$XDG_CONFIG_HOME/mivv/config.py`)

## usage

1. have pyqt5 installed

2. `PYTHONPATH=. python3 mivv --help`

see `mivv/var.py` for keybind

## known limitations

* qtsvg only support svg tiny

* qtpdf does not have a pyqt version,
poppler-qt5 is broken(cannot install in venv)

* Loading all thumbnails use too much memory

	see `memory_management.md`

## todo(maybe)

* transparent image preview black flash with chessboard(because of jpg)

* video

* shift+create canvas=every 25% scaling

* flip change position

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
