# 🧠 Ideen Ingest Channel

SSH-zugänglicher Drag-and-Drop Eingangskanal für GBrain Ideen-System mit automatischem Import und Graph-Visualisierung.

## Features

- 📁 **Drag-and-Drop Interface**: Einfacher Datei-Upload per Drag & Drop
- 🔄 **Automatischer GBrain Import**: Neue Dateien werden automatisch in GBrain importiert
- 🔍 **Ideen-Suche**: Volltextsuche im Ideen-System
- 📊 **Graph-Visualisierung**: Interaktive Visualisierung von Ideen-Beziehungen
- 🌐 **SSH-Zugriff**: Sicherer Remote-Zugriff via SSH-Tunnel
- 🎨 **Modernes UI**: React-basierte Benutzeroberfläche
- ⚡ **FastAPI Backend**: Performantes Python-Backend

## Tech Stack

### Backend
- **FastAPI**: Modernes, schnelles Web-Framework
- **Python 3.12+**: Aktuelle Python-Version
- **GBrain CLI**: Integration mit dem GBrain Wissenssystem
- **Uvicorn**: ASGI-Server

### Frontend
- **React 18**: UI-Framework
- **TypeScript**: Type-Sicherheit
- **Vite**: Schnelles Build-Tool
- **React Flow**: Graph-Visualisierung
- **React Dropzone**: Drag-and-Drop Funktionalität
- **Axios**: HTTP-Client

## Projektstruktur

```
ideen-ingest-channel/
├── backend/                 # FastAPI Backend
│   ├── src/
│   │   ├── api/            # API Router
│   │   ├── services/       # GBrain Integration
│   │   └── core/           # Konfiguration
│   ├── pyproject.toml      # Python-Abhängigkeiten
│   └── venv/               # Virtuelle Umgebung
├── frontend/               # React Frontend
│   ├── src/
│   │   ├── App.tsx         # Hauptkomponente
│   │   ├── GraphVisualization.tsx  # Graph-Komponente
│   │   └── App.css         # Styles
│   ├── package.json        # Node-Abhängigkeiten
│   └── vite.config.ts      # Vite-Konfiguration
├── deploy.sh              # Deployment-Script
├── build-prod.sh          # Production-Build-Script
├── SSH-DEPLOYMENT.md      # SSH/Deployment-Dokumentation
└── README.md              # Diese Datei
```

## Quick Start

### Voraussetzungen

- Python 3.12+
- Node.js 18+
- GBrain CLI installiert und konfiguriert
- pnpm oder npm

### Installation

1. **Backend installieren**:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

2. **Frontend installieren**:
```bash
cd frontend
npm install
```

### Entwicklung starten

**Option 1: Beide Services gleichzeitig**:
```bash
./deploy.sh
```

**Option 2: Manuelles Starten**:
```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate
uvicorn src.main:app --host 0.0.0.0 --port 8001

# Terminal 2: Frontend
cd frontend
npm run dev
```

### Zugriff

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8001
- **API Dokumentation**: http://localhost:8001/docs

## Nutzung

### Dateien hochladen

1. Wähle die Phase (Seed, Sprout, Growth, Flower, Harvest)
2. Ziehe Dateien (.md, .txt, .json, .yaml, .yml) per Drag & Drop in den Upload-Bereich
3. Dateien werden automatisch in GBrain importiert

### Ideen durchsuchen

1. Gib Suchbegriff in das Suchfeld ein
2. Klicke auf "Search" oder drücke Enter
3. Ergebnisse werden als Liste angezeigt

### Graph-Visualisierung

1. Klicke auf "Graph" Button oben rechts
2. Interaktive Graph-Ansicht mit Ideen als Knoten
3. Klicke auf Knoten für Details

### SSH-Zugriff

Siehe `SSH-DEPLOYMENT.md` für detaillierte Anleitungen.

## API Endpunkte

### Ingest API
- `POST /api/ingest/upload` - Datei hochladen
- `GET /api/ingest/files` - Alle Dateien auflisten
- `DELETE /api/ingest/files/{filename}` - Datei löschen

### Ideas API
- `GET /api/ideas/search` - Ideen suchen
- `GET /api/ideas/list` - Alle Ideen auflisten
- `GET /api/ideas/{slug}` - Idee details
- `GET /api/ideas/{slug}/graph` - Graph für Idee
- `POST /api/ideas/link` - Ideen verlinken

### Status API
- `GET /api/status/health` - Health Check
- `GET /api/status/system` - System-Status

## Konfiguration

### Backend Konfiguration

Erstelle `.env` Datei im `backend/` Verzeichnis:

```env
# App Settings
APP_NAME=Ideen Ingest Channel
APP_VERSION=0.1.0
DEBUG=true

# Server Settings
HOST=0.0.0.0
PORT=8001

# File Upload Settings
UPLOAD_DIR=/home/dyai/ideen-growth-system/seeds
MAX_FILE_SIZE=10485760

# GBrain Settings
GBRAIN_SOURCE=ideas
GBRAIN_COMMAND=gbrain
```

### Frontend Konfiguration

Die API-URL kann in `src/App.tsx` angepasst werden:

```typescript
const API_BASE_URL = '/api' // Entwicklung (mit Proxy)
// const API_BASE_URL = 'http://your-server:8001/api' // Produktion
```

## Production Deployment

### Backend als Systemd Service

```bash
# Service installieren
sudo cp ideen-ingest-backend.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable ideen-ingest-backend
sudo systemctl start ideen-ingest-backend
```

### Frontend Build

```bash
./build-prod.sh
```

Die gebauten Dateien liegen in `frontend/dist/` und können mit nginx oder einem anderen Web-Server ausgeliefert werden.

## Development

### Backend Development

```bash
cd backend
source venv/bin/activate
uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload
```

### Frontend Development

```bash
cd frontend
npm run dev
```

### Code Style

- **Backend**: Black, isort
- **Frontend**: ESLint, Prettier (konfiguriert in Vite)

## Troubleshooting

### Backend startet nicht

```bash
# Logs prüfen
sudo journalctl -u ideen-ingest-backend -n 50

# Port prüfen
lsof -i :8001

# Manuelles Testen
cd backend
source venv/bin/activate
uvicorn src.main:app --host 0.0.0.0 --port 8001
```

### Frontend kann nicht verbinden

- Backend läuft: `curl http://localhost:8001/api/status/health`
- CORS-Einstellungen prüfen
- Firewall-Regeln prüfen
- API-URL Konfiguration prüfen

## Contributing

1. Fork das Repository
2. Feature-Branch erstellen (`git checkout -b feature/AmazingFeature`)
3. Changes committen (`git commit -m 'Add some AmazingFeature'`)
4. zum Branch pushen (`git push origin feature/AmazingFeature`)
5. Pull Request öffnen

## License

MIT License - siehe LICENSE Datei für Details.

## Support

Bei Problemen oder Fragen:
- GitHub Issues: https://github.com/DYAI2025/ideen-ingest-channel/issues
- Dokumentation: Siehe `SSH-DEPLOYMENT.md`

## Acknowledgments

- GBrain für das Wissenssystem
- FastAPI für das Backend-Framework
- React für das Frontend-Framework
- React Flow für die Graph-Visualisierung