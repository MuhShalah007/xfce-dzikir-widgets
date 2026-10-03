#!/bin/bash
# Start conky + dzikir bar and enable persistent click-through.

pkill conky 2>/dev/null
pkill -f clickthrough_loop 2>/dev/null
sleep 1

export DISPLAY=:0

# Start system monitor conky (right sidebar)
conky -d -c /home/darsya/.config/conky/conky.conf
sleep 2

# Dzikir top bar — GTK+Pango (proper Arabic shaping; conky Xft breaks ligatures)
DISPLAY=:0 nohup python3 /home/darsya/.config/conky/scripts/dzikir_bar.py >/dev/null 2>&1 &
sleep 2

# Click-through for system monitor (persistent loop — conky may reset shape on update)
nohup bash /home/darsya/.config/conky/scripts/clickthrough_loop.sh "ConkySystem" >/dev/null 2>&1 &

# Click-through + raise for dzikir bar (persistent loop)
nohup bash /home/darsya/.config/conky/scripts/clickthrough_loop.sh "DzikirBar" >/dev/null 2>&1 &
wmctrl -r DzikirBar -b add,above 2>/dev/null
