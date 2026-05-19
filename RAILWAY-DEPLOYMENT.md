# Railway Deployment Guide (Backend + Frontend)

## Zielbild
- **2 Railway Services** im selben Projekt:
  - `ideen-backend` aus `backend/`
  - `ideen-frontend` aus `frontend/`
- Frontend ruft Backend über `VITE_API_URL` auf.

## 1) Backend Service
1. In Railway: **New Service** → GitHub Repo verbinden.
2. **Root Directory** auf `backend` setzen.
3. Railway nutzt `backend/railway.json`.

### Erwartete Runtime
- Start Command: `python -m uvicorn src.main:app --host 0.0.0.0 --port $PORT`
- Healthcheck: `/health`

### Backend Variablen (Minimum)
- `UPLOAD_DIR=/tmp/uploads`
- `GBRAIN_COMMAND=gbrain`
- optional: `GBRAIN_SOURCE=ideas`

> Hinweis: Auf Railway ist das Dateisystem ephemer. Für persistente Daten externes Storage nutzen.

## 2) Frontend Service
1. In Railway: **New Service** → gleiches Repo.
2. **Root Directory** auf `frontend` setzen.
3. Railway nutzt `frontend/railway.json`.

### Erwartete Runtime
- Build: `npm ci && npm run build`
- Start: `npm run preview -- --host 0.0.0.0 --port ${PORT:-3000}`
- Healthcheck: `/`

### Frontend Variablen (Pflicht)
- `VITE_API_URL=https://<backend-service>.up.railway.app`

## 3) CORS / API Routing
Das Frontend verwendet in Production die URL aus `VITE_API_URL`.
Wenn `VITE_API_URL` fehlt, fällt die App auf `/api` zurück (nur sinnvoll mit Reverse Proxy).

## 4) Deployment Checkliste
- Backend `/health` liefert HTTP 200.
- Frontend lädt ohne Build-Fehler.
- Browser-Netzwerk: Requests gehen an `https://<backend>/api/...`.
- Backend Logs zeigen erfolgreiche Requests.

## 5) CLI Alternative
```bash
railway login

# Backend
cd backend
railway up

# Frontend
cd ../frontend
railway up
```
