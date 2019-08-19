pyROT
-----

This is the trivial child of [brython](https://brython.info/), a python implementation in javascript, and [rot.js](https://ondras.github.io/rot.js), a roguelike library.

The rot API is unchanged and some constructs might not be very pythonic.

A demo can be tried [here](https://benob.github.io/pyROT/).

The interaction between python and javascript is rather fragile. While it is relatively safe to call js from python, the converse requires wrappers. See wrappers in `index.html` for examples.

![](https://github.com/benob/pyROT/blob/master/screenshot.png)
