# SSH Access and Deployment Guide

## Overview
The Ideen Ingest Channel can be accessed via SSH tunnel for secure remote access.

## Quick Start

### Local Development
```bash
# Start both backend and frontend
./deploy.sh
```

### Backend Only (Production Mode)
```bash
cd backend
source venv/bin/activate
uvicorn src.main:app --host 0.0.0.0 --port 8001
```

### Frontend Only
```bash
cd frontend
npm run dev
```

## SSH Tunnel Setup

### From Remote Machine
```bash
# Forward local port 5173 to remote frontend
ssh -L 5173:localhost:5173 user@remote-server

# Forward local port 8001 to remote backend API
ssh -L 8001:localhost:8001 user@remote-server

# Forward both ports at once
ssh -L 5173:localhost:5173 -L 8001:localhost:8001 user@remote-server
```

### Access via SSH Tunnel
Once the SSH tunnel is established:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8001
- API Documentation: http://localhost:8001/docs

## Systemd Service Installation

### Install Backend Service
```bash
# Copy service file
sudo cp ideen-ingest-backend.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable ideen-ingest-backend

# Start service
sudo systemctl start ideen-ingest-backend

# Check status
sudo systemctl status ideen-ingest-backend
```

### Service Management
```bash
# Start service
sudo systemctl start ideen-ingest-backend

# Stop service
sudo systemctl stop ideen-ingest-backend

# Restart service
sudo systemctl restart ideen-ingest-backend

# View logs
sudo journalctl -u ideen-ingest-backend -f

# Check status
sudo systemctl status ideen-ingest-backend
```

## Production Deployment

### Backend Configuration
Create `.env` file in backend directory:
```env
# App Settings
APP_NAME=Ideen Ingest Channel
APP_VERSION=0.1.0
DEBUG=false

# Server Settings
HOST=0.0.0.0
PORT=8001

# File Upload Settings
UPLOAD_DIR=/home/dyai/ideen-growth-system/seeds
MAX_FILE_SIZE=10485760

# GBrain Settings
GBRAIN_SOURCE=ideas
GBRAIN_COMMAND=gbrain

# SSH Settings
SSH_ENABLED=true
SSH_PORT=2222
```

### Frontend Configuration
Update API URL in production build:
```typescript
// In App.tsx, change for production:
const API_BASE_URL = '/api' // Uses proxy in dev
// For production, use actual backend URL:
const API_BASE_URL = 'http://your-server:8001/api'
```

### Build Frontend for Production
```bash
cd frontend
npm run build
```

Serve the built files with nginx or another web server.

## Firewall Configuration

### Allow Required Ports
```bash
# Allow frontend port (if running separately)
sudo ufw allow 5173/tcp

# Allow backend API port
sudo ufw allow 8001/tcp

# Allow SSH (if not already allowed)
sudo ufw allow 22/tcp
```

## Security Considerations

1. **SSH Access**: Use key-based authentication instead of passwords
2. **Firewall**: Only expose necessary ports
3. **HTTPS**: Use reverse proxy (nginx) with SSL for production
4. **Authentication**: Add authentication to the API endpoints
5. **Rate Limiting**: Implement rate limiting on API endpoints

## Troubleshooting

### Backend Won't Start
```bash
# Check logs
sudo journalctl -u ideen-ingest-backend -n 50

# Check if port is in use
sudo lsof -i :8001

# Test backend manually
cd backend
source venv/bin/activate
uvicorn src.main:app --host 0.0.0.0 --port 8001
```

### Frontend Can't Connect to Backend
- Check if backend is running: `curl http://localhost:8001/api/status/health`
- Verify CORS settings in backend
- Check firewall rules
- Verify API URL configuration

### SSH Tunnel Issues
- Verify SSH connection: `ssh user@server`
- Check if ports are already in use: `lsof -i :5173`
- Use `-v` flag for verbose SSH output: `ssh -v -L 5173:localhost:5173 user@server`

## Monitoring

### Health Checks
```bash
# Backend health
curl http://localhost:8001/api/status/health

# System status
curl http://localhost:8001/api/status/system
```

### Logs
```bash
# Backend service logs
sudo journalctl -u ideen-ingest-backend -f

# Application logs
tail -f /var/log/ideen-ingest/app.log
```