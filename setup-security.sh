#!/bin/bash

# SSH und Firewall Setup

echo "🔐 Konfiguriere SSH und Firewall..."

# SSH Service aktivieren
echo "📡 Aktiviere SSH Service..."
sudo systemctl start ssh
sudo systemctl enable ssh

# SSH Status prüfen
echo "📊 SSH Status:"
sudo systemctl status ssh --no-pager

# Firewall konfigurieren
echo "🔥 Konfiguriere Firewall..."
sudo ufw allow 22/tcp comment 'SSH'
sudo ufw allow 80/tcp comment 'HTTP'
sudo ufw allow 443/tcp comment 'HTTPS'
sudo ufw --force enable

# Firewall Status prüfen
echo "📊 Firewall Status:"
sudo ufw status verbose

echo ""
echo "✅ SSH und Firewall konfiguriert!"
echo ""
echo "📡 SSH Zugriff:"
echo "   Lokal: ssh dyai@localhost"
echo "   Extern: ssh dyai@93.128.152.173"
echo "   Domain: ssh dyai@vision.dyai.cloud (nach DNS-Propagation)"
echo ""
echo "🔐 Offene Ports:"
echo "   22/tcp - SSH"
echo "   80/tcp - HTTP (Caddy)"
echo "   443/tcp - HTTPS (Cloudflare)"