#!/bin/bash
# Monitor output directory for new agent deliverables

OUTPUT_DIR="$HOME/wuphf-agency-output"
LOG_FILE="$HOME/wuphf-agency-output/monitor.log"

echo "🔍 Monitoring WUPHF Agent Outputs..."
echo "Output Directory: $OUTPUT_DIR"
echo "Press Ctrl+C to stop"
echo ""

# Get initial file count
initial_count=$(find "$OUTPUT_DIR" -type f | wc -l)
echo "Initial file count: $initial_count"
echo ""

# Monitor for changes
while true; do
    current_count=$(find "$OUTPUT_DIR" -type f | wc -l)

    if [ $current_count -gt $initial_count ]; then
        echo "🎉 NEW OUTPUT DETECTED! ($(date '+%Y-%m-%d %H:%M:%S'))"
        echo "File count changed from $initial_count to $current_count"
        echo ""

        # Find new files
        find "$OUTPUT_DIR" -type f -mmin -1 | while read file; do
            echo "📄 NEW FILE: $file"
            echo "   Size: $(du -h "$file" | cut -f1)"
            echo "   Type: $(file -b "$file")"
            echo ""
        done

        # Update initial count
        initial_count=$current_count

        # Log to file
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] New outputs detected. Total files: $current_count" >> "$LOG_FILE"
    fi

    # Check every 10 seconds
    sleep 10
done