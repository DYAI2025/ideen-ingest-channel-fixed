#!/bin/bash

# Production build script
# Builds frontend for production deployment

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

echo "🏗️  Building Ideen Ingest Channel for production..."

# Build frontend
echo "📦 Building frontend..."
cd "$FRONTEND_DIR"
npm run build

echo "✅ Frontend built successfully!"
echo "📁 Build output: $FRONTEND_DIR/dist"
echo ""
echo "To deploy:"
echo "1. Copy backend/ to your server"
echo "2. Copy frontend/dist/ to your web server"
echo "3. Configure nginx or another web server to serve the frontend"
echo "4. Start the backend service using systemd or the deployment script"