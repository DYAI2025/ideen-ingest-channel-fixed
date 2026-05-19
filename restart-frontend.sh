#!/bin/bash

# Frontend Dev-Server neustarten mit neuer Konfiguration

echo "🔄 Starte Frontend Dev-Server neu..."

# Prozess beenden
kill 625054

# Warten bis Prozess beendet ist
sleep 2

# In das Frontend-Verzeichnis wechseln und neu starten
cd /home/dyai/ideen-ingest-channel/frontend
nohup npm run dev > /tmp/frontend-dev.log 2>&1 &

echo "✅ Frontend Dev-Server neu gestartet"
echo ""
echo "📊 Prüfe ob er läuft:"
sleep 3
ps aux | grep "vite" | grep -v grep

echo ""
echo "📝 Logs: tail -f /tmp/frontend-dev.log"