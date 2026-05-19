#!/bin/bash

# Railway Setup Script

echo "🚀 Railway Setup für Ideen-Ingest-Channel"

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

# Projekt initialisieren
echo "📁 Initialisiere Railway Projekt..."
cd /home/dyai/ideen-ingest-channel

# Backend deployen
echo "🚀 Deploye Backend..."
cd backend
railway init
railway up

# Frontend deployen  
echo "🚀 Deploye Frontend..."
cd ../frontend
railway init
railway up

echo ""
echo "✅ Railway Setup abgeschlossen!"
echo ""
echo "🌐 Deine URLs:"
echo "   Backend: railway backend domain"
echo "   Frontend: railway frontend domain"
echo ""
echo "🔧 Custom Domain konfigurieren:"
echo "   railway domain add vision.dyai.cloud"