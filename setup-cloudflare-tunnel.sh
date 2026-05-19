#!/bin/bash

# Cloudflare Tunnel Setup für SSH ohne Port Forwarding

echo "🌐 Setup Cloudflare Tunnel für SSH..."

# Cloudflare Tunnel installieren
if ! command -v cloudflared &> /dev/null; then
    echo "📦 Installiere cloudflared..."
    wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
    sudo dpkg -i cloudflared-linux-amd64.deb
    rm cloudflared-linux-amd64.deb
else
    echo "✅ cloudflared bereits installiert"
fi

# Tunnel erstellen (nicht interaktiv)
echo "🔧 Erstelle Cloudflare Tunnel..."
TUNNEL_NAME="ssh-tunnel"
TUNNEL_UUID=$(cloudflared tunnel create $TUNNEL_NAME --output /tmp/tunnel.json 2>&1 | grep -oP '(?<=id: )[^ ]+' || echo "")

if [ -z "$TUNNEL_UUID" ]; then
    echo "⚠️  Tunnel existiert vielleicht bereits, versuche vorhandenen Tunnel zu nutzen..."
    # Versuche vorhandenen Tunnel zu finden
    cloudflared tunnel list
    echo ""
    echo "Bitte manuellen Setup folgen:"
    echo "1. Gehe zu https://dash.cloudflare.com/"
    echo "2. Zero Trust → Networks → Tunnels"
    echo "3. Erstelle neuen Tunnel oder nutze vorhandenen"
    echo "4. Konfiguriere SSH Service"
    exit 1
fi

echo "✅ Tunnel erstellt: $TUNNEL_UUID"

# Konfiguration erstellen
echo "⚙️  Erstelle Tunnel Konfiguration..."
mkdir -p ~/.cloudflared
cat > ~/.cloudflared/config.yml <<EOF
tunnel: $TUNNEL_UUID
credentials-file: ~/.cloudflared/$TUNNEL_UUID.json

ingress:
  - hostname: ssh.vision.dyai.cloud
    service: ssh://localhost:22
  - service: http_status:404
EOF

# Credentials verschieben
mv /tmp/tunnel.json ~/.cloudflared/$TUNNEL_UUID.json

# Tunnel als Service starten
echo "🚀 Starte Cloudflare Tunnel Service..."
sudo cloudflared service install
sudo systemctl start cloudflared
sudo systemctl enable cloudflared

# DNS Record erstellen
echo "📝 DNS Record needed:"
echo "   CNAME ssh.vision.dyai.cloud → $TUNNEL_UUID.cfargotunnel.com"
echo ""
echo "📊 Tunnel Status:"
sudo systemctl status cloudflared --no-pager

echo ""
echo "✅ Cloudflare Tunnel eingerichtet!"
echo ""
echo "📡 Nächste Schritte:"
echo "1. Gehe zu https://dash.cloudflare.com/"
echo "2. Zero Trust → Networks → Tunnels"
echo "3. Wähle den Tunnel '$TUNNEL_NAME'"
echo "4. Konfiguriere Public Hostname:"
echo "   - Subdomain: ssh"
echo "   - Domain: vision.dyai.cloud"
echo "   - Service: ssh://localhost:22"
echo ""
echo "🔐 Danach SSH über: ssh dyai@ssh.vision.dyai.cloud"