#!/usr/bin/env python3
"""
Debug Robot Movement - Test if DOFBOT is actually receiving commands
"""

import smbus2 as smbus
import time
import sys

class DOFBOTDebugger:
    def __init__(self, bus=0, address=0x50):
        self.bus = bus
        self.address = address
        self.i2c = None
        
    def connect(self):
        try:
            self.i2c = smbus.SMBus(self.bus)
            print(f"✅ Connected to I2C bus {self.bus}, address 0x{self.address:02X}")
            return True
        except Exception as e:
            print(f"❌ Failed to connect: {e}")
            return False
    
    def test_basic_communication(self):
        """Test basic I2C communication"""
        print("\n🔍 Testing Basic I2C Communication:")
        print("=" * 40)
        
        try:
            # Try to read a byte from the device
            data = self.i2c.read_byte_data(self.address, 0x00)
            print(f"✅ Read byte from register 0x00: 0x{data:02X}")
            
            # Try to write a byte to the device
            self.i2c.write_byte_data(self.address, 0x00, 0x01)
            print("✅ Wrote byte to register 0x00")
            
            return True
        except Exception as e:
            print(f"❌ Communication error: {e}")
            return False
    
    def test_servo_commands(self):
        """Test servo movement commands"""
        print("\n⚙️ Testing Servo Commands:")
        print("=" * 40)
        
        # Test different servo command formats
        test_commands = [
            # Format: [command_type, servo_id, position_high, position_low, speed]
            ([0x01, 0x01, 0x00, 0x00, 0x64], "Servo 1 to 0°"),
            ([0x01, 0x01, 0x01, 0x90, 0x64], "Servo 1 to 90°"),
            ([0x01, 0x01, 0x02, 0x00, 0x64], "Servo 1 to 180°"),
            ([0x01, 0x06, 0x00, 0x1E, 0x64], "Gripper to 30°"),
            ([0x01, 0x06, 0x00, 0xB4, 0x64], "Gripper to 180°"),
        ]
        
        for cmd, description in test_commands:
            try:
                print(f"Testing: {description}")
                self.i2c.write_i2c_block_data(self.address, 0x01, cmd)
                time.sleep(0.1)
                print(f"  ✅ Command sent successfully")
                
                # Try to read back the position
                try:
                    read_cmd = [0x01, cmd[1], 0x00]
                    self.i2c.write_i2c_block_data(self.address, 0x01, read_cmd)
                    time.sleep(0.01)
                    data = self.i2c.read_i2c_block_data(self.address, 0x00, 2)
                    if len(data) >= 2:
                        raw_position = (data[0] << 8) | data[1]
                        position = int(raw_position * 180 / 1000)
                        print(f"  📊 Read back position: {position}°")
                    else:
                        print(f"  ⚠️ Could not read back position")
                except Exception as e:
                    print(f"  ⚠️ Could not read back position: {e}")
                    
            except Exception as e:
                print(f"  ❌ Command failed: {e}")
    
    def test_power_management(self):
        """Test power management commands"""
        print("\n⚡ Testing Power Management:")
        print("=" * 40)
        
        power_commands = [
            ([0x01, 0xFF, 0x00, 0x00], "Emergency Stop"),
            ([0x01, 0x00, 0x01, 0x00], "Power On"),
            ([0x01, 0x00, 0x02, 0x00], "Standby Mode"),
            ([0x01, 0x00, 0x03, 0x00], "Active Mode"),
        ]
        
        for cmd, description in power_commands:
            try:
                print(f"Testing: {description}")
                self.i2c.write_i2c_block_data(self.address, 0x00, cmd)
                time.sleep(0.5)
                print(f"  ✅ Command sent")
            except Exception as e:
                print(f"  ❌ Command failed: {e}")
    
    def test_servo_power(self):
        """Test individual servo power control"""
        print("\n🔌 Testing Servo Power Control:")
        print("=" * 40)
        
        for servo_id in range(1, 7):
            try:
                # Power on servo
                cmd_on = [0x01, servo_id, 0x01, 0x00]
                self.i2c.write_i2c_block_data(self.address, 0x40, cmd_on)
                time.sleep(0.1)
                print(f"  ✅ Servo {servo_id} power on command sent")
                
                # Power off servo
                cmd_off = [0x01, servo_id, 0x00, 0x00]
                self.i2c.write_i2c_block_data(self.address, 0x40, cmd_off)
                time.sleep(0.1)
                print(f"  ✅ Servo {servo_id} power off command sent")
                
            except Exception as e:
                print(f"  ❌ Servo {servo_id} power control failed: {e}")
    
    def check_physical_indicators(self):
        """Check for physical indicators on the robot"""
        print("\n💡 Physical Robot Checks:")
        print("=" * 40)
        print("Please check the following on your DOFBOT Pro:")
        print("1. 🔴 Power LED: Is it lit?")
        print("2. 🟢 Status LED: Is it blinking or solid?")
        print("3. 🔧 Physical switches: Any safety switches that need to be enabled?")
        print("4. 🔌 Cables: Are all servo cables properly connected?")
        print("5. ⚡ Power supply: Is the robot getting enough power?")
        print("6. 🔒 Lock mode: Is there a physical lock or safety mode?")
        print("7. 🎛️ Control mode: Is the robot in the correct control mode?")
        
        response = input("\nDo you see any LED indicators on the robot? (y/n): ")
        if response.lower() == 'y':
            print("✅ Good! The robot is powered on.")
        else:
            print("❌ No LEDs visible - check power supply and connections.")
        
        response = input("Are there any physical switches or buttons on the robot? (y/n): ")
        if response.lower() == 'y':
            print("⚠️ Check if any switches need to be enabled for movement.")
        else:
            print("No physical switches found.")
    
    def disconnect(self):
        if self.i2c:
            self.i2c.close()
            print("🔌 Disconnected")

def main():
    print("🔧 DOFBOT Pro Movement Debugger")
    print("=" * 40)
    
    debugger = DOFBOTDebugger(bus=0, address=0x50)
    
    if not debugger.connect():
        print("❌ Could not connect to robot")
        return
    
    # Run all tests
    debugger.test_basic_communication()
    debugger.test_power_management()
    debugger.test_servo_power()
    debugger.test_servo_commands()
    debugger.check_physical_indicators()
    
    debugger.disconnect()
    
    print("\n📋 Debug Summary:")
    print("=" * 40)
    print("If commands are being sent but robot doesn't move:")
    print("1. Check power supply voltage and current")
    print("2. Verify servo cables are connected")
    print("3. Look for safety switches or locks")
    print("4. Try power cycling the robot")
    print("5. Check if robot is in the correct control mode")
    print("6. Verify the robot is not in emergency stop mode")

if __name__ == "__main__":
    main() 