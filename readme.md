# mivv

PyQt5 simple image viewer.

![demo](https://asrcpq.github.io/resources/2111/mivv_demo.gif)

## control

Mouse(image mode):

* drag middle button: pan

* shift + drag middle button: rotation

* ctrl + drag middle button: zoom

* drag right button move left/right: next/prev image

* drag right button move up: enter grid mode

Mouse(grid mode):

* drag middle: move cursor

* ctrl + drag middle: change thumbtail size

* left click: select cursor, enter image mode if already selected

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

3. `python3 mivv xxx.png` or `hpm/entrypoint xxx.png`

## notes

Low quality gif scaling(efficiency)

## bugs

* chance of grid mode cursor index overflow(hard to reproduce)

## todo

* make move speed in grid mode proportional to reciprocal of zoom level

* async load + memory management
