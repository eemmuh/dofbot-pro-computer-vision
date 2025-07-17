#!/bin/bash

# Memory-optimized YOLO training script for Jetson Orin
# This script monitors system resources and uses optimized settings

echo "=== Memory-Optimized YOLO Training for Jetson Orin ==="
echo "Starting training with memory-optimized configuration..."

# Check if we have the required files
if [ ! -f "cfg/yolo-cup-memory-optimized.cfg" ]; then
    echo "Error: Memory-optimized config file not found!"
    exit 1
fi

if [ ! -f "data/cup.data" ]; then
    echo "Error: cup.data file not found!"
    exit 1
fi

if [ ! -f "yolov4.weights" ]; then
    echo "Error: yolov4.weights file not found!"
    exit 1
fi

# Function to monitor system resources
monitor_resources() {
    while true; do
        echo "=== System Resources ==="
        echo "GPU Memory:"
        if command -v nvidia-smi &> /dev/null; then
            nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader,nounits | while read line; do
                echo "  $line"
            done
        else
            echo "  nvidia-smi not available"
        fi
        
        echo "System Memory:"
        free -h | grep -E "Mem|Swap"
        
        echo "CPU Usage:"
        top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1
        
        echo "========================"
        sleep 30
    done
}

# Start resource monitoring in background
monitor_resources &
MONITOR_PID=$!

# Set environment variables for better memory management
export CUDA_VISIBLE_DEVICES=0
export CUDA_LAUNCH_BLOCKING=1

# Clear GPU memory before starting
echo "Clearing GPU memory..."
sudo fuser -v /dev/nvidia* 2>/dev/null | xargs -I {} kill -9 {} 2>/dev/null || true

# Start training with memory-optimized configuration
echo "Starting YOLO training with memory-optimized settings..."
echo "Configuration: batch=2, subdivisions=4, width=256, height=256"
echo "Effective batch size: 0.5 (increased from 0.25)"

cd darknet
./darknet detector train ../data/cup.data ../cfg/yolo-cup-memory-optimized.cfg ../yolov4.weights

# Clean up
kill $MONITOR_PID 2>/dev/null || true
echo "Training completed or interrupted." 