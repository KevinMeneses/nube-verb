#!/bin/zsh
# Instala Nube Verb en REAPER (macOS) como enlace: los cambios del repo se ven al volver a insertar el FX.
set -e
DST="$HOME/Library/Application Support/REAPER/Effects/Nube Verb"
cd "$(dirname "$0")"
mkdir -p "$DST"
ln -sf "$PWD/nube_verb.jsfx" "$DST/nube_verb.jsfx"
echo "Listo: en REAPER busca \"Nube Verb\" en el navegador de FX (JS: Nube Verb)."
