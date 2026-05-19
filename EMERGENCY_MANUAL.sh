#!/bin/bash
# ⚠️ EMERGENCY MANUAL INTERVENTION SCRIPT
# USE ONLY AS ABSOLUTE LAST RESORT WHEN ALL AUTONOMOUS SYSTEMS FAIL
# This script bypasses all autonomous systems and requires manual confirmation

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║          ⚠️  EMERGENCY MANUAL INTERVENTION SYSTEM ⚠️                ║"
echo "║                                                              ║"
echo "║  This script bypasses ALL autonomous systems and should only      ║"
echo "║  be used when ALL automatic recovery mechanisms have failed.      ║"
echo "║                                                              ║"
echo "║  NORMAL OPERATION: Let the autonomy_watchdog.py handle everything  ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check for escalation tickets
ESCALATION_DIR="$HOME/.wuphf/escalations"
if [ -d "$ESCALATION_DIR" ]; then
    ESCALATION_COUNT=$(ls -1 "$ESCALATION_DIR"/*.md 2>/dev/null | wc -l)
    if [ "$ESCALATION_COUNT" -gt 0 ]; then
        echo "📋 Found $ESCALATION_COUNT pending escalation tickets:"
        ls -lt "$ESCALATION_DIR"/*.md | head -5
        echo ""
    fi
fi

# Force stop all autonomous systems
echo "🛑 STOPPING ALL AUTONOMOUS SYSTEMS..."
pkill -9 -f autonomy_watchdog.py
pkill -9 -f orchestrator.py
pkill -9 -f wuphf

echo "✅ All autonomous systems stopped"
echo ""

# System status check
echo "📊 CURRENT SYSTEM STATUS:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# WUPHF status
if pgrep -f wuphf > /dev/null; then
    echo "✓ WUPHF: RUNNING"
else
    echo "✗ WUPHF: STOPPED"
fi

# Ollama status
if pgrep -f ollama > /dev/null; then
    echo "✓ Ollama: RUNNING"
else
    echo "✗ Ollama: STOPPED"
fi

# Orchestrator status
if [ -f ".env" ] && grep -q "OPENROUTER_API_KEY=" .env; then
    echo "✓ Orchestrator: CONFIGURED"
else
    echo "✗ Orchestrator: NOT CONFIGURED"
fi

# Task queue status
if [ -d "$HOME/.wuphf/wiki/tasks" ]; then
    TASK_COUNT=$(ls -1 "$HOME/.wuphf/wiki/tasks"/*.md 2>/dev/null | wc -l)
    echo "✓ Task Queue: $TASK_COUNT pending tasks"
else
    echo "✗ Task Queue: NOT ACCESSIBLE"
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Manual intervention options
echo "🔧 MANUAL INTERVENTION OPTIONS:"
echo ""
echo "1. FORCE START WUPHF"
echo "2. FORCE START ORCHESTRATOR CAMPAIGN"
echo "3. VIEW ESCALATION TICKETS"
echo "4. VIEW SYSTEM LOGS"
echo "5. RESTART AUTONOMOUS SYSTEMS"
echo "6. EXIT EMERGENCY MODE"
echo ""

read -p "Select option (1-6): " choice

case $choice in
    1)
        echo "🚀 FORCE STARTING WUPHF..."
        ./wuphf
        ;;
    2)
        echo "🚀 FORCE STARTING ORCHESTRATOR..."
        python3 orchestrator.py launch_campaign
        ;;
    3)
        echo "📋 VIEWING ESCALATION TICKETS..."
        if [ -d "$ESCALATION_DIR" ]; then
            for ticket in "$ESCALATION_DIR"/*.md; do
                echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                cat "$ticket"
                echo ""
            done
        else
            echo "No escalation tickets found"
        fi
        ;;
    4)
        echo "📋 VIEWING SYSTEM LOGS..."
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "📋 Watchdog Log:"
        tail -20 ~/.wuphf/watchdog.log
        echo ""
        echo "📋 WUPHF Crash Log:"
        tail -10 ~/.wuphf/wuphf_crash.log
        ;;
    5)
        echo "🔄 RESTARTING AUTONOMOUS SYSTEMS..."
        echo "Starting autonomy_watchdog in background..."
        nohup python3 autonomy_watchdog.py > ~/.wuphf/watchdog_output.log 2>&1 &
        echo "✅ Autonomous systems restarted"
        echo "Monitor with: tail -f ~/.wuphf/watchdog_output.log"
        ;;
    6)
        echo "🚪 EXITING EMERGENCY MODE"
        echo "Note: Autonomous systems will NOT restart automatically"
        echo "To restore autonomy: python3 autonomy_watchdog.py"
        ;;
    *)
        echo "❌ Invalid option"
        exit 1
        ;;
esac