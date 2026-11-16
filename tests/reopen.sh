#!/bin/zsh
# Cierra la demo de la interfaz (si hay) y la vuelve a abrir con el código nuevo. NUBE_SHOT=archivo.png toma captura.
cd "$(dirname "$0")"
R=/Applications/REAPER.app/Contents/MacOS/REAPER
osascript -e 'tell application "System Events" to tell process "REAPER" to get name of every window' 2>/dev/null | grep -q "Nube Verb demo" && { $R -nonewinst "$PWD/ui_close.lua" >/dev/null 2>&1 & sleep 3; }
rm -f out/ui.txt; $R -nonewinst "$PWD/ui_demo.lua" >/dev/null 2>&1 &
for i in $(seq 1 20); do grep -q done out/ui.txt 2>/dev/null && break; sleep 0.5; done; sleep 2.5
[ -n "$NUBE_SHOT" ] && screencapture -x -R26,66,1000,693 "$NUBE_SHOT"
echo listo
