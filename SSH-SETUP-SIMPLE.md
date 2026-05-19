# SSH Setup - Einfache Lösung

## Problem
Port 22 ist von außen nicht erreichbar (Router Port Forwarding fehlt)

## Lösung: SSH Port ändern auf 2222

### Schritt 1: SSH Port ändern
```bash
cd /home/dyai/ideen-ingest-channel
./change-ssh-port.sh
```

### Schritt 2: Router Port Forwarding einrichten

#### Für FritzBox:
1. Öffne: http://fritz.box
2. Internet → Freigaben → Portfreigaben
3. Neue Portfreigabe:
   - Anwendung: "SSH" oder "Eigen"
   - Protokoll: TCP
   - Externer Port: **2222**
   - Interner Port: **2222**
   - An Computer: **192.168.178.65** (deine IP)
4. Speichern

#### Für andere Router:
1. Router-Interface öffnen (meist 192.168.1.1 oder 192.168.178.1)
2. Port Forwarding / NAT / Virtual Server
3. Regel erstellen:
   - Extern Port: 2222
   - Intern Port: 2222
   - Intern IP: 192.168.178.65
   - Protokoll: TCP

### Schritt 3: Firewall aktualisieren
```bash
sudo ufw allow 2222/tcp comment "SSH on port 2222"
```

### Schritt 4: Testen
```bash
# Von außen (nach Router-Konfiguration):
ssh -p 2222 dyai@93.128.152.173
```

## Alternative: Kein SSH von außen nötig

Da du Cloudflare für die Web-Services nutzt, kannst du:
- Web-Services über HTTPS erreichen: https://vision.dyai.cloud
- SSH nur lokal nutzen (wenn du am Computer sitzt)
- Für Remote-SSH später Tailscale reparieren oder Cloudflare Tunnel nutzen

## Empfehlung
1. Erst Web-Services testen (Cloudflare funktioniert bereits)
2. SSH später einrichten, wenn du wirklich externen SSH-Zugriff brauchst