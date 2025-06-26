#!/usr/bin/env python3
"""
DOFBOT Connection and Movement Test
This script tests the connection to the DOFBOT robot and makes it move.
"""

import time
import serial
from src.robot.dofbot_controller import DOFBOTController

def test_serial_ports():
    """Test available serial ports to find DOFBOT."""
    import glob
    
    print("Scanning for available serial ports...")
    
    # Check different types of serial ports
    port_patterns = [
        '/dev/ttyUSB*',    # USB serial devices
        '/dev/ttyACM*',    # USB CDC ACM devices
        '/dev/ttyS*',      # Standard serial ports
        '/dev/ttyTHS*',    # Tegra hardware serial
        '/dev/ttyAMA*'     # ARM serial
    ]
    
    all_ports = []
    for pattern in port_patterns:
        ports = glob.glob(pattern)
        if ports:
            print(f"Found {pattern}: {ports}")
            all_ports.extend(ports)
    
    if not all_ports:
        print("No serial ports found!")
        return None
    
    print(f"\nAll available serial ports: {all_ports}")
    return all_ports

def test_dofbot_connection():
    """Test DOFBOT connection and basic communication."""
    print("="*50)
    print("DOFBOT CONNECTION TEST")
    print("="*50)
    
    # Test available ports
    ports = test_serial_ports()
    if not ports:
        print("\n❌ No serial ports found!")
        print("Please check:")
        print("1. DOFBOT is connected via USB")
        print("2. USB cable is working")
        print("3. DOFBOT is powered on")
        return False
    
    # Try to connect to DOFBOT on different ports
    print(f"\nAttempting to connect to DOFBOT...")
    
    for port in ports:
        print(f"\nTrying {port}...")
        robot = DOFBOTController(port=port)
        
        try:
            if robot.connect():
                print(f"✅ SUCCESS: Connected to DOFBOT on {port}!")
                print(f"Port: {robot.port}")
                print(f"Baudrate: {robot.baudrate}")
                return robot
            else:
                print(f"❌ Failed to connect on {port}")
        except Exception as e:
            print(f"❌ Error connecting to {port}: {e}")
    
    print("\n❌ FAILED: Could not connect to any port")
    return False

def test_basic_movement(robot):
    """Test basic robot movement."""
    print("\n" + "="*50)
    print("BASIC MOVEMENT TEST")
    print("="*50)
    
    if not robot:
        print("❌ No robot connection available")
        return False
    
    print("Testing basic movement commands...")
    print("WARNING: Make sure the robot arm has clear space around it!")
    
    # Test gripper
    print("\n1. Testing gripper...")
    try:
        print("   Opening gripper...")
        robot.open_gripper()
        time.sleep(2)
        
        print("   Closing gripper...")
        robot.close_gripper()
        time.sleep(2)
        print("   ✅ Gripper test completed")
    except Exception as e:
        print(f"   ❌ Gripper test failed: {e}")
    
    # Test position movement (if implemented)
    print("\n2. Testing position movement...")
    try:
        # Move to a safe position (adjust coordinates as needed)
        print("   Moving to position (100, 100, 50)...")
        robot.move_to_position(100, 100, 50)
        time.sleep(3)
        
        print("   Moving to position (200, 100, 50)...")
        robot.move_to_position(200, 100, 50)
        time.sleep(3)
        
        print("   ✅ Position movement test completed")
    except Exception as e:
        print(f"   ❌ Position movement test failed: {e}")
        print("   (This is normal if move_to_position is not implemented yet)")
    
    return True

def test_manual_control(robot):
    """Test manual control mode."""
    print("\n" + "="*50)
    print("MANUAL CONTROL TEST")
    print("="*50)
    
    if not robot:
        return False
    
    print("Manual control test - you can control the robot manually")
    print("Commands:")
    print("  'o' - Open gripper")
    print("  'c' - Close gripper")
    print("  'h' - Home position")
    print("  'q' - Quit")
    print("  '1-6' - Move individual joints (if implemented)")
    
    try:
        while True:
            command = input("\nEnter command (o/c/h/q/1-6): ").strip().lower()
            
            if command == 'q':
                break
            elif command == 'o':
                print("Opening gripper...")
                robot.open_gripper()
            elif command == 'c':
                print("Closing gripper...")
                robot.close_gripper()
            elif command == 'h':
                print("Moving to home position...")
                robot.home_position()
            elif command in ['1', '2', '3', '4', '5', '6']:
                angle = input(f"Enter angle for joint {command} (degrees): ").strip()
                try:
                    angle = float(angle)
                    robot.move_joint(int(command), angle)
                except ValueError:
                    print("Invalid angle")
            else:
                print("Invalid command")
                
    except KeyboardInterrupt:
        print("\nManual control stopped")
    
    return True

def check_dofbot_setup():
    """Check DOFBOT setup and provide guidance."""
    print("\n" + "="*50)
    print("DOFBOT SETUP CHECK")
    print("="*50)
    
    print("To connect DOFBOT to your Jetson:")
    print("\n1. Hardware Setup:")
    print("   - Connect DOFBOT to Jetson via USB cable")
    print("   - Power on DOFBOT (usually has a power switch)")
    print("   - Make sure DOFBOT is in normal operation mode")
    
    print("\n2. Software Setup:")
    print("   - DOFBOT should appear as a USB serial device")
    print("   - Common ports: /dev/ttyUSB0, /dev/ttyACM0")
    print("   - Baudrate is typically 115200")
    
    print("\n3. Troubleshooting:")
    print("   - Check USB cable connection")
    print("   - Try different USB ports")
    print("   - Restart DOFBOT if needed")
    print("   - Check if DOFBOT firmware is working")
    
    print("\n4. Alternative Connection Methods:")
    print("   - Some DOFBOTs use Bluetooth")
    print("   - Some use WiFi modules")
    print("   - Check DOFBOT documentation for your model")

def main():
    """Main test function."""
    print("DOFBOT Robot Test Suite")
    print("="*50)
    
    # Check setup first
    check_dofbot_setup()
    
    # Test connection
    robot = test_dofbot_connection()
    
    if not robot:
        print("\n❌ CONNECTION TEST FAILED")
        print("\nPossible solutions:")
        print("1. Connect DOFBOT via USB and power it on")
        print("2. Check if DOFBOT appears in 'lsusb' output")
        print("3. Try running: sudo usermod -a -G dialout $USER")
        print("4. Reboot and try again")
        print("5. Check DOFBOT documentation for connection details")
        return
    
    # Test basic movement
    test_basic_movement(robot)
    
    # Ask for manual control test
    print("\n" + "="*50)
    choice = input("Do you want to test manual control? (y/n): ").strip().lower()
    
    if choice == 'y':
        test_manual_control(robot)
    
    # Cleanup
    robot.disconnect()
    print("\n✅ DOFBOT test completed successfully!")
    print("You can now proceed with YOLO training.")

if __name__ == "__main__":
    main() 