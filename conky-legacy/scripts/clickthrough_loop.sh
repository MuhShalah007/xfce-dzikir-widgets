#!/bin/bash
# Re-apply click-through to conky/dzikir windows every 5s in case WM resets shape.
# Usage: clickthrough_loop.sh "WindowName"
export DISPLAY=:0

WINNAME="$1"
[ -z "$WINNAME" ] && exit 1

while true; do
    WID=$(xdotool search --name "$WINNAME" 2>/dev/null | head -1)
    if [ -n "$WID" ]; then
        python3 /home/darsya/.config/conky/scripts/clickthrough.py "$WID" 2>/dev/null
    fi
    sleep 5
done
