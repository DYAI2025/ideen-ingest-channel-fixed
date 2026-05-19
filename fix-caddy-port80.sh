#!/bin/bash

# Caddy auf Port 80 konfigurieren (jetzt frei nach Docker-Caddy Stop)

echo "🔧 Konfiguriere Caddy auf Port 80..."

# Original Port-80 Konfiguration wiederherstellen
sudo cp /home/dyai/ideen-ingest-channel/Caddyfile-cloudflare-fixed /etc/caddy/Caddyfile

# Caddy validieren
echo "🔍 Validiere Caddy Konfiguration..."
sudo caddy validate --config /etc/caddy/Caddyfile

if [ $? -eq 0 ]; then
    echo "✅ Konfiguration valide, starte Caddy neu..."
    sudo systemctl restart caddy
    sleep 3
    
    # Status prüfen
    echo "📊 Caddy Status:"
    sudo systemctl status caddy --no-pager
    
    echo ""
    echo "✅ Caddy läuft jetzt auf Port 80!"
    echo ""
    echo "🌐 Teste lokal:"
    curl -s http://localhost:80 | head -5
    
    echo ""
    echo "🌐 Nach Cloudflare Propagation (2-5 Min):"
    echo "   https://vision.dyai.cloud"
    echo "   https://kanban.vision.dyai.cloud"
    echo "   https://graph.vision.dyai.cloud"
    echo "   https://obsidian.vision.dyai.cloud"
else
    echo "❌ Konfiguration fehlerhaft"
    exit 1
fi