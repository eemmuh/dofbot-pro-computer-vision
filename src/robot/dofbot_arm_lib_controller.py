#!/usr/bin/env python3
"""
DOFBOT Pro Controller using Arm_Lib
Uses the correct Arm_Lib protocol for DOFBOT Pro
"""

import sys
import time

# Add Arm_Lib to path
sys.path.append('/home/jetson/software/Arm_Lib')

try:
    from Arm_Lib import Arm_Device
except ImportError:
    print("❌ Arm_Lib not found. Please install it first.")
    sys.exit(1)

class DOFBOTArmLibController:
    def __init__(self, i2c_bus=7):
        """
        Initialize DOFBOT controller using Arm_Lib
        
        Args:
            i2c_bus (int): I2C bus number (default: 7 for DOFBOT Pro)
        """
        try:
            self.arm = Arm_Device(i2c_bus)
            self.connected = True
            print(f"✅ Connected to DOFBOT Pro using Arm_Lib (bus {i2c_bus})")
        except Exception as e:
            print(f"❌ Failed to connect to DOFBOT Pro: {e}")
            self.connected = False
    
    def set_servo_position(self, servo_id, angle, time_ms=1000):
        """
        Set servo position using Arm_Lib
        
        Args:
            servo_id (int): Servo ID (1-6)
            angle (int): Angle in degrees (0-180)
            time_ms (int): Movement time in milliseconds
        """
        if not self.connected:
            print("❌ Not connected to DOFBOT Pro")
            return False
        
        try:
            print(f"🤖 Moving servo {servo_id} to {angle}°")
            self.arm.Arm_serial_servo_write(servo_id, angle, time_ms)
            return True
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
        if not self.connected:
            print("❌ Not connected to DOFBOT Pro")
            return False
        
        # Convert percentage to angle (0-180)
        angle = int((100 - open_percent) * 180 / 100)
        
        try:
            print(f"🤏 Setting gripper to {open_percent}% open ({angle}°)")
            self.arm.Arm_serial_servo_write(6, angle, time_ms)
            return True
        except Exception as e:
            print(f"❌ Error setting gripper: {e}")
            return False
    
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
            self.arm.Arm_serial_servo_write6_array(positions, time_ms)
            return True
        except Exception as e:
            print(f"❌ Error moving all servos: {e}")
            return False
    
    def home_position(self, time_ms=1000):
        """Move to home position"""
        home_pos = [90, 90, 90, 90, 90, 90]  # All servos to center
        return self.move_all_servos(home_pos, time_ms)
    
    def read_servo_position(self, servo_id):
        """
        Read current servo position
        
        Args:
            servo_id (int): Servo ID (1-6)
            
        Returns:
            int: Current angle in degrees, or None if failed
        """
        if not self.connected:
            print("❌ Not connected to DOFBOT Pro")
            return None
        
        try:
            angle = self.arm.Arm_serial_servo_read(servo_id)
            if angle is not None:
                print(f"📊 Servo {servo_id} current position: {angle}°")
            return angle
        except Exception as e:
            print(f"❌ Error reading servo {servo_id}: {e}")
            return None
    
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
                current_pos = self.read_servo_position(servo_id)
                
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
        pickup_pos = [90, 45, 135, 90, 90, 90]  # [base, shoulder, elbow, wrist, wrist_pitch, gripper]
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
    
    def get_status(self):
        """Get current status of all servos"""
        if not self.connected:
            print("❌ Not connected to DOFBOT Pro")
            return
        
        print("📊 DOFBOT Pro Status:")
        print("=" * 30)
        
        for servo_id in range(1, 7):
            position = self.read_servo_position(servo_id)
            if position is not None:
                print(f"Servo {servo_id}: {position}°")
            else:
                print(f"Servo {servo_id}: Error reading position")

def main():
    """Test the DOFBOT Arm_Lib controller"""
    print("🤖 DOFBOT Pro Arm_Lib Controller Test")
    print("=" * 50)
    
    # Try different I2C buses
    for bus in [7, 0, 1]:
        print(f"\n🔍 Trying I2C bus {bus}...")
        
        try:
            controller = DOFBOTArmLibController(i2c_bus=bus)
            
            if controller.connected:
                print(f"✅ Connected to bus {bus}")
                
                # Get current status
                controller.get_status()
                
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
                print(f"❌ Failed to connect to bus {bus}")
                
        except Exception as e:
            print(f"❌ Error with bus {bus}: {e}")
            continue
    
    print("\n🎯 Test completed!")

if __name__ == "__main__":
    main() 