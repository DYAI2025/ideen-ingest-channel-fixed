#!/bin/bash

# Setup Script für Cloudflare + Caddy
# Cloudflare übernimmt SSL, Caddy liefert HTTP

set -e

echo "🌐 Setup für Cloudflare + Caddy"

# Cloudflare DNS Konfiguration
echo "📝 Cloudflare DNS Einstellungen:"
echo "================================"
echo "Gehe zu https://dash.cloudflare.com/"
echo ""
echo "Erstelle/Update folgende DNS Records:"
echo ""
echo "1. vision.dyai.cloud"
echo "   Typ: A"
echo "   Inhalt: 93.128.152.173"
echo "   Proxy: ✅ (Orange Wolke) - Aktiviert"
echo "   TTL: Auto"
echo ""
echo "2. kanban.vision.dyai.cloud"
echo "   Typ: CNAME"
echo "   Inhalt: vision.dyai.cloud"
echo "   Proxy: ✅ (Orange Wolke) - Aktiviert"
echo "   TTL: Auto"
echo ""
echo "3. graph.vision.dyai.cloud"
echo "   Typ: CNAME"
echo "   Inhalt: vision.dyai.cloud"
echo "   Proxy: ✅ (Orange Wolke) - Aktiviert"
echo "   TTL: Auto"
echo ""
echo "4. obsidian.vision.dyai.cloud"
echo "   Typ: CNAME"
echo "   Inhalt: vision.dyai.cloud"
echo "   Proxy: ✅ (Orange Wolke) - Aktiviert"
echo "   TTL: Auto"
echo ""
echo "SSL/TLS Einstellungen in Cloudflare:"
echo "→ SSL/TLS → Overview → Mode: 'Full' oder 'Full (strict)'"
echo ""

read -p "Cloudflare DNS konfiguriert? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Bitte erst Cloudflare konfigurieren"
    exit 1
fi

# Caddy Konfiguration für HTTP (Cloudflare macht SSL)
echo "🔧 Konfiguriere Caddy für HTTP (Cloudflare übernimmt SSL)..."
sudo cp /home/dyai/ideen-ingest-channel/Caddyfile-cloudflare /etc/caddy/Caddyfile

# Caddy validieren und starten
echo "✅ Validiere Caddy Konfiguration..."
sudo caddy validate --config /etc/caddy/Caddyfile

if [ $? -eq 0 ]; then
    echo "🔄 Starte Caddy neu..."
    sudo systemctl restart caddy
    sudo systemctl enable caddy
    
    sleep 3
    
    # Status prüfen
    echo "📊 Caddy Status:"
    sudo systemctl status caddy --no-pager
    
    echo ""
    echo "✅ Setup abgeschlossen!"
    echo ""
    echo "🌐 Verfügbar unter:"
    echo "   https://vision.dyai.cloud"
    echo "   https://kanban.vision.dyai.cloud"
    echo "   https://graph.vision.dyai.cloud"
    echo "   https://obsidian.vision.dyai.cloud"
    echo ""
    echo "🔐 SSL wird von Cloudflare bereitgestellt"
    echo "⏳ Warte 2-5 Minuten für Cloudflare Cache/Propagation"
else
    echo "❌ Caddy Konfiguration fehlerhaft"
    exit 1
fi