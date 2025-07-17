#!/usr/bin/env python3
"""
Debug script to see what darknet is actually outputting
"""
import cv2
import subprocess
import tempfile
import os

def debug_darknet_output():
    print("🔍 Debugging Darknet Output")
    print("=" * 40)
    
    # Initialize camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Error: Could not open camera")
        return
    
    # Capture a frame
    ret, frame = cap.read()
    if not ret:
        print("❌ Error: Could not read frame")
        return
    
    cap.release()
    
    # Save frame to temporary file
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
        cv2.imwrite(tmp_file.name, frame)
        temp_image_path = tmp_file.name
    
    try:
        # Run Darknet detection with verbose output
        model_path = "backup/yolo-cup-memory-optimized_final.weights"
        config_path = "cfg/yolo-cup-memory-optimized.cfg"
        
        # Use absolute paths
        abs_model_path = os.path.abspath(model_path)
        abs_config_path = os.path.abspath(config_path)
        
        cmd = [
            "./darknet", "detect", abs_config_path, abs_model_path, temp_image_path,
            "-thresh", "0.3"
        ]
        
        # Change to darknet directory for execution
        darknet_dir = "darknet"
        result = subprocess.run(cmd, cwd=darknet_dir, capture_output=True, text=True)
        
        print("📊 Darknet Return Code:", result.returncode)
        print("\n📤 STDOUT:")
        print("=" * 40)
        print(result.stdout)
        print("\n📤 STDERR:")
        print("=" * 40)
        print(result.stderr)
        
        # Parse the output line by line
        print("\n🔍 Parsing Output Lines:")
        print("=" * 40)
        lines = result.stdout.strip().split('\n')
        for i, line in enumerate(lines):
            print(f"Line {i+1}: '{line}'")
            if ':' in line and '%' in line:
                print(f"  -> Potential detection: {line}")
            elif line.strip() and all(c.isdigit() or c in '.-' for c in line.strip()):
                print(f"  -> Potential coordinates: {line}")
        
    finally:
        # Clean up temporary file
        if os.path.exists(temp_image_path):
            os.unlink(temp_image_path)
    
    print("\n✅ Debug completed!")

if __name__ == "__main__":
    debug_darknet_output() 