# XFCE & Linux Desktop Dzikir Widgets 🕊️

Koleksi widget pengingat dzikir harian yang ringan, elegan, dan estetik untuk lingkungan desktop XFCE / Linux (GNOME, Cinnamon, MATE, dll).

Dilengkapi dengan rendering font Arab berharakat (*proper ligatures & diacritics via GTK3 + Pango*), transliterasi Latin, dan terjemahan bahasa Indonesia.

---

## 🌟 Dua Pilihan Tampilan

### 1. **Dzikir Popup (Telegram Notification Toast)**
- **Letak**: Pojok kanan bawah layar (di atas panel taskbar).
- **Gaya**: Card dark acrylic rounded bergaya notifikasi Telegram.
- **Animasi**: Meluncur naik (*slide-up*) halus saat muncul, menampilkan teks dzikir, animasi timer countdown, lalu meluncur turun.
- **Interaksi**:
  - *Hover* kursor: Menjeda timer agar bisa dibaca tanpa terburu-buru.
  - *Klik kartu*: Langsung ganti ke kalimat dzikir berikutnya.
  - *Tombol ✕*: Tutup notifikasi seketika.

### 2. **Dzikir Bar (Top Overlay)**
- **Letak**: Bilah tipis melayang di bagian atas layar.
- **Gaya**: Teks Arab berjalan (*seamless continuous scrolling ticker*).
- **Fitur**: *Click-through* (XFixes input region) sehingga klik mouse tetap tembus ke aplikasi di bawahnya.

---

## 🚀 Instalasi Cepat (1 Perintah)

```bash
git clone https://github.com/MuhShalah007/xfce-dzikir-widgets.git
cd xfce-dzikir-widgets
./install.sh
```

### Opsi Pilihan Tampilan Saat Install
```bash
./install.sh         # Pasang mode Popup Telegram (Default)
./install.sh --bar   # Pasang mode Bar Atas Ticker
./install.sh --both  # Pasang kedua-duanya
./install.sh --none  # Pasang script tanpa autostart
```

---

## 🛠️ Perintah Kontrol (CLI)

Setelah diinstall, perintah berikut bisa dipanggil langsung dari terminal:

### Dzikir Popup:
```bash
dzikir-popup start     # Jalankan popup
dzikir-popup stop      # Matikan popup
dzikir-popup restart   # Mulai ulang popup
dzikir-popup status    # Cek status running/stopped

# Custom durasi: [waktu tampil (detik)] [jeda tunggu (detik)]
dzikir-popup start 10 15
```

### Dzikir Bar:
```bash
dzikir-bar start       # Jalankan bar atas
dzikir-bar stop        # Matikan bar atas
dzikir-bar restart     # Mulai ulang bar atas
dzikir-bar status      # Cek status

# Custom: [y_offset] [tinggi] [kecepatan]
dzikir-bar start 0 36 1.5
```

---

## 📂 Struktur File

```
xfce-dzikir-widgets/
├── install.sh              # Script instalasi otomatis + autostart
├── uninstall.sh            # Script pembersihan & pencopotan
├── dzikir-popup/           # Source widget popup Telegram toast
│   ├── dzikir_popup.py
│   ├── dzikir-popup
│   └── dzikir-popup.desktop
├── dzikir-bar/             # Source widget bar atas continuous scroll
│   ├── dzikir_bar.py
│   ├── dzikir-bar
│   └── dzikir-bar.desktop
└── conky-legacy/           # Arsip konfigurasi lama berbasis Conky
    ├── conky-dzikir.conf
    ├── conky.conf
    └── scripts/
```

---

## ⚙️ Kustomisasi Kalimat Dzikir

Daftar kalimat dzikir tersimpan langsung di file Python:
- `~/.config/xfce-dzikir-widgets/dzikir_popup.py`
- `~/.config/xfce-dzikir-widgets/dzikir_bar.py`

Anda bisa menambah doa atau dzikir baru dengan format:
```python
{
    "arabic": "سُبْحَانَ اللَّهِ",
    "latin": "Subhanallah",
    "meaning": "Maha Suci Allah."
}
```

---

## 🗑️ Uninstall

Untuk menghapus widget:
```bash
./uninstall.sh
```

---

## 📜 Lisensi
MIT License.
