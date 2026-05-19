#!/bin/bash

# Tailscale Reparatur Script

echo "🔧 Repariere Tailscale..."

# Tailscale Service stoppen
echo "🛑 Stoppe Tailscale Service..."
sudo systemctl stop tailscaled 2>/dev/null || true
sudo pkill -9 tailscaled 2>/dev/null || true

# Warten bis Process komplett beendet ist
sleep 2

# Tailscale Service starten
echo "🚀 Starte Tailscale Service..."
sudo systemctl start tailscaled
sudo systemctl enable tailscaled

# Warten bis Service bereit ist
echo "⏳ Warte auf Tailscale Service..."
sleep 5

# Tailscale verbinden
echo "🔗 Verbinde Tailscale..."
sudo tailscale up

# Status prüfen
echo "📊 Tailscale Status:"
sudo tailscale status

# IP anzeigen
TAILSCALE_IP=$(sudo tailscale ip -4 2>/dev/null || echo "Nicht verfügbar")
echo ""
echo "✅ Tailscale repariert und aktiv!"
echo ""
echo "📡 SSH über Tailscale:"
if [ -n "$TAILSCALE_IP" ] && [ "$TAILSCALE_IP" != "Nicht verfügbar" ]; then
    echo "   ssh dyai@$TAILSCALE_IP"
else
    echo "   Tailscale IP wird noch ermittelt..."
    echo "   Prüfe mit: sudo tailscale ip -4"
fi
echo ""
echo "🌐 Tailscale Dashboard: https://login.tailscale.com/admin/machines"