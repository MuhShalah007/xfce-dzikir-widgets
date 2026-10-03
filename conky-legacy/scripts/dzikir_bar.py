#!/usr/bin/env python3
"""
Dzikir bar — thin overlay at top of screen with scrolling Arabic text.
Uses GTK3 + Pango for proper Arabic text shaping (ligatures).
Click-through via GTK input region.
"""

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('PangoCairo', '1.0')
gi.require_version('Gdk', '3.0')

from gi.repository import Gtk, Gdk, GLib, Pango, PangoCairo
import signal
import ctypes
import ctypes.util

# ── Dzikir text — Arabic with proper diacritics ──
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

# Repeat for seamless scroll
TEXT = DHIKR * 3

class DzikirBar(Gtk.Window):
    def __init__(self):
        super().__init__(Gtk.WindowType.TOPLEVEL)
        self.set_title("DzikirBar")
        self.set_decorated(False)
        self.set_app_paintable(True)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_keep_above(True)
        self.stick()

        # Screen geometry + ARGB visual for true transparency
        screen = Gdk.Screen.get_default()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.set_visual(visual)
        monitor = screen.get_monitor_geometry(0)
        self.screen_width = monitor.width
        self.bar_height = 46
        self.bar_y = 28  # below GNOME panel

        self.set_size_request(self.screen_width, self.bar_height)
        self.set_position(Gtk.WindowPosition.NONE)
        self.move(0, self.bar_y)

        # Scroll state
        self.scroll_offset = 0.0
        self.scroll_speed = 1.5  # pixels per frame
        self.frame_interval = 30  # ms (~33fps)

        # Pango layout for text
        self.layout = None
        self.text_width = 0

        # Connect draw
        self.connect("draw", self.on_draw)
        self.connect("realize", self.on_realize)

        # Input shape for click-through (set after realize)
        self.connect("size-allocate", self.on_size_allocate)

        # Start scroll timer
        GLib.timeout_add(self.frame_interval, self.scroll_tick)

    def set_clickthrough(self):
        """Set empty XFixes input shape so mouse clicks pass through to windows below."""
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
                return

            xid = self.get_window().get_xid()
            region = libxfixes.XFixesCreateRegion(display, None, 0)
            libxfixes.XFixesSetWindowShapeRegion(display, xid, 2, 0, 0, region)
            libxfixes.XFixesDestroyRegion(display, region)
            libx11.XFlush(display)
            libx11.XCloseDisplay(display)
        except Exception:
            pass  # Non-fatal — window still works, just not click-through

    def on_realize(self, widget):
        # Create Pango layout with Arabic font
        self.layout = self.create_pango_layout()
        self.layout.set_text(TEXT)
        font_desc = Pango.font_description_from_string("Noto Naskh Arabic 15")
        self.layout.set_font_description(font_desc)
        self.layout.set_auto_dir(False)  # Force LTR direction for scroll

        # Get text width
        ink_ext, log_ext = self.layout.get_extents()
        self.text_width = log_ext.width / Pango.SCALE

        # Built-in click-through: set empty input shape so clicks pass through.
        # Re-apply after 2s to handle WM race conditions on startup.
        self.set_clickthrough()
        GLib.timeout_add_seconds(2, self.set_clickthrough)

    def on_size_allocate(self, widget, allocation):
        # Re-apply click-through in case WM resets the shape on resize/move
        self.set_clickthrough()


    def scroll_tick(self):
        self.scroll_offset += self.scroll_speed
        if self.scroll_offset >= self.text_width:
            self.scroll_offset = 0.0
        self.queue_draw()
        return True

    def on_draw(self, widget, cr):
        # Background — semi-transparent dark
        cr.set_source_rgba(0.04, 0.04, 0.07, 0.45)  # semi-transparent dark
        cr.paint()

        # Clip to bar area
        cr.rectangle(0, 0, self.screen_width, self.bar_height)
        cr.clip()

        # Draw text — scrolls left → right (enters from left, exits right)
        # Two copies one text-width apart; wrap resets to same residue mod width.
        x = self.scroll_offset - self.text_width
        y = (self.bar_height - 15 * 2.0) / 2  # vertical center w/ room for harakat

        cr.set_source_rgb(0.98, 0.87, 0.69)  # soft gold #f9e2af

        # Draw text twice for seamless wrap
        PangoCairo.update_layout(cr, self.layout)
        cr.move_to(x, y)
        PangoCairo.show_layout(cr, self.layout)

        # Second copy for seamless scroll
        cr.move_to(x + self.text_width, y)
        PangoCairo.show_layout(cr, self.layout)

        return True


def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    win = DzikirBar()
    win.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
