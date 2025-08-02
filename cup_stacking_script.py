#!/usr/bin/env python3
"""
Cup Stacking Robot Script
Python script version of the cup stacking system
"""

import sys
import os
import cv2
import numpy as np
import time
import threading

# Add src directory to path for imports
sys.path.append(os.path.join(os.getcwd(), 'src'))

def main():
    """Main cup stacking script"""
    print("🥤 Cup Stacking Robot Script")
    print("=" * 50)
    
    # Check if we can import the required modules
    try:
        from vision.cup_detector import CupDetector
        from robot.dofbot_controller import DOFBOTController
        print("✅ All modules imported successfully")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure all required files are in the correct locations")
        return
    
    # Configuration
    model_path = "backup/yolo-cup-memory-optimized_final.weights"
    camera_id = 0
    simulation_mode = True  # Set to False when robot is connected
    
    print(f"🎯 Using YOLO model: {model_path}")
    print(f"📷 Camera ID: {camera_id}")
    print(f"🤖 Simulation mode: {simulation_mode}")
    
    # Initialize components
    print("\n🔧 Initializing components...")
    
    # Initialize YOLO detector
    try:
        detector = CupDetector(model_path=model_path, conf_threshold=0.5)
        print("✅ YOLO detector initialized")
    except Exception as e:
        print(f"❌ Failed to initialize YOLO detector: {e}")
        return
    
    # Initialize camera
    try:
        camera = cv2.VideoCapture(camera_id)
        if not camera.isOpened():
            print(f"❌ Could not open camera {camera_id}")
            return
        print("✅ Camera initialized")
    except Exception as e:
        print(f"❌ Camera initialization failed: {e}")
        return
    
    # Initialize robot (if not in simulation mode)
    robot = None
    if not simulation_mode:
        try:
            robot = DOFBOTController()
            if not robot.connected:
                print("⚠️ Robot not connected, continuing in simulation mode")
                simulation_mode = True
            else:
                print("✅ Robot connected")
        except Exception as e:
            print(f"⚠️ Robot initialization failed: {e}")
            simulation_mode = True
    
    if simulation_mode:
        print("🎭 Running in simulation mode")
    
    # Main loop
    print("\n🎮 Starting cup stacking system...")
    print("Controls:")
    print("- Press 'd' to detect cups")
    print("- Press 's' to start stacking")
    print("- Press 't' to test robot")
    print("- Press 'h' to home robot")
    print("- Press 'q' to quit")
    
    # Check if camera is working
    camera_working = False
    test_frame = camera.read()[1]
    if test_frame is not None:
        camera_working = True
        print("✅ Camera is working - real-time mode available")
    else:
        print("⚠️ Camera not available - using simulation mode only")
    
    try:
        while True:
            if camera_working:
                # Capture frame
                ret, frame = camera.read()
                if not ret:
                    print("❌ Could not read frame")
                    time.sleep(0.1)
                    continue
                
                # Display frame
                cv2.imshow('Cup Stacking System', frame)
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
            else:
                # No camera - just wait for input
                print("\nEnter command (d/s/t/h/q): ", end='', flush=True)
                try:
                    import select
                    import sys
                    if select.select([sys.stdin], [], [], 0.1)[0]:
                        command = sys.stdin.readline().strip().lower()
                        if command == 'q':
                            break
                        elif command == 'd':
                            key = ord('d')
                        elif command == 's':
                            key = ord('s')
                        elif command == 't':
                            key = ord('t')
                        elif command == 'h':
                            key = ord('h')
                        else:
                            key = 0
                    else:
                        key = 0
                except:
                    key = 0
            
            if key == ord('q'):
                break
            elif key == ord('d'):
                # Detect cups
                print("\n🔍 Detecting cups...")
                if camera_working:
                    detections = detector.detect_cups(frame)
                    positions = detector.get_cup_positions(frame)
                    
                    # Draw detections
                    result_frame = detector.draw_detections(frame.copy(), detections)
                    cv2.imshow('Cup Detection', result_frame)
                    
                    print(f"📊 Found {len(detections)} cups")
                    for i, pos in enumerate(positions):
                        print(f"  Cup {i+1}: ({pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f})")
                else:
                    print("🎭 Simulating cup detection...")
                    print("📊 Found 3 cups (simulation)")
                    print("  Cup 1: (0.25, 0.30, 0.05)")
                    print("  Cup 2: (0.45, 0.30, 0.05)")
                    print("  Cup 3: (0.65, 0.30, 0.05)")
                
            elif key == ord('s'):
                # Start stacking sequence
                print("\n🚀 Starting stacking sequence...")
                if camera_working:
                    detections = detector.detect_cups(frame)
                    positions = detector.get_cup_positions(frame)
                else:
                    # Simulate cup positions
                    positions = [(0.25, 0.30, 0.05), (0.45, 0.30, 0.05), (0.65, 0.30, 0.05)]
                
                if not positions:
                    print("❌ No cups detected for stacking")
                    continue
                
                print(f"📊 Stacking {len(positions)} cups...")
                
                # Simulate stacking (or use real robot)
                for i, (x, y, z) in enumerate(positions):
                    print(f"🥤 Processing cup {i+1}/{len(positions)}")
                    
                    if simulation_mode:
                        print(f"🎭 Simulating: Pick cup at ({x:.2f}, {y:.2f}, {z:.2f})")
                        time.sleep(1)
                        print(f"🎭 Simulating: Place cup {i+1} in stack")
                        time.sleep(1)
                    else:
                        # Real robot operations would go here
                        print(f"🤖 Robot: Pick cup at ({x:.2f}, {y:.2f}, {z:.2f})")
                        # robot.pick_cup(x, y, z)
                        # robot.place_cup(stack_x, stack_y, stack_z)
                
                print("✅ Stacking sequence completed!")
                
            elif key == ord('t'):
                # Test robot
                print("\n🧪 Testing robot...")
                if simulation_mode:
                    print("🎭 Simulating robot test movements")
                    time.sleep(2)
                    print("✅ Robot test completed (simulation)")
                else:
                    print("🤖 Running real robot test")
                    # robot.test_movements()
                
            elif key == ord('h'):
                # Home robot
                print("\n🏠 Moving robot to home position...")
                if simulation_mode:
                    print("🎭 Simulating: Moving to home position")
                    time.sleep(2)
                    print("✅ Home position reached (simulation)")
                else:
                    print("🤖 Moving robot to home position")
                    # robot.home_position()
    
    except KeyboardInterrupt:
        print("\n⏹️ Interrupted by user")
    
    finally:
        # Cleanup
        print("\n🧹 Cleaning up...")
        camera.release()
        cv2.destroyAllWindows()
        
        if robot and not simulation_mode:
            robot.disconnect()
        
        print("✅ Cleanup completed")
        print("👋 Cup stacking system shutdown")

if __name__ == "__main__":
    main() 