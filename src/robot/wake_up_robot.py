#!/usr/bin/env python3
"""
Wake Up Robot - Try different initialization sequences
"""

import smbus2 as smbus
import time

def wake_up_robot():
    print("🤖 Wake Up Robot Test")
    print("=" * 40)
    print("💡 Trying different wake-up sequences...")
    print("🎯 The robot might need a specific initialization sequence.")
    print()
    
    try:
        i2c = smbus.SMBus(0)
        print("✅ Connected to I2C bus 0")
        
        # Different wake-up sequences
        sequences = [
            # Format: (register, [data], description)
            (0x00, [0x01, 0x00, 0x00, 0x00], "Wake Up 1"),
            (0x00, [0x02, 0x00, 0x00, 0x00], "Wake Up 2"),
            (0x00, [0x03, 0x00, 0x00, 0x00], "Wake Up 3"),
            (0x10, [0x01, 0x00, 0x00, 0x00], "Enable Control 1"),
            (0x10, [0x02, 0x00, 0x00, 0x00], "Enable Control 2"),
            (0x20, [0x01, 0x00, 0x00, 0x00], "Enable Remote 1"),
            (0x20, [0x02, 0x00, 0x00, 0x00], "Enable Remote 2"),
            (0x30, [0x01, 0x00, 0x00, 0x00], "Enable Computer 1"),
            (0x30, [0x02, 0x00, 0x00, 0x00], "Enable Computer 2"),
        ]
        
        for register, data, description in sequences:
            print(f"\n🧪 Testing: {description}")
            try:
                i2c.write_i2c_block_data(0x50, register, data)
                time.sleep(1)
                print(f"  ✅ Sequence sent")
                
                # Test computer command
                print(f"  🧪 Testing computer command...")
                test_cmd = [0x01, 0x01, 0x01, 0x90, 0x64]  # Move servo 1 to 90°
                i2c.write_i2c_block_data(0x50, 0x01, test_cmd)
                time.sleep(2)
                
                response = input("  Did the robot move to computer command? (y/n): ")
                if response.lower() == 'y':
                    print(f"🎉 SUCCESS! {description} worked!")
                    return True
                else:
                    print(f"  ❌ No movement")
                    
            except Exception as e:
                print(f"  ❌ Sequence failed: {e}")
        
        return False
        
    except Exception as e:
        print(f"❌ Wake up test failed: {e}")
        return False
    finally:
        if 'i2c' in locals():
            i2c.close()

def test_continuous_commands():
    """Test sending continuous commands to see if robot responds"""
    print("\n🔄 Testing Continuous Commands")
    print("=" * 40)
    
    try:
        i2c = smbus.SMBus(0)
        print("✅ Connected to I2C bus 0")
        
        print("🧪 Sending continuous commands for 10 seconds...")
        print("💡 Watch the robot for any movement...")
        
        start_time = time.time()
        while time.time() - start_time < 10:
            # Send different commands rapidly
            commands = [
                [0x01, 0x01, 0x01, 0x90, 0x64],  # Servo 1 to 90°
                [0x01, 0x06, 0x00, 0x1E, 0x64],  # Gripper to 30°
                [0x01, 0x01, 0x01, 0x45, 0x64],  # Servo 1 to 45°
                [0x01, 0x06, 0x00, 0xB4, 0x64],  # Gripper to 180°
            ]
            
            for cmd in commands:
                try:
                    i2c.write_i2c_block_data(0x50, 0x01, cmd)
                    time.sleep(0.5)
                except:
                    pass
        
        print("✅ Continuous command test completed")
        response = input("Did you see any movement during the test? (y/n): ")
        return response.lower() == 'y'
        
    except Exception as e:
        print(f"❌ Continuous test failed: {e}")
        return False
    finally:
        if 'i2c' in locals():
            i2c.close()

def main():
    print("🔧 Wake Up Robot Test")
    print("=" * 50)
    
    # Try wake-up sequences
    if wake_up_robot():
        print("\n🎉 Robot is now responding to computer commands!")
        return
    
    # Try continuous commands
    print("\n🔄 Trying continuous command test...")
    if test_continuous_commands():
        print("\n🎉 Robot responded to continuous commands!")
        return
    
    print("\n❌ No wake-up sequence worked.")
    print("💡 Alternative solutions:")
    print("1. Check if robot needs specific software/drivers")
    print("2. Look for robot documentation")
    print("3. Try connecting with different software")
    print("4. Check if robot is in a locked state")

if __name__ == "__main__":
    main() 