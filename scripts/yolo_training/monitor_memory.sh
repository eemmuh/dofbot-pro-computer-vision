#!/bin/bash

# Simple memory monitoring script for Jetson Orin
# Run this in a separate terminal to monitor resources during training

echo "=== Jetson Orin Memory Monitor ==="
echo "Press Ctrl+C to stop monitoring"
echo ""

while true; do
    clear
    echo "=== $(date) ==="
    echo ""
    
    echo "GPU Memory Usage:"
    nvidia-smi --query-gpu=index,name,memory.used,memory.total,memory.free,utilization.gpu --format=csv,noheader,nounits | while IFS=, read -r index name used total free util; do
        echo "  GPU $index ($name): ${used}MB / ${total}MB (${free}MB free) - ${util}% util"
    done
    
    echo ""
    echo "System Memory:"
    free -h
    
    echo ""
    echo "CPU Usage:"
    top -bn1 | grep "Cpu(s)" | awk '{print "  CPU: " $2}'
    
    echo ""
    echo "Processes using GPU:"
    nvidia-smi pmon -c 1 | head -10
    
    sleep 5
done 