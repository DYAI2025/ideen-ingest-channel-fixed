#!/bin/bash

# Caddy auf Port 8080 konfigurieren (Port 80 ist belegt)

echo "🔧 Konfiguriere Caddy auf Port 8080..."

# Backup
sudo cp /etc/caddy/Caddyfile /etc/caddy/Caddyfile.backup-port80

# Neue Konfiguration
sudo cp /home/dyai/ideen-ingest-channel/Caddyfile-port8080 /etc/caddy/Caddyfile

# Firewall für Port 8080 öffnen
sudo ufw allow 8080/tcp comment "Caddy on port 8080"

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
    echo "✅ Caddy läuft jetzt auf Port 8080!"
    echo ""
    echo "⚠️  Cloudflare Konfiguration anpassen:"
    echo "   Gehe zu https://dash.cloudflare.com/"
    echo "   Zero Trust → Networks → Tunnels (oder DNS)"
    echo "   Ändere den Origin Port von 80 auf 8080"
    echo ""
    echo "🌐 Oder teste lokal:"
    echo "   http://localhost:8080"
    echo "   http://vision.dyai.cloud:8080"
else
    echo "❌ Konfiguration fehlerhaft"
    exit 1
fi