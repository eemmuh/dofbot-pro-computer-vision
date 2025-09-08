#!/bin/bash

# Ultra Memory Optimized YOLO Training for Jetson Orin NX
# This script includes memory cleanup and optimized settings

echo "🧠 Starting Ultra Memory Optimized YOLO Training..."
echo "📱 Target: Jetson Orin NX 8GB RAM"
echo ""

# Memory cleanup before training
echo "🧹 Cleaning up memory..."
sudo sync
echo 3 | sudo tee /proc/sys/vm/drop_caches > /dev/null
sudo swapoff -a && sudo swapon -a

# Check available memory
echo "📊 Memory Status:"
free -h
echo ""

# Kill any existing darknet processes
echo "🔄 Stopping any existing darknet processes..."
pkill -f darknet || true
sleep 2

# Set environment variables for memory optimization
export CUDA_VISIBLE_DEVICES=0
export CUDA_LAUNCH_BLOCKING=1

# Start training with ultra-memory config
echo "🚀 Starting training with ultra-memory configuration..."
cd /home/jetson/cup-stacking-project

# Use the new ultra-memory config
./darknet/darknet detector train \
    data/cup.data \
    cfg/yolo-cup-ultra-memory.cfg \
    darknet/yolov4.weights \
    -dont_show \
    -clear \
    -map

echo "✅ Training completed!"
