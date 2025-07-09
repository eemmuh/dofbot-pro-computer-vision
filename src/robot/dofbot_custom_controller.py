#!/usr/bin/env python3
"""
Custom DOFBOT Pro Controller
Uses the correct I2C address (0x50) found on bus 0
"""

import smbus
import time

class DOFBOTCustomController:
    def __init__(self, i2c_bus=0, i2c_addr=0x50):
        """
        Initialize custom DOFBOT controller
        
        Args:
            i2c_bus (int): I2C bus number (default: 0)
            i2c_addr (int): I2C address (default: 0x50)
        """
        try:
            self.bus = smbus.SMBus(i2c_bus)
            self.addr = i2c_addr
            self.connected = True
            print(f"✅ Connected to DOFBOT Pro (bus {i2c_bus}, addr 0x{i2c_addr:02x})")
        except Exception as e:
            print(f"❌ Failed to connect: {e}")
            self.connected = False
    
    def set_servo_position(self, servo_id, angle, time_ms=1000):
        """
        Set servo position using custom protocol
        
        Args:
            servo_id (int): Servo ID (1-6)
            angle (int): Angle in degrees (0-180)
            time_ms (int): Movement time in milliseconds
        """
        if not self.connected:
            print("❌ Not connected to DOFBOT Pro")
            return False
        
        try:
            # Convert angle to servo position (0-4095 for most servos)
            pos = int((4095 - 0) * (angle - 0) / (180 - 0) + 0)
            
            # Split into high and low bytes
            pos_H = (pos >> 8) & 0xFF
            pos_L = pos & 0xFF
            time_H = (time_ms >> 8) & 0xFF
            time_L = time_ms & 0xFF
            
            # Try different command formats
            commands = [
                # Format 1: [servo_id, pos_H, pos_L, time_H, time_L]
                [servo_id, pos_H, pos_L, time_H, time_L],
                # Format 2: [0x10 + servo_id, pos_H, pos_L, time_H, time_L]
                [0x10 + servo_id, pos_H, pos_L, time_H, time_L],
                # Format 3: [0x19, servo_id, pos_H, pos_L, time_H, time_L]
                [0x19, servo_id, pos_H, pos_L, time_H, time_L],
            ]
            
            for i, cmd in enumerate(commands):
                try:
                    print(f"🤖 Moving servo {servo_id} to {angle}° (format {i+1})")
                    self.bus.write_i2c_block_data(self.addr, cmd[0], cmd[1:])
                    time.sleep(0.1)  # Wait for response
                    return True
                except Exception as e:
                    print(f"  Format {i+1} failed: {e}")
                    continue
            
            print(f"❌ All command formats failed for servo {servo_id}")
            return False
            
        except Exception as e:
            print(f"❌ Error moving servo {servo_id}: {e}")
            return False
    
    def set_gripper(self, open_percent, time_ms=1000):
        """
        Set gripper position
        
        Args:
            open_percent (int): 0 = closed, 100 = fully open
            time_ms (int): Movement time in milliseconds
        """
        # Convert percentage to angle (0-180)
        angle = int((100 - open_percent) * 180 / 100)
        return self.set_servo_position(6, angle, time_ms)
    
    def move_all_servos(self, positions, time_ms=1000):
        """
        Move all servos to specified positions
        
        Args:
            positions (list): [servo1, servo2, servo3, servo4, servo5, servo6] angles
            time_ms (int): Movement time in milliseconds
        """
        if not self.connected:
            print("❌ Not connected to DOFBOT Pro")
            return False
        
        if len(positions) != 6:
            print("❌ positions must be a list of 6 angles")
            return False
        
        try:
            print(f"🤖 Moving all servos to {positions}")
            
            # Convert all angles to servo positions
            servo_positions = []
            for angle in positions:
                pos = int((4095 - 0) * (angle - 0) / (180 - 0) + 0)
                servo_positions.extend([(pos >> 8) & 0xFF, pos & 0xFF])
            
            time_H = (time_ms >> 8) & 0xFF
            time_L = time_ms & 0xFF
            
            # Try different multi-servo command formats
            commands = [
                # Format 1: [0x1d, all_positions, time_H, time_L]
                [0x1d] + servo_positions + [time_H, time_L],
                # Format 2: [0x17, all_positions, time_H, time_L]
                [0x17] + servo_positions + [time_H, time_L],
                # Format 3: [0x1e, time_H, time_L] then [0x1d, all_positions]
                [0x1e, time_H, time_L],
            ]
            
            for i, cmd in enumerate(commands):
                try:
                    if i == 2:  # Format 3: two-step command
                        self.bus.write_i2c_block_data(self.addr, cmd[0], cmd[1:])
                        time.sleep(0.01)
                        self.bus.write_i2c_block_data(self.addr, 0x1d, servo_positions)
                    else:
                        self.bus.write_i2c_block_data(self.addr, cmd[0], cmd[1:])
                    
                    time.sleep(0.1)
                    return True
                except Exception as e:
                    print(f"  Format {i+1} failed: {e}")
                    continue
            
            print("❌ All multi-servo command formats failed")
            return False
            
        except Exception as e:
            print(f"❌ Error moving all servos: {e}")
            return False
    
    def home_position(self, time_ms=1000):
        """Move to home position"""
        home_pos = [90, 90, 90, 90, 90, 90]  # All servos to center
        return self.move_all_servos(home_pos, time_ms)
    
    def test_servos(self):
        """Test all servos with small movements"""
        if not self.connected:
            print("❌ Not connected to DOFBOT Pro")
            return False
        
        print("🧪 Testing all servos...")
        
        # Test each servo individually
        for servo_id in range(1, 7):
            if servo_id == 6:  # Gripper
                print(f"Testing gripper (servo {servo_id})...")
                self.set_gripper(50)   # Half open
                time.sleep(1)
                self.set_gripper(0)    # Closed
                time.sleep(1)
                self.set_gripper(100)  # Open
                time.sleep(1)
            else:
                print(f"Testing servo {servo_id}...")
                
                # Small movement test
                self.set_servo_position(servo_id, 85)
                time.sleep(0.5)
                self.set_servo_position(servo_id, 95)
                time.sleep(0.5)
                self.set_servo_position(servo_id, 90)
                time.sleep(0.5)
        
        print("✅ Servo test completed")
        return True
    
    def cup_stacking_sequence(self):
        """Perform a simple cup stacking sequence"""
        if not self.connected:
            print("❌ Not connected to DOFBOT Pro")
            return False
        
        print("🥤 Starting cup stacking sequence...")
        
        # Step 1: Move to pickup position
        pickup_pos = [90, 45, 135, 90, 90, 90]
        self.move_all_servos(pickup_pos)
        time.sleep(1)
        
        # Step 2: Open gripper
        self.set_gripper(100)  # Fully open
        time.sleep(0.5)
        
        # Step 3: Move down to cup
        pickup_pos[1] = 30  # Lower shoulder
        pickup_pos[2] = 150  # Raise elbow
        self.move_all_servos(pickup_pos)
        time.sleep(1)
        
        # Step 4: Close gripper to grab cup
        self.set_gripper(0)  # Close
        time.sleep(1)
        
        # Step 5: Lift cup
        pickup_pos[1] = 60  # Raise shoulder
        pickup_pos[2] = 120  # Lower elbow
        self.move_all_servos(pickup_pos)
        time.sleep(1)
        
        # Step 6: Move to stacking position
        stack_pos = [180, 60, 120, 90, 90, 90]  # Rotate base
        self.move_all_servos(stack_pos)
        time.sleep(1)
        
        # Step 7: Lower and release cup
        stack_pos[1] = 45  # Lower shoulder
        stack_pos[2] = 135  # Raise elbow
        self.move_all_servos(stack_pos)
        time.sleep(1)
        
        self.set_gripper(100)  # Open gripper
        time.sleep(0.5)
        
        # Step 8: Return to home
        self.home_position()
        
        print("✅ Cup stacking sequence completed!")
        return True

def main():
    """Test the custom DOFBOT controller"""
    print("🤖 Custom DOFBOT Pro Controller Test")
    print("=" * 50)
    
    # Try different I2C addresses on bus 0
    addresses = [0x50, 0x57, 0x30]
    
    for addr in addresses:
        print(f"\n🔍 Trying I2C address 0x{addr:02x} on bus 0...")
        
        try:
            controller = DOFBOTCustomController(i2c_bus=0, i2c_addr=addr)
            
            if controller.connected:
                print(f"✅ Connected to address 0x{addr:02x}")
                
                # Test servos
                controller.test_servos()
                
                # Home position
                controller.home_position()
                
                # Ask user if they want to run cup stacking
                response = input("\n🥤 Run cup stacking sequence? (y/n): ")
                if response.lower() == 'y':
                    controller.cup_stacking_sequence()
                
                break
            else:
                print(f"❌ Failed to connect to address 0x{addr:02x}")
                
        except Exception as e:
            print(f"❌ Error with address 0x{addr:02x}: {e}")
            continue
    
    print("\n🎯 Test completed!")

if __name__ == "__main__":
    main() 