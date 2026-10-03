#!/usr/bin/env bash
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${RED}Menghentikan dan menghapus XFCE Dzikir Widgets...${NC}"

# Stop processes
pkill -f "dzikir_popup.py" 2>/dev/null || true
pkill -f "dzikir_bar.py" 2>/dev/null || true

# Remove binaries and autostarts
rm -f "$HOME/.local/bin/dzikir-popup" "$HOME/.local/bin/dzikir-bar"
rm -f "$HOME/.config/autostart/dzikir-popup.desktop" "$HOME/.config/autostart/dzikir-bar.desktop"

# Prompt remove configs
read -p "Hapus juga folder konfigurasi di ~/.config/xfce-dzikir-widgets? [y/N]: " confirm
if [[ "$confirm" =~ ^[yY]$ ]]; then
  rm -rf "$HOME/.config/xfce-dzikir-widgets"
  echo -e "${GREEN}✓ Folder konfigurasi dihapus.${NC}"
fi

echo -e "${GREEN}✓ Uninstall selesai.${NC}"
