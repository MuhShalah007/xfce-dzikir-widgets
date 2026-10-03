#!/usr/bin/env python3
"""
Dzikir Popup Notification — Telegram-style toast at bottom-right of screen.
Cycles through dzikir phrases periodically with smooth slide-in animation.
"""

import sys
import math
import signal
import gi

gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk, GLib, Pango

# ── Dzikir Database ──
DHIKR_ITEMS = [
    {
        "arabic": "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ",
        "latin": "Bismillahir-rahmanir-rahim",
        "meaning": "Dengan nama Allah Yang Maha Pengasih lagi Maha Penyayang."
    },
    {
        "arabic": "سُبْحَانَ اللَّهِ وَبِحَمْدِهِ ، سُبْحَانَ اللَّهِ الْعَظِيمِ",
        "latin": "Subhanallahi wa bihamdihi, Subhanallahil 'Azhim",
        "meaning": "Maha Suci Allah dengan segala puji-Nya, Maha Suci Allah Yang Maha Agung."
    },
    {
        "arabic": "الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ",
        "latin": "Alhamdulillahi Rabbil 'Alamin",
        "meaning": "Segala puji bagi Allah, Tuhan seluruh alam."
    },
    {
        "arabic": "لَا إِلٰهَ إِلَّا اللَّهُ وَحْدَهُ لَا شَرِيكَ لَهُ، لَهُ الْمُلْكُ وَلَهُ الْحَمْدُ وَهُوَ عَلَىٰ كُلِّ شَيْءٍ قَدِيرٌ",
        "latin": "La ilaha illallahu wahdahu la syarika lah...",
        "meaning": "Tiada tuhan selain Allah Yang Maha Esa, tiada sekutu bagi-Nya..."
    },
    {
        "arabic": "اللَّهُمَّ صَلِّ وَسَلِّمْ عَلَىٰ نَبِيِّنَا مُحَمَّدٍ وَعَلَىٰ آلِهِ وَصَحْبِهِ أَجْمَعِينَ",
        "latin": "Allahumma shalli wa sallim 'ala nabiyyina Muhammad...",
        "meaning": "Ya Allah, limpahkan shalawat dan salam kepada Nabi kami Muhammad."
    },
    {
        "arabic": "رَبَّنَا ظَلَمْنَا أَنْفُسَنَا وَإِنْ لَمْ تَغْفِرْ لَنَا وَتَرْحَمْنَا لَنَكُونَنَّ مِنَ الْخَاسِرِينَ",
        "latin": "Rabbana zhalamna anfusana...",
        "meaning": "Ya Tuhan kami, kami telah menzalimi diri kami sendiri..."
    },
    {
        "arabic": "أَسْتَغْفِرُ اللَّهَ الْعَظِيمَ الَّذِي لَا إِلٰهَ إِلَّا هُوَ الْحَيَّ الْقَيُّومَ وَأَتُوبُ إِلَيْهِ",
        "latin": "Astaghfirullahal 'Azhim...",
        "meaning": "Aku memohon ampun kepada Allah Yang Maha Agung..."
    },
    {
        "arabic": "لَا حَوْلَ وَلَا قُوَّةَ إِلَّا بِاللَّهِ الْعَلِيِّ الْعَظِيمِ",
        "latin": "La hawla wa la quwwata illa billahil 'Aliyyil 'Azhim",
        "meaning": "Tiada daya dan kekuatan kecuali dengan pertolongan Allah Yang Maha Tinggi."
    },
    {
        "arabic": "اللَّهُمَّ إِنَّكَ عَفُوٌّ كَرِيمٌ تُحِبُّ الْعَفْوَ فَاعْفُ عَنِّي",
        "latin": "Allahumma innaka 'afuwwun karim tuhibbul 'afwa fa'fu 'anni",
        "meaning": "Ya Allah, Engkau Maha Pemaaf dan Maha Mulia, maka maafkanlah aku."
    },
    {
        "arabic": "رَبِّ اغْفِرْ لِي وَتُبْ عَلَيَّ إِنَّكَ أَنْتَ التَّوَّابُ الرَّحِيمُ",
        "latin": "Rabbighfirli wa tub 'alayya innaka antat-Tawwabur-Rahim",
        "meaning": "Ya Tuhanku ampunilah aku dan terimalah tobatku..."
    },
    {
        "arabic": "سُبْحَانَ اللَّهِ ، وَالْحَمْدُ لِلَّهِ ، وَلَا إِلٰهَ إِلَّا اللَّهُ ، وَاللَّهُ أَكْبَرُ",
        "latin": "Subhanallah, Walhamdulillah, Wa la ilaha illallah, Wallahu Akbar",
        "meaning": "Maha Suci Allah, Segala Puji bagi Allah, Tiada Tuhan selain Allah, Allah Maha Besar."
    },
    {
        "arabic": "يَا حَيُّ يَا قَيُّومُ بِرَحْمَتِكَ أَسْتَغِيثُ",
        "latin": "Ya Hayyu Ya Qayyum bi rahmatika astaghits",
        "meaning": "Wahai Rabb Yang Maha Hidup, Yang Maha Berdiri Sendiri, dengan rahmat-Mu aku memohon pertolongan."
    },
    {
        "arabic": "حَسْبُنَا اللَّهُ وَنِعْمَ الْوَكِيلُ نِعْمَ الْمَوْلَىٰ وَنِعْمَ النَّصِيرُ",
        "latin": "Hasbunallahu wa ni'mal wakil, ni'mal mawla wa ni'man nashir",
        "meaning": "Cukuplah Allah menjadi penolong kami dan Allah adalah sebaik-baik pelindung."
    }
]

