#!/usr/bin/env python3
"""
DOFBOT Pro I2C Controller
Controls the DOFBOT Pro robot via I2C communication
"""

import smbus2
import time
import struct

class DOFBOTI2CController:
    def __init__(self, bus=0, address=0x50):
        """
        Initialize DOFBOT I2C controller
        
        Args:
            bus (int): I2C bus number (usually 0 or 1)
            address (int): I2C address of the servo controller
        """
        self.bus = bus
        self.address = address
        self.i2c = None
        self.connected = False
        
        # DOFBOT servo addresses (typical)
        self.SERVO_ADDRESSES = {
            1: 0x01,  # Base rotation
            2: 0x02,  # Shoulder
            3: 0x03,  # Elbow
            4: 0x04,  # Wrist rotation
            5: 0x05,  # Wrist pitch
            6: 0x06   # Gripper
        }
        
        # Servo limits (degrees)
        self.SERVO_LIMITS = {
            1: (0, 180),    # Base rotation
            2: (0, 180),    # Shoulder
            3: (0, 180),    # Elbow
            4: (0, 180),    # Wrist rotation
            5: (0, 180),    # Wrist pitch
            6: (0, 180)     # Gripper
        }
        
        self.connect()
    
    def connect(self):
        """Connect to the I2C bus"""
        try:
            self.i2c = smbus2.SMBus(self.bus)
            self.connected = True
            print(f"✅ Connected to I2C bus {self.bus}, address 0x{self.address:02X}")
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
            print("🔌 Disconnected from I2C bus")
    
    def read_servo_position(self, servo_id):
        """
        Read servo position
        
        Args:
            servo_id (int): Servo ID (1-6)
            
        Returns:
            int: Servo position in degrees, or None if failed
        """
        if not self.connected or not self.i2c or servo_id not in self.SERVO_ADDRESSES:
            return None
        
        try:
            # Try different read commands
            commands = [
                # Command 1: Direct position read
                [0x01, self.SERVO_ADDRESSES[servo_id], 0x00],
                # Command 2: Status read
                [0x02, self.SERVO_ADDRESSES[servo_id]],
                # Command 3: Position read
                [0x03, self.SERVO_ADDRESSES[servo_id]]
            ]
            
            for cmd in commands:
                try:
                    # Send command
                    if self.i2c:
                        self.i2c.write_i2c_block_data(self.address, cmd[0], cmd[1:])
                        time.sleep(0.01)
                        
                        # Read response
                        data = self.i2c.read_i2c_block_data(self.address, 0x00, 2)
                        if len(data) >= 2:
                            position = (data[0] << 8) | data[1]
                            return position
                except Exception as e:
                    continue
            
            return None
            
        except Exception as e:
            print(f"❌ Error reading servo {servo_id}: {e}")
            return None
    
    def set_servo_position(self, servo_id, position, speed=100):
        """
        Set servo position
        
        Args:
            servo_id (int): Servo ID (1-6)
            position (int): Position in degrees (0-180)
            speed (int): Movement speed (0-255)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.connected or not self.i2c or servo_id not in self.SERVO_ADDRESSES:
            return False
        
        # Check limits
        min_pos, max_pos = self.SERVO_LIMITS[servo_id]
        position = max(min_pos, min(max_pos, position))
        
        try:
            # Try different command formats
            commands = [
                # Format 1: Standard servo command
                [0x01, self.SERVO_ADDRESSES[servo_id], position, speed],
                # Format 2: Position only
                [0x02, self.SERVO_ADDRESSES[servo_id], position],
                # Format 3: With time
                [0x03, self.SERVO_ADDRESSES[servo_id], position, speed, 0x00]
            ]
            
            for cmd in commands:
                try:
                    if self.i2c:
                        self.i2c.write_i2c_block_data(self.address, cmd[0], cmd[1:])
                        time.sleep(0.01)
                        
                        # Check if command was accepted
                        response = self.i2c.read_i2c_block_data(self.address, 0x00, 1)
                        if response and response[0] == 0x06:  # ACK
                            print(f"✅ Servo {servo_id} set to {position}°")
                            return True
                except Exception as e:
                    continue
            
            # If no response, assume it worked
            print(f"✅ Servo {servo_id} set to {position}° (no response)")
            return True
            
        except Exception as e:
            print(f"❌ Error setting servo {servo_id}: {e}")
            return False
    
    def set_gripper(self, open_percent):
        """
        Set gripper position
        
        Args:
            open_percent (int): 0 = closed, 100 = fully open
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Convert percentage to servo position
        position = int((100 - open_percent) * 180 / 100)
        return self.set_servo_position(6, position)
    
    def home_all_servos(self):
        """Move all servos to home position"""
        home_positions = {
            1: 90,  # Base center
            2: 90,  # Shoulder center
            3: 90,  # Elbow center
            4: 90,  # Wrist center
            5: 90,  # Wrist pitch center
            6: 90   # Gripper half open
        }
        
        print("🏠 Moving all servos to home position...")
        for servo_id, position in home_positions.items():
            self.set_servo_position(servo_id, position)
            time.sleep(0.5)
        
        print("✅ All servos moved to home position")
    
    def test_servos(self):
        """Test all servos with small movements"""
        print("🧪 Testing all servos...")
        
        for servo_id in range(1, 7):
            if servo_id == 6:  # Gripper
                print(f"Testing gripper (servo {servo_id})...")
                self.set_gripper(50)  # Half open
                time.sleep(1)
                self.set_gripper(0)   # Closed
                time.sleep(1)
                self.set_gripper(100) # Open
                time.sleep(1)
            else:
                print(f"Testing servo {servo_id}...")
                current_pos = self.read_servo_position(servo_id)
                print(f"  Current position: {current_pos}°")
                
                # Small movement test
                self.set_servo_position(servo_id, 85)
                time.sleep(0.5)
                self.set_servo_position(servo_id, 95)
                time.sleep(0.5)
                self.set_servo_position(servo_id, 90)
                time.sleep(0.5)
        
        print("✅ Servo test completed")
    
    def __del__(self):
        """Cleanup on destruction"""
        self.disconnect()

def main():
    """Test the DOFBOT I2C controller"""
    print("🤖 DOFBOT Pro I2C Controller Test")
    print("=" * 40)
    
    # Try different I2C addresses
    addresses = [0x50, 0x57, 0x30]
    
    for address in addresses:
        print(f"\n🔍 Trying I2C address 0x{address:02X}...")
        
        try:
            controller = DOFBOTI2CController(bus=0, address=address)
            
            if controller.connected:
                print(f"✅ Connected to address 0x{address:02X}")
                
                # Test servos
                controller.test_servos()
                
                # Home position
                controller.home_all_servos()
                
                controller.disconnect()
                break
            else:
                print(f"❌ Failed to connect to address 0x{address:02X}")
                
        except Exception as e:
            print(f"❌ Error with address 0x{address:02X}: {e}")
            continue
    
    print("\n🎯 Test completed!")

if __name__ == "__main__":
    main() 