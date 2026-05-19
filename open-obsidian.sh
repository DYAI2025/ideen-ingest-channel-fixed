#!/bin/bash

# Obsidian Opener Script
# Öffnet Obsidian mit dem GBrain-Vault als Graph

OBSIDIAN_VAULT="/home/dyai/obsidian-vault"

echo "🧠 Öffne Obsidian mit GBrain Vault..."

# Prüfen ob Obsidian installiert ist
if command -v obsidian &> /dev/null; then
    obsidian "$OBSIDIAN_VAULT"
elif [ -f "/usr/bin/obsidian" ]; then
    /usr/bin/obsidian "$OBSIDIAN_VAULT"
elif [ -f "/usr/bin/flatpak" ]; then
    flatpak run md.obsidian.Obsidian "$OBSIDIAN_VAULT"
else
    echo "❌ Obsidian nicht gefunden"
    echo ""
    echo "Installations-Optionen:"
    echo "1. Download: https://obsidian.md/download"
    echo "2. Flatpak: flatpak install flathub md.obsidian.Obsidian"
    echo "3. Snap: snap install obsidian"
    echo ""
    echo "Alternativ: Nutze den Web-Graph Viewer:"
    echo "🌐 http://localhost:3006"
fi