# Domain Setup Anleitung: vision.dyai.cloud

## Problem: SSH Connection Refused
**Ursache:** SSH Service ist nicht aktiviert

## Lösung 1: SSH Aktivieren
```bash
sudo systemctl start ssh
sudo systemctl enable ssh
```

## Lösung 2: DNS Einrichtung
Bevor du das Domain Setup startest, musst du den DNS Record erstellen:

### DNS Record erstellen
Gehe zu deinem DNS-Provider (Cloudflare, Namecheap, etc.) und erstelle:

**Typ:** A Record  
**Name:** vision.dyai.cloud  
**Wert:** 93.128.152.173  
**TTL:** 300 (5 Minuten)

### DNS Prüfen
```bash
./check-dns.sh
```

## Lösung 3: Automatisches Setup
Führe das Setup Script aus:
```bash
cd /home/dyai/ideen-ingest-channel
./setup-domain.sh
```

Das Script macht automatisch:
1. ✅ SSH Service aktivieren
2. ✅ Caddy installieren
3. ✅ SSL-Zertifikate automatisch (Let's Encrypt)
4. ✅ Reverse Proxy konfigurieren
5. ✅ Firewall öffnen

## Lösung 4: Manuelles Setup (ohne Script)

### 1. SSH aktivieren
```bash
sudo systemctl start ssh
sudo systemctl enable ssh
```

### 2. Caddy installieren
```bash
# Caddy GPG Key hinzufügen
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg

# Caddy Repo hinzufügen
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list

# Installieren
sudo apt update
sudo apt install caddy -y
```

### 3. Caddy Konfiguration
```bash
sudo nano /etc/caddy/Caddyfile
```

Inhalt:
```caddy
# Main Domain
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
    reverse_proxy localhost:3000
}

# Obsidian Graph Subdomain
graph.vision.dyai.cloud {
    reverse_proxy localhost:3006
}

# Obsidian Kanban Subdomain
obsidian.vision.dyai.cloud {
    reverse_proxy localhost:3007
}
```

### 4. Caddy starten
```bash
sudo systemctl restart caddy
sudo systemctl enable caddy
```

### 5. Firewall öffnen
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw --force enable
```

## Ergebnis
Nach erfolgreichem Setup sind folgende URLs erreichbar:

- **Main:** https://vision.dyai.cloud
- **Kanban:** https://kanban.vision.dyai.cloud  
- **Graph:** https://graph.vision.dyai.cloud
- **Obsidian:** https://obsidian.vision.dyai.cloud

SSL-Zertifikate werden automatisch von Let's Encrypt ausgestellt.

## Fehlersuche

### SSL Probleme
```bash
# Caddy Logs prüfen
sudo journalctl -u caddy -f

# DNS prüfen
dig vision.dyai.cloud
```

### Service Status
```bash
# Caddy Status
sudo systemctl status caddy

# SSH Status
sudo systemctl status ssh
```

### Port Prüfung
```bash
# Ports prüfen
sudo netstat -tulpn | grep -E ':(80|443|22)'
```

## SSH Zugriff nach Setup
```bash
ssh dyai@93.128.152.173
```

Ofter mit dem neuen Domain Namen (wenn DNS propagiert ist):
```bash
ssh dyai@vision.dyai.cloud
```