CSS = b"""
#toast-window {
    background-color: transparent;
}

#toast-card {
    background-color: rgba(26, 35, 48, 0.94);
    border: 1px solid rgba(75, 150, 240, 0.35);
    border-radius: 14px;
    padding: 12px 16px 14px 16px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.55);
}

#toast-card:hover {
    border-color: rgba(75, 150, 240, 0.6);
    background-color: rgba(30, 41, 56, 0.97);
}

#header-box {
    margin-bottom: 6px;
}

#app-title {
    font-family: 'Inter', 'Segoe UI', sans-serif;
    font-size: 11.5px;
    font-weight: bold;
    color: #4daafc;
}

#counter-badge {
    font-family: 'Inter', monospace;
    font-size: 10px;
    color: #64748b;
    background-color: rgba(255, 255, 255, 0.07);
    border-radius: 8px;
    padding: 1px 6px;
    margin-left: 6px;
}

#close-btn {
    min-height: 18px;
    min-width: 18px;
    padding: 0;
    margin: 0;
    border: none;
    background: transparent;
    color: #64748b;
    font-size: 12px;
    font-weight: bold;
}

#close-btn:hover {
    color: #ef4444;
    background: transparent;
}

#arabic-label {
    font-family: 'Noto Naskh Arabic', 'Amiri', 'Scheherazade New', serif;
    font-size: 17px;
    font-weight: 600;
    color: #f8fafc;
    margin-top: 2px;
    margin-bottom: 4px;
}

#latin-label {
    font-family: 'Inter', 'Segoe UI', sans-serif;
    font-size: 10px;
    font-style: italic;
    color: #38bdf8;
    margin-bottom: 2px;
}

#meaning-label {
    font-family: 'Inter', 'Segoe UI', sans-serif;
    font-size: 10.5px;
    color: #94a3b8;
}

#progress-bar {
    min-height: 3px;
    border-radius: 2px;
    margin-top: 8px;
}

#progress-bar trough {
    background-color: rgba(255, 255, 255, 0.08);
    border-radius: 2px;
    min-height: 3px;
    border: none;
}

#progress-bar progress {
    background-color: #38bdf8;
    border-radius: 2px;
    min-height: 3px;
    border: none;
}
"""

