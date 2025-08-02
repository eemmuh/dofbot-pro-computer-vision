#!/usr/bin/env python3
"""
Fixed DOFBOT Cup Stacking Demo using Arm_Lib
Demonstrates basic robot movement and gripper control
"""

# Fix smbus import issue BEFORE importing Arm_Lib
import sys
try:
    import smbus2 as smbus
    sys.modules['smbus'] = smbus
    print("✅ smbus compatibility fixed")
except ImportError:
    print("❌ smbus2 not available")
    sys.exit(1)

import cv2
import time
import threading

# Now import Arm_Lib after fixing smbus
try:
    from Arm_Lib import Arm_Device
    print("✅ Arm_Lib imported successfully")
except Exception as e:
    print(f"❌ Error importing Arm_Lib: {e}")
    sys.exit(1)

def main():
    print("🤖 DOFBOT Cup Stacking Demo with Arm_Lib (Fixed)")
    print("=" * 60)
    
    # Initialize camera
    print("📷 Initializing camera...")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Error: Could not open camera")
        print("Continuing without camera...")
        camera_available = False
    else:
        camera_available = True
        print("✅ Camera initialized")

    # Initialize DOFBOT controller with Arm_Lib
    print("🔌 Initializing DOFBOT controller with Arm_Lib...")
    try:
        robot = Arm_Device()
        time.sleep(0.1)  # Small delay for initialization
        print("✅ DOFBOT connected successfully with Arm_Lib!")
    except Exception as e:
        print(f"❌ Error: Could not connect to DOFBOT: {e}")
        print("Please check:")
        print("1. DOFBOT is connected via USB")
        print("2. DOFBOT is powered on")
        print("3. DOFBOT is in operation mode")
        return

    # Move to home position on startup
    print("🏠 Moving to home position...")
    robot.Arm_serial_servo_write6(90, 90, 90, 90, 90, 30, 3000)
    time.sleep(3)
    print("✅ Home position reached!")

    print("\n🎯 Demo Ready!")
    print("Controls:")
    print("- Press 'h' to move to home position")
    print("- Press 'o' to open gripper")
    print("- Press 'c' to close gripper")
    print("- Press '1' to move to position 1 (left)")
    print("- Press '2' to move to position 2 (center)")
    print("- Press '3' to move to position 3 (right)")
    print("- Press '4' to move to position 4 (up)")
    print("- Press '5' to move to position 5 (down)")
    print("- Press 'g' to test gripper sequence")
    print("- Press 'q' to quit")
    print("\n💡 TIP: Make sure the camera window is focused for keyboard input!")
    print("   Or use the console input method below.")

    # Define some demo positions (servo angles)
    demo_positions = {
        '1': [45, 90, 90, 90, 90, 30],   # Left position
        '2': [90, 90, 90, 90, 90, 30],   # Center position  
        '3': [135, 90, 90, 90, 90, 30],  # Right position
        '4': [90, 45, 90, 90, 90, 30],   # Up position
        '5': [90, 135, 90, 90, 90, 30],  # Down position
    }

    # Function to handle robot commands
    def execute_command(command):
        if command == 'h':
            print("🏠 Moving to home position...")
            robot.Arm_serial_servo_write6(90, 90, 90, 90, 90, 30, 3000)
            time.sleep(3)
            print("✅ Home position reached!")
        elif command == 'o':
            print("🤏 Opening gripper...")
            robot.Arm_serial_servo_write(6, 180, 1000)
            time.sleep(1)
            print("✅ Gripper opened!")
        elif command == 'c':
            print("🤏 Closing gripper...")
            robot.Arm_serial_servo_write(6, 30, 1000)
            time.sleep(1)
            print("✅ Gripper closed!")
        elif command == 'g':
            print("🤏 Testing gripper sequence...")
            robot.Arm_serial_servo_write(6, 180, 1000)  # Open
            time.sleep(1)
            robot.Arm_serial_servo_write(6, 30, 1000)   # Close
            time.sleep(1)
            print("✅ Gripper sequence completed!")
        elif command in demo_positions:
            print(f"🎯 Moving to position {command}...")
            angles = demo_positions[command]
            robot.Arm_serial_servo_write6(
                angles[0], angles[1], angles[2], 
                angles[3], angles[4], angles[5], 
                2000
            )
            time.sleep(2)
            print(f"✅ Position {command} reached!")
        else:
            print(f"❌ Unknown command: {command}")

    # Console input thread
    def console_input():
        while True:
            try:
                command = input("\nEnter command (h/o/c/1/2/3/4/5/g/q): ").strip().lower()
                if command == 'q':
                    print("🛑 Quitting...")
                    break
                elif command in ['h', 'o', 'c', '1', '2', '3', '4', '5', 'g']:
                    execute_command(command)
                else:
                    print("❌ Invalid command. Valid commands: h, o, c, 1, 2, 3, 4, 5, g, q")
            except KeyboardInterrupt:
                print("\n🛑 Interrupted by user")
                break
            except EOFError:
                break

    # Start console input thread
    console_thread = threading.Thread(target=console_input, daemon=True)
    console_thread.start()

    try:
        if camera_available:
            print("\n📹 Camera window opened. You can use keyboard input on the window OR console input below.")
            
            while True:
                # Capture frame
                ret, frame = cap.read()
                if not ret:
                    print("❌ Error: Could not read frame")
                    break

                # Display frame
                cv2.imshow('DOFBOT Cup Stacking Demo - Arm_Lib', frame)
                
                # Handle key presses from camera window
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("🛑 Quitting...")
                    break
                elif key in [ord('h'), ord('o'), ord('c'), ord('1'), ord('2'), ord('3'), ord('4'), ord('5'), ord('g')]:
                    command = chr(key)
                    execute_command(command)
        else:
            print("\n📝 Using console input only (no camera)")
            # Wait for console thread to finish
            console_thread.join()

    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    finally:
        # Cleanup
        if camera_available:
            cap.release()
            cv2.destroyAllWindows()
        
        # Return to home position before closing
        print("🏠 Returning to home position...")
        robot.Arm_serial_servo_write6(90, 90, 90, 90, 90, 30, 3000)
        time.sleep(3)
        
        print("✅ Demo complete!")

if __name__ == "__main__":
    main() 