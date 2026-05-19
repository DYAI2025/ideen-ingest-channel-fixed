#!/bin/bash

# Docker Container finden, der Port 80 nutzt

echo "🔍 Suche Docker Container auf Port 80..."
echo ""

# Container mit Port 80 finden
docker ps --format "table {{.ID}}\t{{.Names}}\t{{.Ports}}" | grep ":80"

echo ""
echo "📋 Alle Container:"
docker ps -a

echo ""
echo "🔧 Um den Container zu stoppen:"
echo "   docker stop <CONTAINER_ID>"
echo ""
echo "🔄 Um Port zu ändern (im docker-compose.yml oder docker run):"
echo "   -p 8080:80 statt -p 80:80"