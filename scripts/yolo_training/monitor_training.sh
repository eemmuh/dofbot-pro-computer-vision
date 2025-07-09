#!/bin/bash

echo "🎯 Monitoring YOLO Training Progress for Jetson Orin NX"
echo "Press Ctrl+C to stop monitoring"
echo ""

while true; do
    echo "=== $(date) ==="
    
    # Check if training is still running
    if pgrep -f "darknet.*train" > /dev/null; then
        echo "✅ Training is running"
        
        # Show recent log entries with training progress
        if [ -f "training.log" ]; then
            echo "📊 Recent training log (last 15 lines):"
            tail -15 training.log | grep -E "(iteration|avg loss|mAP|saving)" || echo "No recent training data yet..."
        fi
        
        # Show system resources (Jetson-compatible)
        echo "💻 System resources:"
        echo "CPU Load: $(uptime | awk -F'load average:' '{print $2}')"
        echo "Memory: $(free -h | grep Mem | awk '{print $3"/"$2 " (" $3/$2*100 "%)"}')"
        
        # Show darknet process details
        echo "🔧 Darknet process:"
        ps aux | grep darknet | grep -v grep | awk '{print "  PID:", $2, "CPU:", $3"%", "MEM:", $4"%", "Runtime:", $10}'
        
    else
        echo "❌ Training process not found"
        break
    fi
    
    echo ""
    echo "⏳ Waiting 30 seconds for next update..."
    echo "----------------------------------------"
    sleep 30
done

echo "Training monitoring stopped" 