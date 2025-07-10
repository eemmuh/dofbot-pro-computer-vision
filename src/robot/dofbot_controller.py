#!/usr/bin/env python3
"""
DOFBOT Pro Controller
Comprehensive controller for the DOFBOT Pro robot arm
"""

import smbus2
import time
import math

class DOFBOTController:
    def __init__(self, bus=0, address=0x50):
        """
        Initialize DOFBOT controller
        
        Args:
            bus (int): I2C bus number (usually 0)
            address (int): I2C address of the servo controller
        """
        self.bus = bus
        self.address = address
        self.i2c = None
        self.connected = False
        
        # DOFBOT servo configuration
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
        
        # Home position
        self.HOME_POSITION = {
            1: 90,  # Base center
            2: 90,  # Shoulder center
            3: 90,  # Elbow center
            4: 90,  # Wrist center
            5: 90,  # Wrist pitch center
            6: 90   # Gripper half open
        }
        
        # Current positions
        self.current_positions = self.HOME_POSITION.copy()
        
        self.connect()
    
    def connect(self):
        """Connect to the I2C bus"""
        try:
            self.i2c = smbus2.SMBus(self.bus)
            self.connected = True
            print(f"✅ Connected to DOFBOT Pro on I2C bus {self.bus}, address 0x{self.address:02X}")
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
            print("🔌 Disconnected from DOFBOT Pro")
            
    def read_servo_position(self, servo_id):
        """
        Read servo position using DOFBOT protocol
        
        Args:
            servo_id (int): Servo ID (1-6)
            
        Returns:
            int: Servo position in degrees, or None if failed
        """
        if not self.connected or not self.i2c or servo_id not in self.SERVO_ADDRESSES:
            return None
            
        try:
            # DOFBOT position read command
            cmd = [0x01, self.SERVO_ADDRESSES[servo_id], 0x00]
            self.i2c.write_i2c_block_data(self.address, 0x01, cmd)
            time.sleep(0.01)
            
            # Read response (2 bytes)
            data = self.i2c.read_i2c_block_data(self.address, 0x00, 2)
            if len(data) >= 2:
                # Convert to degrees (DOFBOT uses 0-1000 range)
                raw_position = (data[0] << 8) | data[1]
                position = int(raw_position * 180 / 1000)
                self.current_positions[servo_id] = position
                return position
            
            return None
            
        except Exception as e:
            print(f"❌ Error reading servo {servo_id}: {e}")
            return None
            
    def set_servo_position(self, servo_id, position, speed=100):
        """
        Set servo position using DOFBOT protocol
        
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
            # Convert degrees to DOFBOT range (0-1000)
            raw_position = int(position * 1000 / 180)
            
            # DOFBOT servo command format
            cmd = [
                0x01,                    # Command type
                self.SERVO_ADDRESSES[servo_id],  # Servo address
                (raw_position >> 8) & 0xFF,      # High byte
                raw_position & 0xFF,             # Low byte
                speed                           # Speed
            ]
            
            self.i2c.write_i2c_block_data(self.address, 0x01, cmd)
            time.sleep(0.01)
            
            # Update current position
            self.current_positions[servo_id] = position
            print(f"✅ Servo {servo_id} set to {position}°")
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
        print("🏠 Moving all servos to home position...")
        for servo_id, position in self.HOME_POSITION.items():
            self.set_servo_position(servo_id, position)
            time.sleep(0.5)
        
        print("✅ All servos moved to home position")
    
    def move_to_position(self, positions, speed=100):
        """
        Move multiple servos to specified positions
        
        Args:
            positions (dict): {servo_id: position, ...}
            speed (int): Movement speed
        """
        print("🤖 Moving to specified positions...")
        for servo_id, position in positions.items():
            if servo_id in self.SERVO_ADDRESSES:
                self.set_servo_position(servo_id, position, speed)
                time.sleep(0.2)
    
    def cup_stacking_sequence(self):
        """
        Perform a simple cup stacking sequence
        """
        print("🥤 Starting cup stacking sequence...")
        
        # Step 1: Move to pickup position
        pickup_pos = {
            1: 90,   # Base center
            2: 45,   # Shoulder down
            3: 135,  # Elbow up
            4: 90,   # Wrist center
            5: 90    # Wrist pitch center
        }
        self.move_to_position(pickup_pos)
            time.sleep(1)
        
        # Step 2: Open gripper
        self.set_gripper(100)  # Fully open
        time.sleep(0.5)
        
        # Step 3: Move down to cup
        pickup_pos[2] = 30  # Lower shoulder more
        pickup_pos[3] = 150  # Raise elbow more
        self.move_to_position(pickup_pos)
        time.sleep(1)
        
        # Step 4: Close gripper to grab cup
        self.set_gripper(0)  # Close
        time.sleep(1)
        
        # Step 5: Lift cup
        pickup_pos[2] = 60  # Raise shoulder
        pickup_pos[3] = 120  # Lower elbow
        self.move_to_position(pickup_pos)
        time.sleep(1)
        
        # Step 6: Move to stacking position
        stack_pos = {
            1: 180,  # Base rotate
            2: 60,   # Shoulder
            3: 120,  # Elbow
            4: 90,   # Wrist center
            5: 90    # Wrist pitch center
        }
        self.move_to_position(stack_pos)
        time.sleep(1)
        
        # Step 7: Lower and release cup
        stack_pos[2] = 45  # Lower shoulder
        stack_pos[3] = 135  # Raise elbow
        self.move_to_position(stack_pos)
        time.sleep(1)
        
        self.set_gripper(100)  # Open gripper
        time.sleep(0.5)
        
        # Step 8: Return to home
        self.home_all_servos()
        
        print("✅ Cup stacking sequence completed!")
    
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
    
    def get_status(self):
        """Get current status of all servos"""
        print("📊 DOFBOT Pro Status:")
        print("=" * 30)
        
        for servo_id in range(1, 7):
            position = self.read_servo_position(servo_id)
            if position is not None:
                print(f"Servo {servo_id}: {position}°")
            else:
                print(f"Servo {servo_id}: Error reading position")
    
    def __del__(self):
        """Cleanup on destruction"""
        self.disconnect()

def main():
    """Test the DOFBOT controller"""
    print("🤖 DOFBOT Pro Controller Test")
    print("=" * 40)
    
    try:
        # Initialize controller
        controller = DOFBOTController(bus=0, address=0x50)
        
        if controller.connected:
            # Get current status
            controller.get_status()
            
            # Test servos
            controller.test_servos()
            
            # Home position
            controller.home_all_servos()
            
            # Ask user if they want to run cup stacking
            response = input("\n🥤 Run cup stacking sequence? (y/n): ")
            if response.lower() == 'y':
                controller.cup_stacking_sequence()
            
            controller.disconnect()
        else:
            print("❌ Failed to connect to DOFBOT Pro")
            
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 