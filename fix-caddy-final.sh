#!/bin/bash

# Finaler Caddy Fix: Docker-Caddy stoppen, System-Caddy starten

echo "🔧 Stoppe Docker-Caddy..."
docker stop 8115bd16d807

echo "✅ Docker-Caddy gestoppt"
echo ""

echo "🚀 Starte system-localen Caddy..."
sudo systemctl restart caddy
sleep 3

echo "📊 Caddy Status:"
sudo systemctl status caddy --no-pager

echo ""
echo "🌐 Teste lokal:"
echo "   curl http://localhost:80"
echo ""
echo "🌐 Nach Cloudflare Propagation (2-5 Min):"
echo "   https://vision.dyai.cloud"
echo "   https://kanban.vision.dyai.cloud"
echo "   https://graph.vision.dyai.cloud"
echo "   https://obsidian.vision.dyai.cloud"