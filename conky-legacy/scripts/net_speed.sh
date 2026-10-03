#!/bin/bash
# Human-readable network speed
# Usage: net_speed.sh <interface> <rx|tx>

IFACE="${1:-eno1}"
DIR="$2"

if [ "$DIR" = "rx" ]; then
    FILE="/sys/class/net/$IFACE/statistics/rx_bytes"
elif [ "$DIR" = "tx" ]; then
    FILE="/sys/class/net/$IFACE/statistics/tx_bytes"
else
    echo "0 B/s"
    exit 1
fi

PREV_FILE="/tmp/conky_net_${IFACE}_${DIR}"
CURRENT=$(cat "$FILE")

if [ -f "$PREV_FILE" ]; then
    PREV=$(cat "$PREV_FILE")
    DIFF=$((CURRENT - PREV))
    [ $DIFF -lt 0 ] && DIFF=0

    if [ $DIFF -ge 1073741824 ]; then
        printf "%.1f GB/s" $(awk "BEGIN {printf \"%.1f\", $DIFF/1073741824}")
    elif [ $DIFF -ge 1048576 ]; then
        printf "%.1f MB/s" $(awk "BEGIN {printf \"%.1f\", $DIFF/1048576}")
    elif [ $DIFF -ge 1024 ]; then
        printf "%.1f KB/s" $(awk "BEGIN {printf \"%.1f\", $DIFF/1024}")
    else
        printf "%d B/s" $DIFF
    fi
else
    echo "0 B/s"
fi

echo "$CURRENT" > "$PREV_FILE"
