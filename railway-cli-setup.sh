#!/bin/bash

# Railway CLI Setup und Deployment

echo "🚀 Railway CLI Setup für Ideen-Ingest-Channel"

# Railway CLI installieren
if ! command -v railway &> /dev/null; then
    echo "📦 Installiere Railway CLI..."
    npm install -g @railway/cli
else
    echo "✅ Railway CLI bereits installiert"
fi

# Railway einloggen
echo "🔐 Railway Login..."
railway login

# Im ideen-ingest-channel Verzeichnis
cd /home/dyai/ideen-ingest-channel

# Projekt initialisieren
echo "📁 Initialisiere Railway Projekt..."
railway init

# Deployen
echo "🚀 Deploye zu Railway..."
railway up

echo ""
echo "✅ Deployment gestartet!"
echo ""
echo "📊 Überwache das Deployment im Railway Dashboard:"
echo "   https://railway.app/"
echo ""
echo "🌐 Nach erfolgreichem Deployment:"
echo "   1. Custom Domain hinzufügen: vision.dyai.cloud"
echo "   2. Cloudflare DNS aktualisieren"