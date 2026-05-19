# Railway UI Deployment Guide

## 🚀 Railway UI Deployment - Schritt für Schritt

### 1. Railway Account öffnen
Gehe zu: https://railway.app/

Wenn du noch kein Konto hast:
- "Sign up" → GitHub Login (empfohlen) oder Email
- Bestätige deine Email-Adresse

### 2. Neues Projekt erstellen
1. Klicke auf "New Project" (oben rechts)
2. Wähle "Deploy from GitHub repo"

### 3. GitHub Repository auswählen
1. Railway wird nach GitHub-Zugriff fragen → "Authorize Railway"
2. Suche nach: `ideen-ingest-channel`
3. Wähle das Repository von `DYAI2025`
4. Klicke auf "Import"

### 4. Railway konfiguriert automatisch
Railway erkennt automatisch:
- ✅ Python Backend (FastAPI)
- ✅ Frontend (Vite + React)
- ✅ Build-Konfigurationen (railway.json, nixpacks.toml)
- ✅ Start-Kommandos

### 5. Deployment überwachen
1. Du siehst zwei Services:
   - `backend` (Python FastAPI)
   - `frontend` (Vite + React)

2. Warte bis beide "Healthy" anzeigen (grüner Haken)
   - Das dauert meist 2-5 Minuten
   - Du kannst die Logs in Echtzeit sehen

### 6. URLs erhalten
Sobald deployt ist, bekommst du Railway-URLs:
- Backend: `https://<backend-name>.up.railway.app`
- Frontend: `https://<frontend-name>.up.railway.app`

### 7. Custom Domain konfigurieren
Für `vision.dyai.cloud`:

#### Backend Domain:
1. Klicke auf den `backend` Service
2. Gehe zu "Settings" → "Networking"
3. Klicke auf "Add Domain"
4. Trage ein: `vision.dyai.cloud`
5. Railway zeigt DNS-Records an

#### Frontend Domain (optional):
1. Klicke auf den `frontend` Service  
2. Gehe zu "Settings" → "Networking"
3. Klicke auf "Add Domain"
4. Trage ein: `app.vision.dyai.cloud` (oder andere Subdomain)

### 8. DNS bei Cloudflare aktualisieren
Gehe zu https://dash.cloudflare.com/:

#### Für Backend (vision.dyai.cloud):
```
Typ: CNAME
Name: vision
Inhalt: <backend-name>.up.railway.app
Proxy: ✅ Proxied (Orange Wolke)
TTL: Auto
```

#### Für Frontend (app.vision.dyai.cloud):
```
Typ: CNAME
Name: app
Inhalt: <frontend-name>.up.railway.app  
Proxy: ✅ Proxied (Orange Wolke)
TTL: Auto
```

### 9. SSL automatisch konfigurieren
- Railway erstellt automatisch SSL-Zertifikate
- Cloudflare übernimmt HTTPS-Terminierung
- Keine manuellen SSL-Zertifikate nötig!

### 10. Testen
Nach 2-5 Minuten DNS-Propagation:
- https://vision.dyai.cloud (Backend)
- https://app.vision.dyai.cloud (Frontend)

## 🔧 Fehlersuche

### Deployment schlägt fehl:
1. Klicke auf den Service → "Logs" Tab
2. Prüfe die Error-Messages
3. Meistens sind es Dependencies oder Build-Fehler

### Domain nicht erreichbar:
1. Prüfe DNS-Propagation: `dig vision.dyai.cloud`
2. Prüfe Cloudflare DNS-Settings
3. Warte 5-10 Minuten auf DNS-Cache

### Logs ansehen:
- Klicke auf Service → "Logs" Tab
- Echtzeit-Logs vom Build und Runtime
- Sehr nützlich für Debugging

## 📊 Railway Dashboard Features

### Monitoring:
- CPU, Memory, Network Usage
- Request Counts
- Error Rates
- Response Times

### Scaling:
- Klicke auf Service → "Settings"
- "Scaling" → CPU/RAM anpassen
- Automatische Scaling-Optionen

### Environment Variables:
- Service → "Variables"
- API Keys, Datenbank-URLs etc.
- Sicher und verschlüsselt

## 🎯 Tipps

1. **Erst Backend, dann Frontend** - Frontend braucht Backend-URL
2. **Logs immer prüfen** bei Problemen
3. **DNS Propagation abwarten** (5-10 Min)
4. **Railway Free Tier** - $5/Monat Guthaben, meist genug für Development

## 🚀 Nach dem Deployment

Sobald alles läuft:
1. **Backend API testen**: https://vision.dyai.cloud/docs
2. **Frontend testen**: https://app.vision.dyai.cloud
3. **Monitoring prüfen**: Railway Dashboard
4. **Logs überwachen**: Erste Stunden prüfen

## 💡 Kosten

- Railway Free Tier: $5/Monat Guthaben
- Backend + Frontend: meist ~$2-3/Monat
- Kann bei Bedarf skaliert werden

---

**Viel Erfolg beim Deployment! 🚀**