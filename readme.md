# mivv

PyQt5 simple image viewer.

## control

Mouse(image mode):

* drag middle: pan

* shift + drag middle: rotation

* ctrl + drag middle: zoom

* drag right left/right: next/prev image

* drag up: grid mode

Mouse(grid mode):

* drag middle: move cursor

* ctrl + drag middle: change thumbtail size

* left click: select cursor, if selected enter image mode

Keyboard:

* enter: toggle image/grid mode

* n/N for next/prev image

* hjkl move

* 1 for 100% zoom

* i/o for zoom in/out

* \</\> for rotation

* r for reload

* bar/underscore for flipping

* q/escape for quit

## usage

1. have `XDG_CONFIG_HOME` and `XDG_CACHE_HOME` set

2. have pyqt5 installed

3. `python3 src/mivv.py`

## notes

Low quality gif scaling(efficiency)

## todo

* image async load thumbnail first

## maybe

* grid mode async caching

* image mode async caching

* mem limit
