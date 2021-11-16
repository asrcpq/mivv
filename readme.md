# mivv

PyQt5 simple image viewer.

![demo](https://asrcpq.github.io/resources/2111/mivv_demo.gif)

## Security note

Because mivv write data to cache, there is possiblity that
mivv still have unknown serious bugs that cause file corruption.
A good idea is to wrap this program with firejail, for example:

`firejail --noprofile --read-only=$HOME --read-write=$XDG_CACHE_HOME mivv`

Please consider reporting a bug if any violation is observed.

## features

* async image/thumbnail loading

* free rotation

* annotate image(wip)

## usage

1. have pyqt5 installed

2. `PYTHONPATH=. python3 mivv --help`

see control.md for keybind

## todo(maybe)

* toggle bar

* transparent background

* disable draw

* measure tool

* left up align

* more draw: clear, undo, colorpicker, fill...

* rotation + fill?

* file identifier(instead of by extension)?

* memory management
