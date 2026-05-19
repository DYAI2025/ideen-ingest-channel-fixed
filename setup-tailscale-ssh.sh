#!/bin/bash

# Tailscale SSH Setup

echo "🦎 Konfiguriere Tailscale für SSH..."

# Tailscale starten
echo "🚀 Starte Tailscale..."
sudo tailscale up

# Tailscale Status
echo "📊 Tailscale Status:"
sudo tailscale status

# Tailscale IP anzeigen
TAILSCALE_IP=$(sudo tailscale ip -4)
echo ""
echo "✅ Tailscale läuft!"
echo ""
echo "📡 SSH über Tailscale:"
echo "   ssh dyai@$TAILSCALE_IP"
echo ""
echo "🌐 Tailscale IP: $TAILSCALE_IP"
echo "🔐 Kein Port Forwarding nötig - funktioniert überall!"