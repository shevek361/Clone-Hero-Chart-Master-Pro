#!/bin/bash
# Prüfen, ob python3 installiert ist
if command -v python3 &>/dev/null; then
    echo "Starte CH Chart Master Pro..."
    python3 main.py
else
    echo "Fehler: python3 wurde nicht gefunden. Bitte mit 'sudo apt install python3' installieren."
    read -p "Drücke Enter zum Beenden..."
fi
