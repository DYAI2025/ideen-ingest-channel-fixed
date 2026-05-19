#!/bin/bash
# Main launch script for fully autonomous agency
# Starts all systems with redundant failover mechanisms

echo """
╔════════════════════════════════════════════════════════════════╗
║              🚀 AUTONOMOUS AGENCY LAUNCHER 🚀                   ║
║                                                              ║
║  Starting fully autonomous agency with:                           ║
║  ✓ Cloud Orchestrator (OpenRouter Freemium)                      ║
║  ✓ Local Executors (WUPHF + Ollama)                              ║
║  ✓ Redundant Failover Systems                                     ║
║  ✓ Auto-Recovery Watchdog                                        ║
║  ✓ Zero Manual Intervention Required                             ║
║                                                              ║
║  Emergency manual intervention: ./EMERGENCY_MANUAL.sh          ║
╚════════════════════════════════━━━━━━━━━━━━━━━━━━━━━━━━━━═════╝
"""

# Change to script directory
cd "$(dirname "$0")"

# Pre-flight checks
echo "🔍 PRE-FLIGHT CHECKS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check .env file
if [ ! -f ".env" ]; then
    echo "❌ ERROR: .env file not found!"
    echo "Please create .env with OPENROUTER_API_KEY"
    exit 1
fi

# Check API key
if ! grep -q "OPENROUTER_API_KEY=sk-or" .env; then
    echo "❌ ERROR: OPENROUTER_API_KEY not configured in .env"
    echo "Please edit .env and add your OpenRouter API key"
    exit 1
fi

# Check Ollama
if ! pgrep -f ollama > /dev/null; then
    echo "⚠️  WARNING: Ollama not running"
    echo "Start with: ollama serve"
    echo "Proceeding anyway..."
fi

echo "✅ Pre-flight checks passed"
echo ""

# Start WUPHF with auto-recovery
echo "🚀 STARTING WUPHF"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Kill any existing WUPHF
pkill -9 -f wuphf 2>/dev/null
sleep 2

# Start WUPHF in background
nohup ./wuphf > ~/.wuphf/wuphf_auto.log 2>&1 &
WUPHF_PID=$!

echo "✅ WUPHF started (PID: $WUPHF_PID)"
echo "   Monitor: tail -f ~/.wuphf/wuphf_auto.log"
echo ""

# Wait for WUPHF to be ready
echo "⏳ Waiting for WUPHF to be ready..."
for i in {1..30}; do
    if pgrep -f wuphf > /dev/null; then
        echo "✅ WUPHF process detected"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ ERROR: WUPHF failed to start within 30 seconds"
        echo "Check logs: tail -20 ~/.wuphf/wuphf_auto.log"
        exit 1
    fi
    sleep 1
done

# Additional wait for WUPHF to fully initialize
echo "⏳ Waiting for WUPHF initialization..."
sleep 5

echo "✅ WUPHF ready"
echo ""

# Start initial campaign
echo "🎯 LAUNCHING INITIAL CAMPAIGN"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

python3 orchestrator.py launch_campaign &
ORCHESTRATOR_PID=$!

echo "✅ Initial campaign launched"
echo ""

# Start autonomy watchdog
echo "🛡️ STARTING AUTONOMY WATCHDOG"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

nohup python3 autonomy_watchdog.py > ~/.wuphf/watchdog_output.log 2>&1 &
WATCHDOG_PID=$!

echo "✅ Autonomy watchdog started (PID: $WATCHDOG_PID)"
echo "   Monitor: tail -f ~/.wuphf/watchdog_output.log"
echo ""

# System status
echo "📊 SYSTEM STATUS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "WUPHF: RUNNING (PID: $WUPHF_PID) - Auto-recovery by watchdog"
echo "Orchestrator: RUNNING (PID: $ORCHESTRATOR_PID)"
echo "Watchdog: RUNNING (PID: $WATCHDOG_PID)"
echo ""

# Access information
echo "🌐 ACCESS POINTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Web UI: http://127.0.0.1:7891"
echo "Broker API: http://127.0.0.1:7890"
echo ""

# Monitoring commands
echo "📈 MONITORING COMMANDS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Watch tasks: watch -n 5 'ls -lh ~/.wuphf/wiki/tasks/'"
echo "Watchdog log: tail -f ~/.wuphf/watchdog_output.log"
echo "WUPHF log: tail -f ~/.wuphf/wuphf_auto.log"
echo ""

# Emergency info
echo "⚠️  EMERGENCY (ONLY if absolutely necessary)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Emergency manual: ./EMERGENCY_MANUAL.sh"
echo ""

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║              🎉 AUTONOMOUS AGENCY FULLY OPERATIONAL 🎉            ║"
echo "║                                                              ║"
echo "║  The system is now running FULLY AUTONOMOUS with:              ║"
echo "║  ✓ Cloud intelligence for strategic decisions                    ║"
echo "║  ✓ Local execution for all tasks                                 ║"
echo "║  ✓ Redundant failover systems                                   ║"
║  ✓ Auto-recovery on any failure                                 ║
echo "║                                                              ║"
echo "║  Monitor via Web UI: http://127.0.0.1:7891                       ║"
echo "║  Emergency only: ./EMERGENCY_MANUAL.sh                            ║"
echo "╚════════════════════════════════════════════════════════════════╝"

# Save PIDs for cleanup
echo "$WUPHF_PID" > ~/.wuphf/autonomous_pids.pid
echo "$ORCHESTRATOR_PID" >> ~/.wuphf/autonomous_pids.pid
echo "$WATCHDOG_PID" >> ~/.wuphf/autonomous_pids.pid

echo ""
echo "💡 TIP: The system will run autonomously. Just monitor the Web UI!"
echo "   New campaigns will be triggered automatically every hour."