#!/bin/bash

# Caddy Cloudflare Fix Script

echo "🔧 Aktualisiere Caddy Konfiguration..."

# Backup der alten Konfiguration
sudo cp /etc/caddy/Caddyfile /etc/caddy/Caddyfile.backup-$(date +%Y%m%d-%H%M%S)

# Korrigierte Konfiguration kopieren
sudo cp /home/dyai/ideen-ingest-channel/Caddyfile-cloudflare-fixed /etc/caddy/Caddyfile

# Caddy Konfiguration validieren
echo "🔍 Validiere Caddy Konfiguration..."
sudo caddy validate --config /etc/caddy/Caddyfile

# Wenn Validierung erfolgreich, Caddy neu starten
if [ $? -eq 0 ]; then
    echo "✅ Konfiguration valide, starte Caddy neu..."
    sudo systemctl restart caddy
    sleep 3
    
    # Status prüfen
    echo "📊 Caddy Status:"
    sudo systemctl status caddy --no-pager
    
    echo ""
    echo "✅ Caddy läuft jetzt!"
    echo ""
    echo "🌐 Teste die URLs:"
    echo "   http://vision.dyai.cloud"
    echo "   http://kanban.vision.dyai.cloud"
    echo "   http://graph.vision.dyai.cloud"
    echo "   http://obsidian.vision.dyai.cloud"
    echo ""
    echo "🔐 HTTPS wird von Cloudflare bereitgestellt"
    echo "⏳ Warte 2-5 Minuten für Cloudflare Cache"
else
    echo "❌ Konfiguration fehlerhaft"
    echo "🔄 Backup wiederherstellen..."
    LATEST_BACKUP=$(ls -t /etc/caddy/Caddyfile.backup-* | head -1)
    sudo cp "$LATEST_BACKUP" /etc/caddy/Caddyfile
    exit 1
fi