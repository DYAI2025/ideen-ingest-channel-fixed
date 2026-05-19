# SSH Graph Access Guide

## Schnellstart für SSH-Zugriff

### 1. SSH-Tunnel aufbauen
```bash
# Auf deinem lokalen Rechner:
ssh -L 5173:localhost:5173 -L 8001:localhost:8001 benutzer@remote-server
```

### 2. Zugriff auf die Anwendung
Nachdem der SSH-Tunnel steht:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8001
- **SSH-Graph**: Klicke auf "SSH Graph" Button in der Anwendung

### 3. SSH-optimierte Graph-Features
Die SSH-Graph Ansicht bietet:
- **Automatische Aktualisierung**: Graph wird alle 30 Sekunden neu geladen
- **Optimierte Datenübertragung**: Spezielle API-Endpunkte für SSH
- **Geringere Latenz**: Effizientere Datenstruktur
- **Offline-fähig**: Cache für langsame Verbindungen

## SSH-Graph API Endpunkte

### Vollständiger Graph
```bash
curl http://localhost:8001/api/graph/full-graph
```

### Nur Knoten
```bash
curl http://localhost:8001/api/graph/nodes
```

### Nur Kanten
```bash
curl http://localhost:8001/api/graph/edges
```

## SSH-Konfiguration

### ~/.ssh/config Eintrag
```ssh
Host ideen-server
    HostName your-server.com
    User benutzer
    LocalForward 5173 localhost:5173
    LocalForward 8001 localhost:8001
```

### Verwendung
```bash
ssh ideen-server
```

## Automatischer SSH-Tunnel

### Mit autossh (für dauerhafte Verbindungen)
```bash
sudo apt install autossh

autossh -M 0 -o "ServerAliveInterval 30" -o "ServerAliveCountMax 3" \
  -L 5173:localhost:5173 -L 8001:localhost:8001 \
  benutzer@remote-server
```

### Systemd Service für dauerhaften Tunnel
```ini
[Unit]
Description=SSH Tunnel for Ideen Ingest Channel
After=network.target

[Service]
User=benutzer
ExecStart=/usr/bin/ssh -N -o ServerAliveInterval=60 -o ServerAliveCountMax=3 \
  -L 5173:localhost:5173 -L 8001:localhost:8001 \
  benutzer@remote-server
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

## Performance-Optimierung für SSH

### 1. Kompression aktivieren
```bash
ssh -C -L 5173:localhost:5173 -L 8001:localhost:8001 benutzer@remote-server
```

### 2. SSH-Konfiguration optimieren
In `~/.ssh/config`:
```
Host ideen-server
    Compression yes
    CompressionLevel 6
    Ciphers aes128-ctr,aes192-ctr,aes256-ctr
```

### 3. Graph-Aktualisierungsintervall anpassen
In der SSHGraph-Komponente:
```typescript
<SSHGraph 
  apiUrl="/api/graph" 
  autoRefresh={true} 
  refreshInterval={60000} // 60 Sekunden statt 30
/>
```

## Troubleshooting

### Verbindung fehlgeschlagen
```bash
# SSH-Verbindung testen
ssh benutzer@remote-server

# Ports prüfen
netstat -tuln | grep -E '5173|8001'
```

### Graph wird nicht aktualisiert
- Browser-Cache leeren
- Auf Netzwerkverbindung prüfen
- API-Endpunkt direkt testen: `curl http://localhost:8001/api/graph/full-graph`

### Langsame Verbindung
- Kompression aktivieren (-C)
- Aktualisierungsintervall erhöhen
- Weniger Knoten im Graph anzeigen

## Sicherheitshinweise

1. **SSH-Keys verwenden**: Statt Passwörter
2. **Firewall konfigurieren**: Nur notwendige Ports öffnen
3. **Reverse SSH Tunnel**: Für Server hinter NAT
4. **VPN verwenden**: Für zusätzliche Sicherheit

## Reverse SSH Tunnel (Server hinter NAT)

### Auf dem Server (hinter NAT):
```bash
ssh -R 8001:localhost:8001 -R 5173:localhost:5173 user@public-server
```

### Auf dem öffentlichen Server:
```bash
# Lokal weiterleiten
ssh -L 8001:localhost:8001 -L 5173:localhost:5173 localhost
```

## Mobile Zugriff

### SSH-Apps für iOS:
- Termius
- Blink Shell
- Prompt 2

### SSH-Apps für Android:
- Termux
- JuiceSSH
- ConnectBot

## Monitoring

### SSH-Verbindung überwachen
```bash
# Verbindungstest
ssh -o ConnectTimeout=5 benutzer@remote-server echo "OK"

# Automatischer Neustart bei Verbindungabbruch
while true; do
  ssh -N -L 5173:localhost:5173 -L 8001:localhost:8001 benutzer@remote-server
  sleep 5
done
```