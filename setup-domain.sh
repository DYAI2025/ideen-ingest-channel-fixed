#!/bin/bash

# Setup Script für vision.dyai.cloud mit Caddy Reverse Proxy
# Automatisches SSL via Let's Encrypt

set -e

echo "🚀 Starte Domain Setup für vision.dyai.cloud"

# 1. SSH Service aktivieren (für externen Zugriff)
echo "📡 Aktiviere SSH Service..."
sudo systemctl start ssh
sudo systemctl enable ssh

# 2. Caddy installieren
echo "📦 Installiere Caddy..."
if ! command -v caddy &> /dev/null; then
    # Caddy Repo hinzufügen
    curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
    curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
    
    sudo apt update
    sudo apt install caddy -y
else
    echo "✅ Caddy bereits installiert"
fi

# 3. DNS Einrichtung prüfen
echo "🌐 Prüfe DNS für vision.dyai.cloud..."
echo "⚠️  Stelle sicher, dass vision.dyai.cloud auf 93.128.152.173 zeigt!"
echo "   DNS Record: A vision.dyai.cloud → 93.128.152.173"
read -p "DNS eingerichtet? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Bitte erst DNS einrichten, dann Script erneut ausführen"
    exit 1
fi

# 4. Caddy Konfiguration erstellen
echo "⚙️  Erstelle Caddy Konfiguration..."
sudo tee /etc/caddy/Caddyfile > /dev/null <<EOF
# Main Domain mit automatischem SSL
vision.dyai.cloud {
    # GBrain Backend
    handle_path /api/* {
        reverse_proxy localhost:8001
    }
    
    # GBrain Frontend
    handle_path /* {
        reverse_proxy localhost:5173
    }
}

# Kanban Subdomain
kanban.vision.dyai.cloud {
    handle_path /* {
        reverse_proxy localhost:3000
    }
}

# Obsidian Graph Subdomain
graph.vision.dyai.cloud {
    handle_path /* {
        reverse_proxy localhost:3006
    }
}

# Obsidian Kanban Subdomain
obsidian.vision.dyai.cloud {
    handle_path /* {
        reverse_proxy localhost:3007
    }
}
EOF

# 5. Caddy Service starten
echo "🔄 Starte Caddy Service..."
sudo systemctl restart caddy
sudo systemctl enable caddy

# 6. Firewall Ports öffnen
echo "🔐 Öffne Firewall Ports..."
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw --force enable

# 7. Status prüfen
echo "📊 Prüfe Status..."
sleep 5
sudo systemctl status caddy --no-pager

echo ""
echo "✅ Domain Setup abgeschlossen!"
echo ""
echo "🌐 Verfügbare URLs:"
echo "   Main:      https://vision.dyai.cloud"
echo "   Kanban:    https://kanban.vision.dyai.cloud"
echo "   Graph:     https://graph.vision.dyai.cloud"
echo "   Obsidian:  https://obsidian.vision.dyai.cloud"
echo ""
echo "🔐 SSL-Zertifikate werden automatisch von Let's Encrypt ausgestellt"
echo "📡 SSH Zugriff: ssh dyai@93.128.152.173"
echo ""
echo "⚠️  Warte 5-10 Minuten für DNS-Propagation und SSL-Ausstellung"