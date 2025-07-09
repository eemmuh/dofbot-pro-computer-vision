#!/usr/bin/env python3
"""
DOFBOT Servo Finder
Find the correct servo addresses and position ranges
"""

import smbus2
import time

class DOFBOTServoFinder:
    def __init__(self, bus=0, address=0x50):
        self.bus = bus
        self.address = address
        self.i2c = None
        self.connected = False
        
        self.connect()
    
    def connect(self):
        """Connect to I2C bus"""
        try:
            self.i2c = smbus2.SMBus(self.bus)
            self.connected = True
            print(f"✅ Connected to I2C bus {self.bus}, address 0x{self.address:02X}")
            return True
        except Exception as e:
            print(f"❌ Failed to connect: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from I2C bus"""
        if self.i2c:
            self.i2c.close()
            self.connected = False
    
    def test_servo_addresses(self):
        """Test different servo addresses"""
        print("\n🔍 Testing different servo addresses...")
        
        # Test servo addresses 0x01 to 0x20
        for servo_id in range(1, 33):
            print(f"\n🧪 Testing servo address 0x{servo_id:02X}...")
            
            # Try different position values
            test_positions = [90, 180, 0, 45, 135]
            
            for position in test_positions:
                # Try different command formats
                commands = [
                    # Format 1: [command, servo_id, position]
                    [0x01, servo_id, position],
                    # Format 2: [servo_id, position]
                    [servo_id, position],
                    # Format 3: [command, servo_id, position_high, position_low]
                    [0x01, servo_id, (position >> 8) & 0xFF, position & 0xFF],
                    # Format 4: [0xFF, servo_id, position]
                    [0xFF, servo_id, position],
                ]
                
                for cmd in commands:
                    try:
                        print(f"  Testing: {[hex(x) for x in cmd]} (position {position})")
                        
                        # Send command
                        self.i2c.write_i2c_block_data(self.address, cmd[0], cmd[1:])
                        time.sleep(0.1)
                        
                        # Try to read response
                        try:
                            response = self.i2c.read_i2c_block_data(self.address, 0x00, 2)
                            print(f"    📥 Response: {[hex(x) for x in response]}")
                        except:
                            print(f"    📥 No response")
                        
                        # Ask user if they saw movement
                        response = input(f"    Did servo {servo_id:02X} move? (y/n/s=skip): ")
                        if response.lower() == 'y':
                            print(f"    🎉 SUCCESS! Servo {servo_id:02X} responds to {[hex(x) for x in cmd]}")
                            return servo_id, cmd, position
                        elif response.lower() == 's':
                            break
                        
                    except Exception as e:
                        print(f"    ❌ Error: {e}")
                        continue
        
        return None, None, None
    
    def test_position_ranges(self, servo_id, command_format):
        """Test different position ranges for a working servo"""
        print(f"\n📐 Testing position ranges for servo 0x{servo_id:02X}...")
        
        # Test different position scales
        ranges = [
            (0, 180, "0-180 degrees"),
            (0, 255, "0-255 range"),
            (0, 1000, "0-1000 range"),
            (500, 2500, "500-2500 microseconds"),
            (0, 4095, "12-bit range"),
        ]
        
        for min_val, max_val, description in ranges:
            print(f"\n🧪 Testing {description}...")
            
            # Test a few positions in this range
            test_positions = [min_val, (min_val + max_val) // 2, max_val]
            
            for position in test_positions:
                # Create command with this position
                cmd = command_format.copy()
                if len(cmd) >= 3:
                    if position <= 255:
                        cmd[2] = position
                    else:
                        cmd[2] = (position >> 8) & 0xFF
                        if len(cmd) > 3:
                            cmd[3] = position & 0xFF
                
                try:
                    print(f"  Testing position {position} with {[hex(x) for x in cmd]}")
                    
                    # Send command
                    self.i2c.write_i2c_block_data(self.address, cmd[0], cmd[1:])
                    time.sleep(0.5)
                    
                    # Ask user
                    response = input(f"    Did servo move to position {position}? (y/n): ")
                    if response.lower() == 'y':
                        print(f"    ✅ Position range {description} works!")
                        return min_val, max_val
                
                except Exception as e:
                    print(f"    ❌ Error: {e}")
                    continue
        
        return None, None
    
    def test_servo_enable(self):
        """Test servo enable/disable commands"""
        print("\n🔌 Testing servo enable commands...")
        
        enable_commands = [
            [0x01, 0x00, 0x01],  # Enable all servos
            [0x02, 0x00, 0x01],  # Alternative enable
            [0xFF, 0x00, 0x01],  # Binary enable
            [0x01, 0x01],        # Simple enable
        ]
        
        for cmd in enable_commands:
            try:
                print(f"  Testing enable command: {[hex(x) for x in cmd]}")
                self.i2c.write_i2c_block_data(self.address, cmd[0], cmd[1:])
                time.sleep(0.5)
                
                response = input(f"    Did servos become enabled? (y/n): ")
                if response.lower() == 'y':
                    print(f"    ✅ Enable command {[hex(x) for x in cmd]} works!")
                    return cmd
            except Exception as e:
                print(f"    ❌ Error: {e}")
                continue
        
        return None
    
    def find_working_configuration(self):
        """Find the complete working configuration"""
        print("🔍 DOFBOT Servo Configuration Finder")
        print("=" * 50)
        
        if not self.connected:
            print("❌ Not connected to I2C bus")
            return None
        
        # Step 1: Test servo enable
        print("\n📋 Step 1: Testing servo enable...")
        enable_cmd = self.test_servo_enable()
        
        # Step 2: Find working servo addresses
        print("\n📋 Step 2: Finding working servo addresses...")
        servo_id, command_format, test_position = self.test_servo_addresses()
        
        if servo_id is None:
            print("❌ No working servo addresses found")
            return None
        
        # Step 3: Test position ranges
        print("\n📋 Step 3: Testing position ranges...")
        min_pos, max_pos = self.test_position_ranges(servo_id, command_format)
        
        if min_pos is None:
            print("❌ No working position range found")
            return None
        
        # Report results
        print(f"\n🎉 CONFIGURATION FOUND!")
        print("=" * 30)
        print(f"Servo ID: 0x{servo_id:02X}")
        print(f"Command Format: {[hex(x) for x in command_format]}")
        print(f"Position Range: {min_pos} to {max_pos}")
        if enable_cmd:
            print(f"Enable Command: {[hex(x) for x in enable_cmd]}")
        
        return {
            'servo_id': servo_id,
            'command_format': command_format,
            'position_range': (min_pos, max_pos),
            'enable_command': enable_cmd
        }

def main():
    """Main test function"""
    finder = DOFBOTServoFinder(bus=0, address=0x50)
    
    try:
        config = finder.find_working_configuration()
        
        if config:
            print(f"\n💾 Save this configuration:")
            print(f"   Servo ID: 0x{config['servo_id']:02X}")
            print(f"   Command: {[hex(x) for x in config['command_format']]}")
            print(f"   Range: {config['position_range']}")
        else:
            print("\n❌ No working configuration found")
            print("The robot may need:")
            print("  1. Power supply")
            print("  2. Servo connections")
            print("  3. Different communication method")
    
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        finder.disconnect()

if __name__ == "__main__":
    main() 