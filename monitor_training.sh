#!/bin/bash

echo "Monitoring system resources during YOLO training..."
echo "Press Ctrl+C to stop monitoring"
echo ""

while true; do
    echo "=== $(date) ==="
    
    # Memory usage
    echo "Memory Usage:"
    free -h | grep -E "Mem|Swap"
    
    # GPU and system stats using tegrastats (Jetson-specific)
    echo ""
    echo "GPU and System Stats (tegrastats):"
    timeout 2 tegrastats | tail -1 | sed 's/^/  /'
    
    # CPU usage
    echo ""
    echo "CPU Usage:"
    top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1
    
    # Check if darknet process is running
    if pgrep -f "darknet" > /dev/null; then
        echo ""
        echo "Darknet process is running (PID: $(pgrep -f darknet))"
        
        # Show darknet process details
        echo "Darknet process details:"
        ps aux | grep darknet | grep -v grep | awk '{print "  PID:", $2, "CPU:", $3"%", "MEM:", $4"%", "CMD:", $11}'
    else
        echo ""
        echo "WARNING: Darknet process not found!"
    fi
    
    echo ""
    echo "----------------------------------------"
    sleep 5
done 