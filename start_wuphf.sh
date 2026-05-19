#!/bin/bash
# Simple WUPHF startup script
# Auto-recovery is handled by autonomy_watchdog.py

echo "[STARTUP] Starting WUPHF..."

# Verify configuration
if [ ! -f ~/.wuphf/config.json ]; then
    echo "[STARTUP] ERROR: Configuration file not found!"
    exit 1
fi

# Start WUPHF directly
./wuphf