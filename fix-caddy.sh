#!/bin/bash

# Caddy Fix Script

echo "🔧 Repariere Caddy Konfiguration..."

# Backup der alten Konfiguration
sudo cp /etc/caddy/Caddyfile /etc/caddy/Caddyfile.backup

# Vereinfachte Konfiguration kopieren
sudo cp /home/dyai/ideen-ingest-channel/Caddyfile-simple /etc/caddy/Caddyfile

# Caddy Konfiguration validieren
echo "🔍 Validiere Caddy Konfiguration..."
sudo caddy validate --config /etc/caddy/Caddyfile

# Wenn Validierung erfolgreich, Caddy neu starten
if [ $? -eq 0 ]; then
    echo "✅ Konfiguration valide, starte Caddy neu..."
    sudo systemctl restart caddy
    sleep 3
    
    # Status prüfen
    sudo systemctl status caddy --no-pager
    
    echo ""
    echo "✅ Caddy sollte jetzt laufen!"
    echo "📊 Prüfe mit: sudo systemctl status caddy"
    echo "📝 Logs: sudo journalctl -u caddy -f"
else
    echo "❌ Konfiguration fehlerhaft"
    echo "🔄 Backup wiederherstellen..."
    sudo cp /etc/caddy/Caddyfile.backup /etc/caddy/Caddyfile
fi