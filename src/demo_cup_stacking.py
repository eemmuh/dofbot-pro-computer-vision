#!/usr/bin/env python3
"""
Simple DOFBOT Cup Stacking Demo
Demonstrates basic robot movement and gripper control
"""

import cv2
import time
from robot.dofbot_controller import DOFBOTController

def main():
    print("🤖 DOFBOT Cup Stacking Demo")
    print("=" * 40)
    
    # Initialize camera
    print("📷 Initializing camera...")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Error: Could not open camera")
        return

    # Initialize DOFBOT controller
    print("🔌 Initializing DOFBOT controller...")
    robot = DOFBOTController()
    
    if not robot.connect():
        print("❌ Error: Could not connect to DOFBOT")
        print("Please check:")
        print("1. DOFBOT is connected via USB")
        print("2. DOFBOT is powered on")
        print("3. DOFBOT is in operation mode")
        return

    print("✅ DOFBOT connected successfully!")
    print("🎯 Demo Ready!")
    print("Controls:")
    print("- Press 'h' to move to home position")
    print("- Press 'o' to open gripper")
    print("- Press 'c' to close gripper")
    print("- Press '1' to move to position 1")
    print("- Press '2' to move to position 2")
    print("- Press '3' to move to position 3")
    print("- Press 'q' to quit")

    # Define some demo positions
    demo_positions = {
        '1': {1: 45, 2: 90, 3: 90, 4: 90, 5: 90, 6: 30},   # Left position
        '2': {1: 90, 2: 90, 3: 90, 4: 90, 5: 90, 6: 30},   # Center position
        '3': {1: 135, 2: 90, 3: 90, 4: 90, 5: 90, 6: 30},  # Right position
    }

    try:
        while True:
            # Capture frame
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame")
                break

            # Display frame
            cv2.imshow('DOFBOT Cup Stacking Demo', frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('h'):
                print("🏠 Moving to home position...")
                robot.home_position()
            elif key == ord('o'):
                print("🤏 Opening gripper...")
                robot.open_gripper()
            elif key == ord('c'):
                print("🤏 Closing gripper...")
                robot.close_gripper()
            elif key in demo_positions:
                print(f"🎯 Moving to position {key}...")
                robot.move_to_position(demo_positions[key])
                time.sleep(1)

    finally:
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        robot.disconnect()
        print("✅ Demo complete!")

if __name__ == "__main__":
    main() 