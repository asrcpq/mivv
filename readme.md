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

* pdf/complete svg support(QT no support)

* Thumbnail use too much memory

	see `memory_manage.md`

## todo(maybe)

* toggle bar

* transparent background

* disable draw

* measure tool

* left up align

* more draw: clear, undo, colorpicker, fill...

* rotation + fill?

* memory management

	* more image cache(next prev)

	* prevent huge image from being loaded

	* load thumbnails dynamically
