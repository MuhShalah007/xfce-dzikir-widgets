#!/usr/bin/env python3
"""Set empty input shape on conky window for click-through effect."""

import ctypes
import ctypes.util
import sys

def set_clickthrough(window_id):
    # Load libraries
    libx11 = ctypes.cdll.LoadLibrary(ctypes.util.find_library('X11'))
    libxfixes = ctypes.cdll.LoadLibrary(ctypes.util.find_library('Xfixes'))

    # Set return/arg types
    libx11.XOpenDisplay.restype = ctypes.c_void_p
    libx11.XOpenDisplay.argtypes = [ctypes.c_char_p]
    libx11.XFlush.argtypes = [ctypes.c_void_p]
    libx11.XCloseDisplay.argtypes = [ctypes.c_void_p]

    libxfixes.XFixesCreateRegion.restype = ctypes.c_ulong
    libxfixes.XFixesCreateRegion.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int]
    libxfixes.XFixesSetWindowShapeRegion.argtypes = [
        ctypes.c_void_p,  # display
        ctypes.c_ulong,   # window
        ctypes.c_int,     # shape_kind (2 = ShapeInput)
        ctypes.c_int,     # x_off
        ctypes.c_int,     # y_off
        ctypes.c_ulong,   # region
    ]
    libxfixes.XFixesDestroyRegion.argtypes = [ctypes.c_void_p, ctypes.c_ulong]

    display = libx11.XOpenDisplay(None)
    if not display:
        print("Cannot open display")
        sys.exit(1)

    # Create empty region (no rectangles)
    region = libxfixes.XFixesCreateRegion(display, None, 0)

    # ShapeInput = 2
    libxfixes.XFixesSetWindowShapeRegion(display, window_id, 2, 0, 0, region)

    libxfixes.XFixesDestroyRegion(display, region)
    libx11.XFlush(display)
    libx11.XCloseDisplay(display)
    print(f"Click-through enabled for window {hex(window_id)}")

if __name__ == "__main__":
    wid = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    if not wid:
        print("Usage: clickthrough.py <window_id>")
        sys.exit(1)
    set_clickthrough(wid)
