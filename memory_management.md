# mivv uses too much memory?

Currently this is the major limitation of mivv.
Typically mivv uses ~2GB memory for every 10k images,
because it loads all thumbnail files into memory asynchronously
to accelarate exploration.

A theoretically more correct solution is to
split the async loader into two threads:
a filename loader thread and an image loader thread,
by providing a thumbnail loading window range.
The length of window should be larger than
maximum number of images in a single screen in grid mode,
but smaller than RAM limitation.
While exploring mivv will slide the window to
dynamically drop and load images.

The design of async filename loader is important(at least for me).
In a slow network drive, without async filename traversal
I need to wait a long time before the first image is displayed.

However it is extremely difficult to make two threads work together,
and even I managed to implement it,
it will need hundreds of lines of code of dirty multithreading hacking,
making future maintenance painful.

TL;DR: Dynamic thumbnail loading will be implemented when I found a simple way to do it.
