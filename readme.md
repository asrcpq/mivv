# mivv

PyQt5 simple image viewer.

![demo](https://asrcpq.github.io/resources/2111/mivv_demo.gif)

## control

Tablet(image mode):

* draw

Mouse/Tablet(image mode):

* drag middle button: pan

* shift + drag middle button: rotation

* ctrl + drag middle button: zoom

* drag right button move left/right: next/prev image

* drag right button move up: enter grid mode

Mouse/Tablet(grid mode):

* drag middle: move cursor

* ctrl + drag middle: change thumbtail size

* left click: select cursor, enter image mode if already selected

Keyboard:

* enter or tab: toggle image/grid mode

* n/N: next/prev image

* hjkl or arrow, ctrl-bfud, 0$^: move

* 1/w: 1:1 view/fill view

* i/o: zoom in/out

* \</\>: rotation

* r: reload

* bar/underscore: flipping

* q/escape: quit

* space: gif pause/resume

* s: gif frame forward

## usage

1. have pyqt5 installed

2. `python3 mivv --help`

3. config file locates at `$XDG_CONFIG_HOME/mivv/config.py`,
check `mivv/var.py` for values to override.

## todo(maybe)

* toggle bar

* transparent background

* disable draw

* more draw: clear, undo, colorpicker, fill...

* decide support fixed view size resize or not(need a fill mode with proportional resize)

* async load + memory management
