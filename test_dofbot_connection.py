#!/usr/bin/env python3
"""
Simple DOFBOT Connection Test
Run this script to test if your DOFBOT is properly connected.
"""

import time
from src.robot.dofbot_controller import DOFBOTController

def main():
    print("DOFBOT Connection Test")
    print("=" * 40)
    print()
    print("Before running this test:")
    print("1. Make sure DOFBOT is connected via USB")
    print("2. Make sure DOFBOT is powered on")
    print("3. Make sure DOFBOT is in operation mode (not programming mode)")
    print()
    
    input("Press Enter when DOFBOT is connected and ready...")
    
    print("\nTesting DOFBOT connection...")
    
    # Create controller with auto-detection
    robot = DOFBOTController()
    
    # Try to connect
    if robot.connect():
        print("\n✅ SUCCESS: DOFBOT is connected and responding!")
        print(f"   Port: {robot.port}")
        print(f"   Baudrate: {robot.baudrate}")
        
        # Test basic commands
        print("\nTesting basic commands...")
        
        print("Testing gripper...")
        robot.open_gripper()
        time.sleep(2)
        robot.close_gripper()
        time.sleep(2)
        
        print("Testing home position...")
        robot.home_position()
        time.sleep(3)
        
        print("\n✅ All tests passed! Your DOFBOT is working correctly.")
        print("You can now proceed with the cup stacking project.")
        
        robot.disconnect()
        
    else:
        print("\n❌ FAILED: Could not connect to DOFBOT")
        print()
        print("Troubleshooting steps:")
        print("1. Check USB connection")
        print("2. Make sure DOFBOT is powered on")
        print("3. Try a different USB cable")
        print("4. Try a different USB port")
        print("5. Check if DOFBOT appears in 'lsusb' output")
        print("6. Restart DOFBOT if needed")
        print()
        print("Run 'lsusb' to see if DOFBOT is detected:")
        import subprocess
        result = subprocess.run(['lsusb'], capture_output=True, text=True)
        print(result.stdout)

if __name__ == "__main__":
    main() 