#!/usr/bin/env python3
"""
DOFBOT Pro Protocol Finder
Find the correct I2C protocol for your DOFBOT Pro
"""

import smbus2
import time
import struct

class DOFBOTProtocolFinder:
    def __init__(self, bus=0):
        self.bus = bus
        self.i2c = None
        self.connected = False
        
        # Known I2C addresses
        self.addresses = [0x50, 0x57, 0x30, 0x40, 0x41, 0x42, 0x43, 0x44, 0x45]
        
        # Different command formats to test
        self.protocols = {
            "DOFBOT_Standard": {
                "description": "Standard DOFBOT protocol",
                "addresses": [0x50, 0x57],
                "commands": [
                    # Format: [command_type, servo_id, position_high, position_low, speed]
                    [0x01, 0x01, 0x01, 0xE0, 0x64],  # Servo 1 to 480 (90 degrees)
                    [0x01, 0x02, 0x01, 0xE0, 0x64],  # Servo 2 to 480
                    [0x01, 0x06, 0x01, 0xE0, 0x64],  # Servo 6 (gripper) to 480
                ]
            },
            "DOFBOT_Alternative": {
                "description": "Alternative DOFBOT protocol",
                "addresses": [0x50, 0x57],
                "commands": [
                    # Format: [servo_id, position_high, position_low, speed]
                    [0x01, 0x01, 0xE0, 0x64],  # Servo 1 to 480
                    [0x02, 0x01, 0xE0, 0x64],  # Servo 2 to 480
                    [0x06, 0x01, 0xE0, 0x64],  # Servo 6 to 480
                ]
            },
            "PWM_Servo": {
                "description": "PWM servo controller protocol",
                "addresses": [0x40, 0x41, 0x42, 0x43, 0x44, 0x45],
                "commands": [
                    # Format: [register, position_high, position_low]
                    [0x06, 0x01, 0xE0],  # Servo 1 to 480
                    [0x0A, 0x01, 0xE0],  # Servo 2 to 480
                    [0x0E, 0x01, 0xE0],  # Servo 3 to 480
                ]
            },
            "Simple_Position": {
                "description": "Simple position protocol",
                "addresses": [0x50, 0x57],
                "commands": [
                    # Format: [servo_id, position]
                    [0x01, 90],  # Servo 1 to 90 degrees
                    [0x02, 90],  # Servo 2 to 90 degrees
                    [0x06, 90],  # Servo 6 to 90 degrees
                ]
            },
            "Binary_Protocol": {
                "description": "Binary protocol",
                "addresses": [0x50, 0x57],
                "commands": [
                    # Format: [0xFF, servo_id, position, 0x00]
                    [0xFF, 0x01, 90, 0x00],
                    [0xFF, 0x02, 90, 0x00],
                    [0xFF, 0x06, 90, 0x00],
                ]
            }
        }
        
        self.connect()
    
    def connect(self):
        """Connect to I2C bus"""
        try:
            self.i2c = smbus2.SMBus(self.bus)
            self.connected = True
            print(f"✅ Connected to I2C bus {self.bus}")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to I2C bus {self.bus}: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from I2C bus"""
        if self.i2c:
            self.i2c.close()
            self.connected = False
    
    def test_address(self, address):
        """Test if an I2C address responds"""
        try:
            # Try to read from the address
            data = self.i2c.read_i2c_block_data(address, 0x00, 1)
            return True
        except Exception:
            return False
    
    def send_command(self, address, command, protocol_name):
        """Send a command and check for response"""
        try:
            print(f"  Sending: {protocol_name} - {[hex(x) for x in command]}")
            
            # Try different send methods
            methods = [
                # Method 1: write_i2c_block_data
                lambda: self.i2c.write_i2c_block_data(address, command[0], command[1:]),
                # Method 2: write_byte_data
                lambda: self.i2c.write_byte_data(address, command[0], command[1]),
                # Method 3: write_word_data
                lambda: self.i2c.write_word_data(address, command[0], (command[1] << 8) | command[2]),
                # Method 4: write_quick
                lambda: self.i2c.write_quick(address, command[0]),
            ]
            
            for i, method in enumerate(methods):
                try:
                    method()
                    print(f"    ✅ Method {i+1} succeeded")
                    time.sleep(0.1)
                    
                    # Try to read response
                    try:
                        response = self.i2c.read_i2c_block_data(address, 0x00, 2)
                        print(f"    📥 Response: {[hex(x) for x in response]}")
                    except:
                        print(f"    📥 No response (this might be normal)")
                    
                    return True
                except Exception as e:
                    print(f"    ❌ Method {i+1} failed: {e}")
                    continue
            
            return False
            
        except Exception as e:
            print(f"    ❌ Command failed: {e}")
            return False
    
    def find_working_protocol(self):
        """Find the working protocol for the DOFBOT Pro"""
        print("🔍 DOFBOT Pro Protocol Finder")
        print("=" * 50)
        
        if not self.connected:
            print("❌ Not connected to I2C bus")
            return None
        
        # First, scan for responding addresses
        print("\n📡 Scanning I2C addresses...")
        responding_addresses = []
        
        for address in self.addresses:
            if self.test_address(address):
                print(f"✅ Address 0x{address:02X} responds")
                responding_addresses.append(address)
            else:
                print(f"❌ Address 0x{address:02X} no response")
        
        if not responding_addresses:
            print("❌ No responding I2C addresses found")
            return None
        
        print(f"\n🎯 Found {len(responding_addresses)} responding addresses")
        
        # Test each protocol on responding addresses
        working_protocols = []
        
        for protocol_name, protocol_info in self.protocols.items():
            print(f"\n🧪 Testing protocol: {protocol_name}")
            print(f"   Description: {protocol_info['description']}")
            
            for address in protocol_info['addresses']:
                if address in responding_addresses:
                    print(f"   Testing on address 0x{address:02X}...")
                    
                    # Test each command in the protocol
                    for command in protocol_info['commands']:
                        success = self.send_command(address, command, protocol_name)
                        if success:
                            print(f"   ✅ Command succeeded on 0x{address:02X}")
                            working_protocols.append({
                                'protocol': protocol_name,
                                'address': address,
                                'command': command,
                                'description': protocol_info['description']
                            })
                        
                        time.sleep(0.5)  # Wait between commands
        
        # Report results
        print(f"\n📊 Protocol Test Results")
        print("=" * 30)
        
        if working_protocols:
            print(f"✅ Found {len(working_protocols)} working command(s):")
            for i, result in enumerate(working_protocols, 1):
                print(f"  {i}. Protocol: {result['protocol']}")
                print(f"     Address: 0x{result['address']:02X}")
                print(f"     Command: {[hex(x) for x in result['command']]}")
                print(f"     Description: {result['description']}")
                print()
            
            return working_protocols[0]  # Return first working protocol
        else:
            print("❌ No working protocols found")
            print("\n💡 Suggestions:")
            print("   1. Check if the robot is powered on")
            print("   2. Verify I2C connections")
            print("   3. Check if the robot needs firmware")
            print("   4. Try different I2C addresses")
            return None
    
    def test_physical_movement(self, protocol_info):
        """Test if commands actually move the robot"""
        if not protocol_info:
            return False
        
        print(f"\n🤖 Testing physical movement with {protocol_info['protocol']}")
        print("=" * 50)
        
        address = protocol_info['address']
        command = protocol_info['command']
        
        print("⚠️  WARNING: Robot will attempt to move!")
        print("   Make sure the robot is in a safe position")
        response = input("   Continue? (y/n): ")
        
        if response.lower() != 'y':
            print("❌ Test cancelled")
            return False
        
        print("\n🧪 Testing servo movements...")
        
        # Test different positions
        test_positions = [
            (85, "Slightly left"),
            (95, "Slightly right"),
            (90, "Center"),
            (0, "Far left"),
            (180, "Far right")
        ]
        
        for position, description in test_positions:
            print(f"\n📐 Testing {description} (position {position})...")
            
            # Modify command with new position
            test_command = command.copy()
            if len(test_command) >= 3:
                # Convert position to appropriate format
                if position <= 255:
                    test_command[2] = position
                else:
                    test_command[2] = (position >> 8) & 0xFF
                    if len(test_command) > 3:
                        test_command[3] = position & 0xFF
            
            print(f"   Command: {[hex(x) for x in test_command]}")
            
            # Send command
            success = self.send_command(address, test_command, protocol_info['protocol'])
            
            if success:
                print(f"   ✅ Command sent successfully")
                print(f"   👀 Watch the robot for movement...")
                
                # Wait for user to observe
                time.sleep(3)
                
                response = input(f"   Did the robot move? (y/n): ")
                if response.lower() == 'y':
                    print(f"   🎉 SUCCESS! Protocol {protocol_info['protocol']} works!")
                    return True
                else:
                    print(f"   ❌ No movement observed")
            else:
                print(f"   ❌ Command failed")
        
        print(f"\n❌ No physical movement detected with {protocol_info['protocol']}")
        return False

def main():
    """Main test function"""
    finder = DOFBOTProtocolFinder(bus=0)
    
    try:
        # Find working protocol
        working_protocol = finder.find_working_protocol()
        
        if working_protocol:
            # Test physical movement
            finder.test_physical_movement(working_protocol)
        else:
            print("\n❌ No working protocol found")
            print("The robot may need:")
            print("  1. Power supply")
            print("  2. Correct firmware")
            print("  3. Different communication method")
    
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        finder.disconnect()

if __name__ == "__main__":
    main() 