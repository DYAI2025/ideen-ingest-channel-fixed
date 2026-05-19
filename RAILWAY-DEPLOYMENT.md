# Railway Deployment Guide

## 🚀 Warum Railway?

- ✅ **Automatisches HTTPS** - keine SSL Zertifikate nötig
- ✅ **Keine Port-Konflikte** - Railway handled alles
- ✅ **Einfaches Scaling** - ein Klick für mehr Performance
- ✅ **Built-in Datenbanken** - PostgreSQL, Redis, etc.
- ✅ **Custom Domains** - vision.dyai.cloud einfach konfigurieren
- ✅ **Git Integration** - deployt automatisch bei Code Changes

## 📋 Voraussetzungen

1. Railway Account: https://railway.app/
2. Railway CLI installiert:
```bash
npm install -g @railway/cli
```

## 🔧 Setup Schritte

### 1. Railway CLI installieren
```bash
npm install -g @railway/cli
```

### 2. Einloggen
```bash
railway login
```

### 3. Backend deployen
```bash
cd /home/dyai/ideen-ingest-channel/backend
railway init
railway up
```

### 4. Frontend deployen
```bash
cd /home/dyai/ideen-ingest-channel/frontend  
railway init
railway up
```

### 5. Domain konfigurieren
```bash
# Backend Domain
railway domain add vision.dyai.cloud

# Frontend Domain (optional)
railway domain add app.vision.dyai.cloud
```

## 🌐 Alternative: Railway UI nutzen

Wenn du die CLI nicht nutzen willst:

1. Gehe zu https://railway.app/
2. "New Project" → "Deploy from GitHub repo"
3. Wähle dein Repo (oder lege es an)
4. Railway erkennt automatisch die Konfiguration
5. Füge Custom Domains hinzu im Project Settings

## 📁 Projekt Struktur für Railway

```
/home/dyai/ideen-ingest-channel/
├── backend/
│   ├── railway.json          # Railway Konfiguration
│   ├── nixpacks.toml         # Build Konfiguration
│   ├── main.py               # FastAPI App
│   └── requirements.txt      # Python Dependencies
├── frontend/
│   ├── railway.json          # Railway Konfiguration  
│   ├── nixpacks.toml         # Build Konfiguration
│   ├── package.json          # Node Dependencies
│   └── vite.config.ts        # Vite Konfiguration
```

## 🔧 Environment Variables

In Railway Project Settings → Variables:

**Backend:**
```
PORT=8001
GBRAIN_PATH=/data/gbrain
```

**Frontend:**
```
VITE_API_URL=https://backend-deployment.railway.app
```

## 🎯 Nächste Schritte

1. Railway CLI installieren: `npm install -g @railway/cli`
2. Einloggen: `railway login`
3. Backend deployen: `cd backend && railway up`
4. Frontend deployen: `cd frontend && railway up`
5. Domain konfigurieren: `railway domain add vision.dyai.cloud`

## 💡 Vorteile gegenüber lokalem Setup

- Keine Port-Konflikte (80, 8080, etc.)
- Keine Firewall Konfiguration nötig
- Kein SSH/Router Setup nötig
- Automatisches HTTPS
- Einfaches Scaling
- Built-in Monitoring
- Git-based Deployments

## 🚀 Schnellstart

Führe einfach aus:
```bash
cd /home/dyai/ideen-ingest-channel
./setup-railway.sh
```