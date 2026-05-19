#!/bin/bash

# SSH Port ändern (z.B. auf 2222)

NEW_PORT=2222

echo "🔧 Ändere SSH Port auf $NEW_PORT..."

# SSH Konfiguration ändern
sudo sed -i "s/#Port 22/Port $NEW_PORT/" /etc/ssh/sshd_config
sudo sed -i "s/Port 22/Port $NEW_PORT/" /etc/ssh/sshd_config

# Firewall neuen Port öffnen
sudo ufw allow $NEW_PORT/tcp comment "SSH on port $NEW_PORT"

# SSH neu starten
sudo systemctl restart ssh

echo "✅ SSH Port auf $NEW_PORT geändert!"
echo ""
echo "📡 Neuer SSH Zugriff:"
echo "   ssh -p $NEW_PORT dyai@93.128.152.173"
echo ""
echo "🔐 Router Port Forwarding:"
echo "   Externer Port: $NEW_PORT"
echo "   Interner Port: $NEW_PORT"
echo "   Interne IP: 192.168.178.65"