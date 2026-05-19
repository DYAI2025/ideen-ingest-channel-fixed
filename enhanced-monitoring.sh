#!/bin/bash
# Enhanced Monitoring System - Tracks tasks, outputs, and agent performance

OUTPUT_DIR="$HOME/wuphf-agency-output"
TASK_DIR="$HOME/.wuphf/wiki/tasks"
LOG_DIR="$HOME/wuphf-agency-output/monitoring"
ALERT_LOG="$LOG_DIR/alerts.log"
PERFORMANCE_LOG="$LOG_DIR/performance.log"

echo "🔍 ENHANCED MONITORING SYSTEM"
echo "Monitoring: Outputs, Tasks, Agent Performance"
echo "Press Ctrl+C to stop"
echo ""

# Create log directories
mkdir -p "$LOG_DIR"

# Initialize counters
total_outputs=0
total_tasks=0
completed_tasks=0
failed_tasks=0

echo "📊 MONITORING ACTIVE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

while true; do
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # 1. Output Monitoring
    current_outputs=$(find "$OUTPUT_DIR" -type f | wc -l)
    if [ $current_outputs -gt $total_outputs ]; then
        new_outputs=$((current_outputs - total_outputs))
        echo "[$timestamp] 🎉 NEW OUTPUTS DETECTED: $new_outputs new file(s)"
        
        # List new files
        find "$OUTPUT_DIR" -type f -mmin -1 | while read file; do
            echo "   📄 $file"
        done
        
        total_outputs=$current_outputs
        
        # Log to performance log
        echo "[$timestamp] OUTPUTS: Total=$total_outputs, New=$new_outputs" >> "$PERFORMANCE_LOG"
    fi
    
    # 2. Task Monitoring
    current_tasks=$(find "$TASK_DIR" -name "*.md" | wc -l)
    if [ $current_tasks -ne $total_tasks ]; then
        task_change=$((current_tasks - total_tasks))
        if [ $task_change -gt 0 ]; then
            echo "[$timestamp] 📋 NEW TASKS: $task_change new task(s)"
        fi
        total_tasks=$current_tasks
    fi
    
    # 3. Agent Performance Monitoring
    # Check WUPHF agent activity
    agent_activity=$(ps aux | grep -E "wuphf" | grep -v grep | wc -l)
    if [ "$agent_activity" -lt 3 ]; then
        echo "[$timestamp] ⚠️  ALERT: Low agent activity ($agent_activity processes)" >> "$ALERT_LOG"
        echo "[$timestamp] ⚠️  WARNING: Only $agent_activity WUPHF processes active"
    fi
    
    # 4. Google Search Violation Detection
    google_attempts=$(grep -r "google:search" ~/.wuphf/office/tasks/ 2>/dev/null | wc -l)
    if [ $google_attempts -gt 0 ]; then
        echo "[$timestamp] 🚨 ALERT: $google_attempts Google search attempts detected" >> "$ALERT_LOG"
        echo "[$timestamp] 🚨 CRITICAL: $google_attempts Google search violations!"
    fi
    
    # 5. System Health Check
    wuphf_running=$(pgrep -f wuphf | wc -l)
    orchestrator_running=$(pgrep -f orchestrator | wc -l)
    watchdog_running=$(pgrep -f autonomy_watchdog | wc -l)
    
    if [ $wuphf_running -eq 0 ]; then
        echo "[$timestamp] 🚨 CRITICAL: WUPHF not running!" >> "$ALERT_LOG"
        echo "[$timestamp] 🚨 EMERGENCY: WUPHF process stopped"
    fi
    
    if [ $orchestrator_running -eq 0 ]; then
        echo "[$timestamp] ⚠️  WARNING: Orchestrator not running" >> "$ALERT_LOG"
        echo "[$timestamp] ⚠️  WARNING: Orchestrator process stopped"
    fi
    
    # 6. Periodic Summary (every 5 minutes)
    current_minute=$(date +%M)
    if [ $((current_minute % 5)) -eq 0 ]; then
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "📊 SYSTEM SUMMARY - $timestamp"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "📁 Outputs: $total_outputs files"
        echo "📋 Tasks: $total_tasks tasks"
        echo "🤖 Agents: $agent_activity active"
        echo "🔍 Google violations: $google_attempts"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
    fi
    
    # Sleep for 30 seconds
    sleep 30
done