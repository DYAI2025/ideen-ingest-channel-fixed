# Cloudflare Setup Anleitung

## Schritt 1: Cloudflare DNS konfigurieren

Gehe zu https://dash.cloudflare.com/ und konfiguriere folgende DNS Records:

### Hauptdomain
```
Typ: A
Name: vision.dyai.cloud
Inhalt: 93.128.152.173
Proxy: ✅ (Orange Wolke) - Aktiviert
TTL: Auto
```

### Subdomains (CNAME)
```
Typ: CNAME
Name: kanban.vision.dyai.cloud
Inhalt: vision.dyai.cloud
Proxy: ✅ (Orange Wolke) - Aktiviert
TTL: Auto
```

```
Typ: CNAME
Name: graph.vision.dyai.cloud
Inhalt: vision.dyai.cloud
Proxy: ✅ (Orange Wolke) - Aktiviert
TTL: Auto
```

```
Typ: CNAME
Name: obsidian.vision.dyai.cloud
Inhalt: vision.dyai.cloud
Proxy: ✅ (Orange Wolke) - Aktiviert
TTL: Auto
```

### SSL/TLS Einstellung
1. Gehe zu SSL/TLS → Overview
2. Setze Mode auf **"Full"** oder **"Full (strict)"**

## Schritt 2: Script ausführen

Sobald Cloudflare DNS konfiguriert ist:

```bash
cd /home/dyai/ideen-ingest-channel
./setup-cloudflare.sh
```

Das Script wird:
- ✅ Caddy für HTTP konfigurieren (Cloudflare macht SSL)
- ✅ Caddy validieren und starten
- ✅ Firewall Ports öffnen
- ✅ SSH aktivieren

## Schritt 3: Testen

Nach 2-5 Minuten Wartezeit (für Cloudflare Cache):
- https://vision.dyai.cloud
- https://kanban.vision.dyai.cloud
- https://graph.vision.dyai.cloud
- https://obsidian.vision.dyai.cloud

## Fehlersuche

Falls Probleme:
```bash
# Caddy Status
sudo systemctl status caddy

# Caddy Logs
sudo journalctl -u caddy -f

# DNS prüfen
dig vision.dyai.cloud

# Ports prüfen
sudo netstat -tulpn | grep -E ':(80|443)'
```