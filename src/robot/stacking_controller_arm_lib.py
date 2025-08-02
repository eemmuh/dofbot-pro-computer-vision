#!/usr/bin/env python3
"""
Cup Stacking Controller for DOFBOT Pro using Arm_Lib
Implements basic stacking logic and robot movements
"""

# Fix smbus import issue BEFORE importing Arm_Lib
import sys
try:
    import smbus2 as smbus
    sys.modules['smbus'] = smbus
    print("✅ smbus compatibility fixed")
except ImportError:
    print("❌ smbus2 not available")
    sys.exit(1)

import time
import math
from typing import List, Tuple, Optional

# Now import Arm_Lib after fixing smbus
try:
    from Arm_Lib import Arm_Device
    print("✅ Arm_Lib imported successfully")
except Exception as e:
    print(f"❌ Error importing Arm_Lib: {e}")
    sys.exit(1)

class StackingControllerArmLib:
    def __init__(self, i2c_bus=0):
        """
        Initialize stacking controller with Arm_Lib
        
        Args:
            i2c_bus (int): I2C bus number (0 for DOFBOT Pro)
        """
        try:
            self.arm = Arm_Device()
            time.sleep(0.1)  # Small delay for initialization
            print(f"✅ Arm_Lib initialized successfully")
            self.connected = True
        except Exception as e:
            print(f"❌ Failed to initialize Arm_Lib: {e}")
            self.connected = False
            return
        
        # Stacking parameters
        self.stack_height = 0.05  # 5cm between cups
        self.gripper_open_angle = 180
        self.gripper_closed_angle = 30
        self.approach_distance = 0.02  # 2cm approach distance
        
        # Stacking positions (relative to robot base)
        self.pickup_area = {
            'x_range': (-0.15, 0.15),  # -15cm to +15cm
            'y_range': (0.20, 0.35),   # 20cm to 35cm from base
            'z_height': 0.05           # 5cm above table
        }
        
        self.stack_area = {
            'x': 0.0,      # Center of robot
            'y': 0.25,     # 25cm from base
            'z_base': 0.05 # Base height
        }
        
        # Home position for DOFBOT
        self.home_angles = [90, 90, 90, 90, 90, 30]
        
        # Move to home position on startup
        self.go_home()
    
    def go_home(self):
        """Move robot to home position"""
        if not self.connected:
            print("❌ Robot not connected")
            return
            
        print("🏠 Moving to home position...")
        self.arm.Arm_serial_servo_write6(
            self.home_angles[0], self.home_angles[1], 
            self.home_angles[2], self.home_angles[3], 
            self.home_angles[4], self.home_angles[5], 
            3000
        )
        time.sleep(3)
    
    def open_gripper(self):
        """Open the gripper"""
        if not self.connected:
            print("❌ Robot not connected")
            return
            
        print("🤏 Opening gripper...")
        self.arm.Arm_serial_servo_write(6, self.gripper_open_angle, 1000)
        time.sleep(1)
    
    def close_gripper(self):
        """Close the gripper"""
        if not self.connected:
            print("❌ Robot not connected")
            return
            
        print("🤏 Closing gripper...")
        self.arm.Arm_serial_servo_write(6, self.gripper_closed_angle, 1000)
        time.sleep(1)
    
    def convert_camera_to_robot_coords(self, cup_positions: List[Tuple[float, float, float]]) -> List[Tuple[float, float, float]]:
        """
        Convert camera coordinates to robot coordinates
        
        Args:
            cup_positions: List of (x, y, z) positions from camera (normalized 0-1)
            
        Returns:
            List of (x, y, z) positions in robot coordinates (meters)
        """
        robot_positions = []
        
        for norm_x, norm_y, norm_z in cup_positions:
            # Convert normalized coordinates to robot workspace
            # This is a simplified conversion - should be calibrated properly
            
            # X: -0.15 to 0.15 meters (left to right)
            x = (norm_x - 0.5) * 0.3
            
            # Y: 0.20 to 0.35 meters (distance from robot)
            y = 0.20 + norm_y * 0.15
            
            # Z: 0.05 to 0.15 meters (height)
            z = 0.05 + norm_z * 0.10
            
            robot_positions.append((x, y, z))
        
        return robot_positions
    
    def move_to_position(self, x: float, y: float, z: float, speed: int = 50):
        """
        Move robot to specific position using Arm_Lib
        
        Args:
            x, y, z: Target position in meters
            speed: Movement speed (0-100)
        """
        if not self.connected:
            print("❌ Robot not connected")
            return
            
        print(f"🤖 Moving to position: ({x:.3f}, {y:.3f}, {z:.3f})")
        
        # Convert to servo angles (simplified inverse kinematics)
        # This should be replaced with proper inverse kinematics
        base_angle = math.degrees(math.atan2(x, y))
        shoulder_angle = 45  # Approximate
        elbow_angle = 45     # Approximate
        wrist_rotation = 90   # Center
        wrist_pitch = 90      # Center
        
        # Move servos using Arm_Lib
        self.arm.Arm_serial_servo_write6(
            base_angle, shoulder_angle, elbow_angle,
            wrist_rotation, wrist_pitch, self.gripper_closed_angle,
            speed * 30  # Convert speed to time (ms)
        )
        
        time.sleep(2)  # Wait for movement to complete
    
    def pick_cup(self, x: float, y: float, z: float):
        """
        Pick up a cup from the specified position
        
        Args:
            x, y, z: Cup position in robot coordinates
        """
        if not self.connected:
            print("❌ Robot not connected")
            return
            
        print(f"🤏 Picking cup at ({x:.3f}, {y:.3f}, {z:.3f})")
        
        # Approach position (slightly above and back)
        approach_x = x
        approach_y = y - self.approach_distance
        approach_z = z + 0.05
        
        # Move to approach position
        self.move_to_position(approach_x, approach_y, approach_z)
        
        # Open gripper
        self.open_gripper()
        
        # Move to pickup position
        self.move_to_position(x, y, z)
        
        # Close gripper
        self.close_gripper()
        
        # Lift up
        self.move_to_position(x, y, z + 0.05)
    
    def place_cup(self, x: float, y: float, z: float):
        """
        Place a cup at the specified position
        
        Args:
            x, y, z: Target position in robot coordinates
        """
        if not self.connected:
            print("❌ Robot not connected")
            return
            
        print(f"📦 Placing cup at ({x:.3f}, {y:.3f}, {z:.3f})")
        
        # Approach position (slightly above)
        approach_x = x
        approach_y = y
        approach_z = z + 0.05
        
        # Move to approach position
        self.move_to_position(approach_x, approach_y, approach_z)
        
        # Move to placement position
        self.move_to_position(x, y, z)
        
        # Open gripper
        self.open_gripper()
        
        # Move up slightly
        self.move_to_position(x, y, z + 0.05)
        
        # Close gripper
        self.close_gripper()
    
    def execute_stack_sequence(self, cup_positions: List[Tuple[float, float, float]]):
        """
        Execute the complete cup stacking sequence
        
        Args:
            cup_positions: List of cup positions from camera
        """
        if not self.connected:
            print("❌ Robot not connected")
            return
            
        print(f"🏗️ Starting stack sequence with {len(cup_positions)} cups")
        
        # Convert camera coordinates to robot coordinates
        robot_positions = self.convert_camera_to_robot_coords(cup_positions)
        
        # Sort cups by distance from robot (closest first)
        robot_positions.sort(key=lambda pos: pos[1])  # Sort by Y coordinate
        
        # Stack cups
        stack_x = self.stack_area['x']
        stack_y = self.stack_area['y']
        stack_z = self.stack_area['z_base']
        
        for i, (cup_x, cup_y, cup_z) in enumerate(robot_positions):
            print(f"📦 Processing cup {i+1}/{len(robot_positions)}")
            
            # Pick up cup
            self.pick_cup(cup_x, cup_y, cup_z)
            
            # Place in stack
            stack_height = stack_z + (i * self.stack_height)
            self.place_cup(stack_x, stack_y, stack_height)
            
            print(f"✅ Cup {i+1} stacked at height {stack_height:.3f}m")
        
        # Return to home position
        self.go_home()
        print("🎉 Stacking sequence completed!")
    
    def test_movements(self):
        """Test basic robot movements"""
        if not self.connected:
            print("❌ Robot not connected")
            return
            
        print("🧪 Testing robot movements...")
        
        # Test home position
        self.go_home()
        
        # Test gripper
        self.open_gripper()
        time.sleep(1)
        self.close_gripper()
        time.sleep(1)
        
        # Test simple movements
        test_positions = [
            (0.0, 0.25, 0.10),   # Center, medium height
            (0.1, 0.25, 0.10),   # Right
            (-0.1, 0.25, 0.10),  # Left
            (0.0, 0.25, 0.15),   # Higher
        ]
        
        for i, pos in enumerate(test_positions):
            print(f"Testing position {i+1}: {pos}")
            self.move_to_position(*pos)
            time.sleep(2)
        
        # Return to home
        self.go_home()
        print("✅ Movement test completed!")

def main():
    """Main function for testing"""
    controller = StackingControllerArmLib()
    
    if controller.connected:
        # Test basic movements
        controller.test_movements()
        
        # Example stack sequence (simulated cup positions)
        # cup_positions = [(0.3, 0.4, 0.1), (0.7, 0.6, 0.1), (0.5, 0.5, 0.1)]
        # controller.execute_stack_sequence(cup_positions)
    else:
        print("❌ Failed to initialize robot controller")

if __name__ == "__main__":
    main() 