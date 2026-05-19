#!/bin/bash

# Setup Script für direkte DNS (ohne Cloudflare)
# Caddy übernimmt SSL mit Let's Encrypt

set -e

echo "🌐 Setup für direkte DNS + Caddy SSL"

echo "📝 DNS Einstellungen (ohne Cloudflare Proxy):"
echo "=============================================="
echo "Gehe zu deinem DNS-Provider"
echo ""
echo "Erstelle/Update folgende DNS Records:"
echo ""
echo "1. vision.dyai.cloud"
echo "   Typ: A"
echo "   Inhalt: 93.128.152.173"
echo "   Proxy: ❌ (Graue Wolke) - Deaktiviert"
echo "   TTL: 300"
echo ""
echo "2. kanban.vision.dyai.cloud"
echo "   Typ: A"
echo "   Inhalt: 93.128.152.173"
echo "   Proxy: ❌ (Graue Wolke) - Deaktiviert"
echo "   TTL: 300"
echo ""
echo "3. graph.vision.dyai.cloud"
echo "   Typ: A"
echo "   Inhalt: 93.128.152.173"
echo "   Proxy: ❌ (Graue Wolke) - Deaktiviert"
echo "   TTL: 300"
echo ""
echo "4. obsidian.vision.dyai.cloud"
echo "   Typ: A"
echo "   Inhalt: 93.128.152.173"
echo "   Proxy: ❌ (Graue Wolke) - Deaktiviert"
echo "   TTL: 300"
echo ""

read -p "DNS konfiguriert (ohne Proxy)? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Bitte erst DNS konfigurieren"
    exit 1
fi

# DNS prüfen
echo "🔍 Prüfe DNS Propagation..."
sleep 5

./check-dns.sh
if [ $? -ne 0 ]; then
    echo "⚠️  DNS noch nicht propagiert, versuche trotzdem weiter..."
fi

# Caddy Konfiguration mit SSL
echo "🔧 Konfiguriere Caddy mit SSL..."
sudo cp /home/dyai/ideen-ingest-channel/Caddyfile-simple /etc/caddy/Caddyfile

# Caddy validieren und starten
echo "✅ Validiere Caddy Konfiguration..."
sudo caddy validate --config /etc/caddy/Caddyfile

if [ $? -eq 0 ]; then
    echo "🔄 Starte Caddy neu (SSL wird automatisch ausgestellt)..."
    sudo systemctl restart caddy
    sudo systemctl enable caddy
    
    sleep 5
    
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
    echo "🔐 SSL wird automatisch von Let's Encrypt ausgestellt"
    echo "⏳ Warte 5-10 Minuten für SSL-Ausstellung"
else
    echo "❌ Caddy Konfiguration fehlerhaft"
    exit 1
fi