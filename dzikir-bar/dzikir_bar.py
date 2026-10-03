#!/usr/bin/env python3
"""
Dzikir bar — thin overlay at top/bottom of screen with scrolling Arabic text.
Uses GTK3 + Pango for proper Arabic text shaping (ligatures).
Click-through via XFixes input region.
"""

import sys
import signal
import ctypes
import ctypes.util
import gi

gi.require_version('Gtk', '3.0')
gi.require_version('PangoCairo', '1.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk, GLib, Pango, PangoCairo

DHIKR = (
    "﷽  "
    "سُبْحَانَ اللَّهِ وَبِحَمْدِهِ، سُبْحَانَ اللَّهِ الْعَظِيمِ  ◆  "
    "الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ  ◆  "
    "اللَّهُ أَكْبَرُ  ◆  "
    "لَا إِلَهَ إِلَّا اللَّهُ وَحْدَهُ لَا شَرِيكَ لَهُ، لَهُ الْمُلْكُ وَلَهُ الْحَمْدُ وَهُوَ عَلَى كُلِّ شَيْءٍ قَدِيرٌ  ◆  "
    "اللَّهُمَّ صَلِّ وَسَلِّمْ عَلَى نَبِيِّنَا مُحَمَّدٍ وَعَلَى آلِهِ وَصَحْبِهِ أَجْمَعِينَ  ◆  "
    "رَبَّنَا ظَلَمْنَا أَنْفُسَنَا وَإِنْ لَمْ تَغْفِرْ لَنَا وَتَرْحَمْنَا لَنَكُونَنَّ مِنَ الْخَاسِرِينَ  ◆  "
    "أَسْتَغْفِرُ اللَّهَ الْعَظِيمَ الَّذِي لَا إِلَهَ إِلَّا هُوَ الْحَيَّ الْقَيُّومَ وَأَتُوبُ إِلَيْهِ  ◆  "
    "لَا إِلَهَ إِلَّا اللَّهُ  ◆  "
    "مُحَمَّدٌ رَسُولُ اللَّهِ  ◆  "
    "سُبْحَانَ اللَّهِ  ◆  "
    "الْحَمْدُ لِلَّهِ  ◆  "
    "اللَّهُ أَكْبَرُ  ◆  "
    "لَا حَوْلَ وَلَا قُوَّةَ إِلَّا بِاللَّهِ  ◆  "
    "اللَّهُمَّ إِنَّكَ عَفُوٌّ كَرِيمٌ تُحِبُّ الْعَفْوَ فَاعْفُ عَنِّي  ◆  "
    "رَبِّ اغْفِرْ لِي وَتُبْ عَلَيَّ إِنَّكَ أَنْتَ التَّوَّابُ الرَّحِيمُ  ◆  "
    "اللَّهُمَّ صَلِّ عَلَى مُحَمَّدٍ وَعَلَى آلِ مُحَمَّدٍ كَمَا صَلَّيْتَ عَلَى إِبْرَاهِيمَ وَعَلَى آلِ إِبْرَاهِيمَ إِنَّكَ حَمِيدٌ مَجِيدٌ  ◆  "
    "اللَّهُمَّ بَارِكْ عَلَى مُحَمَّدٍ وَعَلَى آلِ مُحَمَّدٍ كَمَا بَارَكْتَ عَلَى إِبْرَاهِيمَ وَعَلَى آلِ إِبْرَاهِيمَ إِنَّكَ حَمِيدٌ مَجِيدٌ  ◆  "
)

TEXT = DHIKR * 3

class DzikirBar(Gtk.Window):
    def __init__(self, y_offset=0, bar_height=36, speed=1.5):
        super().__init__(Gtk.WindowType.TOPLEVEL)
        self.set_title("DzikirBar")
        self.set_decorated(False)
        self.set_app_paintable(True)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_keep_above(True)
        self.stick()

        screen = Gdk.Screen.get_default()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.set_visual(visual)

        display = screen.get_display()
        monitor = display.get_primary_monitor() or display.get_monitor(0)
        geom = monitor.get_geometry()
        
        self.screen_width = geom.width
        self.bar_height = bar_height
        self.bar_y = y_offset

        self.set_size_request(self.screen_width, self.bar_height)
        self.set_position(Gtk.WindowPosition.NONE)
        self.move(geom.x, geom.y + self.bar_y)

        self.scroll_offset = 0.0
        self.scroll_speed = speed
        self.frame_interval = 30

        self.layout = None
        self.text_width = 0

        self.connect("draw", self.on_draw)
        self.connect("realize", self.on_realize)
        self.connect("size-allocate", self.on_size_allocate)

        GLib.timeout_add(self.frame_interval, self.scroll_tick)

    def set_clickthrough(self):
        try:
            libx11 = ctypes.cdll.LoadLibrary(ctypes.util.find_library('X11'))
            libxfixes = ctypes.cdll.LoadLibrary(ctypes.util.find_library('Xfixes'))

            libx11.XOpenDisplay.restype = ctypes.c_void_p
            libx11.XOpenDisplay.argtypes = [ctypes.c_char_p]
            libx11.XFlush.argtypes = [ctypes.c_void_p]
            libx11.XCloseDisplay.argtypes = [ctypes.c_void_p]

            libxfixes.XFixesCreateRegion.restype = ctypes.c_ulong
            libxfixes.XFixesCreateRegion.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int]
            libxfixes.XFixesSetWindowShapeRegion.argtypes = [
                ctypes.c_void_p,
                ctypes.c_ulong,
                ctypes.c_int,
                ctypes.c_int,
                ctypes.c_int,
                ctypes.c_ulong,
            ]
            libxfixes.XFixesDestroyRegion.argtypes = [ctypes.c_void_p, ctypes.c_ulong]

            display = libx11.XOpenDisplay(None)
            if not display:
                return

            xid = self.get_window().get_xid()
            region = libxfixes.XFixesCreateRegion(display, None, 0)
            libxfixes.XFixesSetWindowShapeRegion(display, xid, 2, 0, 0, region)
            libxfixes.XFixesDestroyRegion(display, region)
            libx11.XFlush(display)
            libx11.XCloseDisplay(display)
        except Exception:
            pass

    def on_realize(self, widget):
        self.layout = self.create_pango_layout()
        self.layout.set_text(TEXT)
        font_desc = Pango.font_description_from_string("Noto Naskh Arabic 15")
        self.layout.set_font_description(font_desc)
        self.layout.set_auto_dir(False)

        ink_ext, log_ext = self.layout.get_extents()
        self.text_width = log_ext.width / Pango.SCALE

        self.set_clickthrough()
        GLib.timeout_add_seconds(2, self.set_clickthrough)

    def on_size_allocate(self, widget, allocation):
        self.set_clickthrough()

    def scroll_tick(self):
        self.scroll_offset += self.scroll_speed
        if self.scroll_offset >= self.text_width:
            self.scroll_offset = 0.0
        self.queue_draw()
        return True

    def on_draw(self, widget, cr):
        cr.set_source_rgba(0.04, 0.04, 0.07, 0.55)
        cr.paint()

        cr.rectangle(0, 0, self.screen_width, self.bar_height)
        cr.clip()

        x = self.scroll_offset - self.text_width
        y = (self.bar_height - 15 * 2.0) / 2

        cr.set_source_rgb(0.98, 0.87, 0.69)

        PangoCairo.update_layout(cr, self.layout)
        cr.move_to(x, y)
        PangoCairo.show_layout(cr, self.layout)

        cr.move_to(x + self.text_width, y)
        PangoCairo.show_layout(cr, self.layout)

        return True

def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    y_offset = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    height = int(sys.argv[2]) if len(sys.argv) > 2 else 36
    speed = float(sys.argv[3]) if len(sys.argv) > 3 else 1.5
    
    win = DzikirBar(y_offset=y_offset, bar_height=height, speed=speed)
    win.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