class DzikirToast(Gtk.Window):
    def __init__(self, display_time=9.0, cooldown_time=7.0):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self.set_title("DzikirNotification")
        self.set_name("toast-window")
        self.set_decorated(False)
        self.set_app_paintable(True)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_keep_above(True)
        self.set_type_hint(Gdk.WindowTypeHint.NOTIFICATION)
        
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.set_visual(visual)

        self.display_time = display_time
        self.cooldown_time = cooldown_time
        self.current_index = 0
        self.is_hovered = False
        self.is_animating = False
        self.target_y = 0
        self.hidden_y = 0
        self.fixed_x = 0
        self.toast_width = 380
        self.anim_progress = 0.0
        self.anim_direction = 0  # 1 = in, -1 = out
        
        self.build_ui()
        self.apply_css()
        
        self.connect("enter-notify-event", self.on_mouse_enter)
        self.connect("leave-notify-event", self.on_mouse_leave)
        self.connect("button-press-event", self.on_click)

        GLib.idle_add(self.start_cycle)

    def apply_css(self):
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(CSS)
        Gtk.StyleContext.add_provider_for_screen(
            self.get_screen(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def build_ui(self):
        self.card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.card.set_name("toast-card")
        self.card.set_size_request(self.toast_width, -1)
        self.add(self.card)

        # Header Box
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        header.set_name("header-box")
        
        icon_label = Gtk.Label(label="🕊️")
        header.pack_start(icon_label, False, False, 0)
        
        title_label = Gtk.Label(label="Dzikir & Pengingat")
        title_label.set_name("app-title")
        header.pack_start(title_label, False, False, 0)
        
        self.counter_label = Gtk.Label(label="1/13")
        self.counter_label.set_name("counter-badge")
        header.pack_start(self.counter_label, False, False, 0)
        
        close_btn = Gtk.Button(label="✕")
        close_btn.set_name("close-btn")
        close_btn.connect("clicked", self.on_close_clicked)
        header.pack_end(close_btn, False, False, 0)
        
        self.card.pack_start(header, False, False, 0)

        # Arabic text
        self.arabic_label = Gtk.Label()
        self.arabic_label.set_name("arabic-label")
        self.arabic_label.set_line_wrap(True)
        self.arabic_label.set_line_wrap_mode(Pango.WrapMode.WORD)
        self.arabic_label.set_justify(Gtk.Justification.CENTER)
        self.arabic_label.set_direction(Gtk.TextDirection.RTL)
        self.card.pack_start(self.arabic_label, False, False, 0)

        # Latin text
        self.latin_label = Gtk.Label()
        self.latin_label.set_name("latin-label")
        self.latin_label.set_line_wrap(True)
        self.latin_label.set_line_wrap_mode(Pango.WrapMode.WORD)
        self.latin_label.set_justify(Gtk.Justification.CENTER)
        self.card.pack_start(self.latin_label, False, False, 0)

        # Meaning text
        self.meaning_label = Gtk.Label()
        self.meaning_label.set_name("meaning-label")
        self.meaning_label.set_line_wrap(True)
        self.meaning_label.set_line_wrap_mode(Pango.WrapMode.WORD)
        self.meaning_label.set_justify(Gtk.Justification.CENTER)
        self.card.pack_start(self.meaning_label, False, False, 0)

        # Progress bar
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_name("progress-bar")
        self.progress_bar.set_fraction(1.0)
        self.card.pack_start(self.progress_bar, False, False, 0)

    def load_item(self, index):
        total = len(DHIKR_ITEMS)
        item = DHIKR_ITEMS[index % total]
        self.counter_label.set_text(f"{index % total + 1}/{total}")
        self.arabic_label.set_text(item["arabic"])
        self.latin_label.set_text(item["latin"])
        self.meaning_label.set_text(item["meaning"])
        self.progress_bar.set_fraction(1.0)

    def update_geometry(self):
        screen = self.get_screen()
        display = screen.get_display()
        monitor = display.get_primary_monitor() or display.get_monitor(0)
        geometry = monitor.get_geometry()
        
        panel_offset = 52
        margin_right = 20
        self.fixed_x = geometry.x + geometry.width - self.toast_width - margin_right
        
        self.show_all()
        _, nat_h = self.get_preferred_height()
        self.target_y = geometry.y + geometry.height - nat_h - panel_offset
        self.hidden_y = geometry.y + geometry.height + 20

    def start_cycle(self):
        self.load_item(self.current_index)
        self.update_geometry()
        self.animate_in()
        return False

    def animate_in(self):
        self.is_animating = True
        self.anim_direction = 1
        self.anim_progress = 0.0
        self.update_geometry()
        self.move(self.fixed_x, self.hidden_y)
        self.show_all()
        GLib.timeout_add(16, self.step_animation)

    def animate_out(self, on_finish=None):
        self.is_animating = True
        self.anim_direction = -1
        self.anim_progress = 1.0
        self.on_finish_anim = on_finish
        GLib.timeout_add(16, self.step_animation)

    def step_animation(self):
        step = 0.08
        if self.anim_direction == 1:
            self.anim_progress += step
            if self.anim_progress >= 1.0:
                self.anim_progress = 1.0
                self.is_animating = False
                y = int(self.target_y)
                self.move(self.fixed_x, y)
                self.start_timer()
                return False
        else:
            self.anim_progress -= step
            if self.anim_progress <= 0.0:
                self.anim_progress = 0.0
                self.is_animating = False
                self.hide()
                if hasattr(self, 'on_finish_anim') and self.on_finish_anim:
                    self.on_finish_anim()
                return False

        t = self.anim_progress
        ease = 1 - math.pow(1 - t, 3)
        curr_y = int(self.hidden_y + (self.target_y - self.hidden_y) * ease)
        self.move(self.fixed_x, curr_y)
        return True

    def start_timer(self):
        self.elapsed = 0.0
        self.timer_step = 0.05
        GLib.timeout_add(int(self.timer_step * 1000), self.update_timer)

    def update_timer(self):
        if self.is_animating:
            return False
        if not self.is_hovered:
            self.elapsed += self.timer_step
            remain = max(0.0, 1.0 - (self.elapsed / self.display_time))
            self.progress_bar.set_fraction(remain)
            
            if self.elapsed >= self.display_time:
                self.animate_out(self.schedule_next)
                return False
        return True

    def schedule_next(self):
        self.current_index = (self.current_index + 1) % len(DHIKR_ITEMS)
        GLib.timeout_add(int(self.cooldown_time * 1000), self.popup_next)

    def popup_next(self):
        self.load_item(self.current_index)
        self.animate_in()
        return False

    def on_close_clicked(self, widget):
        self.animate_out(self.schedule_next)

    def on_click(self, widget, event):
        if event.button == 1:
            self.animate_out(self.schedule_next)

    def on_mouse_enter(self, widget, event):
        self.is_hovered = True

    def on_mouse_leave(self, widget, event):
        self.is_hovered = False

def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    display_sec = 9.0
    cooldown_sec = 7.0
    
    if len(sys.argv) > 1:
        try:
            display_sec = float(sys.argv[1])
        except ValueError:
            pass
    if len(sys.argv) > 2:
        try:
            cooldown_sec = float(sys.argv[2])
        except ValueError:
            pass

    toast = DzikirToast(display_time=display_sec, cooldown_time=cooldown_sec)
    Gtk.main()

if __name__ == "__main__":
    main()
