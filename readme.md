# mivv

PyQt5 simple image viewer.

## default control

Mouse control like gimp, keyboard:

* enter: toggle image/grid mode

* n/N for next/prev image

* hjkl move

* 0 for 100% zoom

* i/o for zoom in/out

* \</\> for rotation

* r for reload

* bar/underscore for flipping

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
