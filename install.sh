#!/usr/bin/env bash
set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}====================================================${NC}"
echo -e "${BLUE}       XFCE / Linux Desktop Dzikir Widgets          ${NC}"
echo -e "${BLUE}====================================================${NC}"

# Target directories
CONFIG_DIR="$HOME/.config/xfce-dzikir-widgets"
BIN_DIR="$HOME/.local/bin"
AUTOSTART_DIR="$HOME/.config/autostart"
SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

mkdir -p "$CONFIG_DIR" "$BIN_DIR" "$AUTOSTART_DIR"

# 1. Check and install system packages if needed
install_dependencies() {
  echo -e "\n${YELLOW}[1/4] Memeriksa dependensi sistem...${NC}"
  
  MISSING_PKGS=()

  if command -v apt-get >/dev/null 2>&1; then
    # Debian/Ubuntu
    PKGS=("python3-gi" "gir1.2-gtk-3.0" "gir1.2-pango-1.0" "fonts-noto-core" "libxfixes3" "libx11-6")
    for pkg in "${PKGS[@]}"; do
      if ! dpkg -s "$pkg" >/dev/null 2>&1; then
        MISSING_PKGS+=("$pkg")
      fi
    done
    if [ ${#MISSING_PKGS[@]} -gt 0 ]; then
      echo -e "Memasang paket via apt: ${MISSING_PKGS[*]}"
      if command -v sudo >/dev/null 2>&1; then
        sudo apt-get update && sudo apt-get install -y "${MISSING_PKGS[@]}" || echo -e "${RED}Gagal install otomatis, jalankan manual jika perlu.${NC}"
      fi
    else
      echo -e "${GREEN}✓ Semua dependensi sistem (apt) sudah lengkap.${NC}"
    fi

  elif command -v pacman >/dev/null 2>&1; then
    # Arch Linux
    PKGS=("python-gobject" "gtk3" "pango" "noto-fonts" "libxfixes" "libx11")
    if command -v sudo >/dev/null 2>&1; then
      sudo pacman -S --needed --noconfirm "${PKGS[@]}" || true
    fi

  elif command -v dnf >/dev/null 2>&1; then
    # Fedora
    PKGS=("python3-gobject" "gtk3" "pango" "google-noto-naskh-arabic-fonts" "libXfixes" "libX11")
    if command -v sudo >/dev/null 2>&1; then
      sudo dnf install -y "${PKGS[@]}" || true
    fi
  else
    echo -e "${YELLOW}Package manager tidak terdeteksi otomatis. Pastikan python3-gi, gtk3, & font Noto Arabic terpasang.${NC}"
  fi
}

# 2. Copy scripts to config and bin
install_scripts() {
  echo -e "\n${YELLOW}[2/4] Memasang file script dan binary...${NC}"
  
  cp "$SRC_DIR/dzikir-popup/dzikir_popup.py" "$CONFIG_DIR/"
  cp "$SRC_DIR/dzikir-bar/dzikir_bar.py" "$CONFIG_DIR/"
  chmod +x "$CONFIG_DIR/dzikir_popup.py" "$CONFIG_DIR/dzikir_bar.py"

  cp "$SRC_DIR/dzikir-popup/dzikir-popup" "$BIN_DIR/"
  cp "$SRC_DIR/dzikir-bar/dzikir-bar" "$BIN_DIR/"
  chmod +x "$BIN_DIR/dzikir-popup" "$BIN_DIR/dzikir-bar"

  # Ensure ~/.local/bin in PATH
  if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo "export PATH=\"\$HOME/.local/bin:\$PATH\"" >> "$HOME/.bashrc"
    echo -e "${GREEN}✓ Menambahkan $BIN_DIR ke ~/.bashrc${NC}"
  fi

  echo -e "${GREEN}✓ File script berhasil dipasang ke $CONFIG_DIR dan $BIN_DIR${NC}"
}

# 3. Setup autostart mode
setup_autostart() {
  echo -e "\n${YELLOW}[3/4] Mengatur Autostart...${NC}"
  
  MODE="${1:-popup}"
  case "$MODE" in
    --bar|bar)
      rm -f "$AUTOSTART_DIR/dzikir-popup.desktop"
      cp "$SRC_DIR/dzikir-bar/dzikir-bar.desktop" "$AUTOSTART_DIR/"
      echo -e "${GREEN}✓ Autostart diatur ke: Dzikir Bar (Top Scroll)${NC}"
      ;;
    --both|both)
      cp "$SRC_DIR/dzikir-popup/dzikir-popup.desktop" "$AUTOSTART_DIR/"
      cp "$SRC_DIR/dzikir-bar/dzikir-bar.desktop" "$AUTOSTART_DIR/"
      echo -e "${GREEN}✓ Autostart diatur ke: Dzikir Popup + Dzikir Bar${NC}"
      ;;
    --none|none)
      rm -f "$AUTOSTART_DIR/dzikir-popup.desktop" "$AUTOSTART_DIR/dzikir-bar.desktop"
      echo -e "${GREEN}✓ Autostart dinonaktifkan (manual run only).${NC}"
      ;;
    *)
      rm -f "$AUTOSTART_DIR/dzikir-bar.desktop"
      cp "$SRC_DIR/dzikir-popup/dzikir-popup.desktop" "$AUTOSTART_DIR/"
      echo -e "${GREEN}✓ Autostart diatur ke: Dzikir Popup (Telegram Notification Toast)${NC}"
      ;;
  esac
}

# 4. Start service
start_service() {
  echo -e "\n${YELLOW}[4/4] Menjalankan widget...${NC}"
  
  MODE="${1:-popup}"
  case "$MODE" in
    --bar|bar)
      "$BIN_DIR/dzikir-popup" stop >/dev/null 2>&1 || true
      "$BIN_DIR/dzikir-bar" restart
      ;;
    --both|both)
      "$BIN_DIR/dzikir-popup" restart
      "$BIN_DIR/dzikir-bar" restart
      ;;
    --none|none)
      echo "Widget tidak dijalankan otomatis."
      ;;
    *)
      "$BIN_DIR/dzikir-bar" stop >/dev/null 2>&1 || true
      "$BIN_DIR/dzikir-popup" restart
      ;;
  esac
}

# Run All
install_dependencies
install_scripts
setup_autostart "$1"
start_service "$1"

echo -e "\n${GREEN}====================================================${NC}"
echo -e "${GREEN}         Instalasi Selesai & Siap Pakai!           ${NC}"
echo -e "${GREEN}====================================================${NC}"
echo -e "Perintah yang tersedia:"
echo -e "  • ${BLUE}dzikir-popup {start|stop|restart|status}${NC}"
echo -e "  • ${BLUE}dzikir-bar   {start|stop|restart|status}${NC}"
echo -e "\nKonfigurasi dan database dzikir:"
echo -e "  • ${YELLOW}$CONFIG_DIR/dzikir_popup.py${NC}"
echo -e "  • ${YELLOW}$CONFIG_DIR/dzikir_bar.py${NC}\n"
