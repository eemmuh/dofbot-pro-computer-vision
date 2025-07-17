#!/usr/bin/env python3
"""
Cup Stacking Controller for DOFBOT Pro
Implements basic stacking logic and robot movements
"""
import time
import math
from typing import List, Tuple, Optional
from .dofbot_controller import DOFBOTController

class StackingController:
    def __init__(self, robot: DOFBOTController):
        """
        Initialize stacking controller with robot instance
        
        Args:
            robot: Initialized DOFBOT controller
        """
        self.robot = robot
        
        # Stacking parameters
        self.stack_height = 0.05  # 5cm between cups
        self.gripper_open_angle = 90
        self.gripper_closed_angle = 0
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
        Move robot to specific position
        
        Args:
            x, y, z: Target position in meters
            speed: Movement speed (0-100)
        """
        print(f"🤖 Moving to position: ({x:.3f}, {y:.3f}, {z:.3f})")
        
        # Convert to servo angles (simplified inverse kinematics)
        # This should be replaced with proper inverse kinematics
        base_angle = math.degrees(math.atan2(x, y))
        shoulder_angle = 45  # Approximate
        elbow_angle = 45     # Approximate
        
        # Move servos
        self.robot.set_servo_position(1, base_angle, speed)
        self.robot.set_servo_position(2, shoulder_angle, speed)
        self.robot.set_servo_position(3, elbow_angle, speed)
        
        time.sleep(2)  # Wait for movement to complete
    
    def pick_cup(self, x: float, y: float, z: float):
        """
        Pick up a cup from the specified position
        
        Args:
            x, y, z: Cup position in robot coordinates
        """
        print(f"🤏 Picking cup at ({x:.3f}, {y:.3f}, {z:.3f})")
        
        # Approach position (slightly above and back)
        approach_x = x
        approach_y = y - self.approach_distance
        approach_z = z + 0.05
        
        # Move to approach position
        self.move_to_position(approach_x, approach_y, approach_z)
        
        # Open gripper
        self.robot.set_servo_position(5, self.gripper_open_angle, 50)
        time.sleep(1)
        
        # Move to cup position
        self.move_to_position(x, y, z)
        
        # Close gripper
        self.robot.set_servo_position(5, self.gripper_closed_angle, 50)
        time.sleep(1)
        
        # Lift cup
        self.move_to_position(x, y, z + 0.05)
        
        print("✅ Cup picked successfully")
    
    def place_cup(self, x: float, y: float, z: float):
        """
        Place a cup at the specified position
        
        Args:
            x, y, z: Target position in robot coordinates
        """
        print(f"📦 Placing cup at ({x:.3f}, {y:.3f}, {z:.3f})")
        
        # Move to placement position
        self.move_to_position(x, y, z + 0.05)
        
        # Lower to placement height
        self.move_to_position(x, y, z)
        
        # Open gripper
        self.robot.set_servo_position(5, self.gripper_open_angle, 50)
        time.sleep(1)
        
        # Lift gripper
        self.move_to_position(x, y, z + 0.05)
        
        print("✅ Cup placed successfully")
    
    def execute_stack_sequence(self, cup_positions: List[Tuple[float, float, float]]):
        """
        Execute the complete stacking sequence
        
        Args:
            cup_positions: List of cup positions from camera
        """
        print("🚀 Starting Cup Stacking Sequence")
        print(f"📊 Found {len(cup_positions)} cups to stack")
        
        if not cup_positions:
            print("❌ No cups detected")
            return
        
        # Convert camera coordinates to robot coordinates
        robot_positions = self.convert_camera_to_robot_coords(cup_positions)
        
        # Sort cups by distance from robot (closest first)
        robot_positions.sort(key=lambda pos: pos[1])  # Sort by Y coordinate
        
        # Stack cups
        for i, (x, y, z) in enumerate(robot_positions):
            print(f"\n🥤 Processing cup {i+1}/{len(robot_positions)}")
            
            # Pick up cup
            self.pick_cup(x, y, z)
            
            # Place in stack
            stack_x = self.stack_area['x']
            stack_y = self.stack_area['y']
            stack_z = self.stack_area['z_base'] + (i * self.stack_height)
            
            self.place_cup(stack_x, stack_y, stack_z)
            
            print(f"✅ Cup {i+1} stacked at height {stack_z:.3f}m")
        
        # Return to home position
        print("\n🏠 Returning to home position")
        self.robot.home_position()
        
        print(f"🎉 Stacking complete! Stacked {len(robot_positions)} cups")
    
    def test_movements(self):
        """
        Test basic robot movements
        """
        print("🧪 Testing Robot Movements")
        
        # Test home position
        print("1. Going to home position...")
        self.robot.home_position()
        time.sleep(2)
        
        # Test gripper
        print("2. Testing gripper...")
        self.robot.set_servo_position(5, self.gripper_open_angle, 50)
        time.sleep(1)
        self.robot.set_servo_position(5, self.gripper_closed_angle, 50)
        time.sleep(1)
        
        # Test simple movement
        print("3. Testing movement...")
        self.move_to_position(0.1, 0.25, 0.1)
        time.sleep(2)
        
        # Return home
        self.robot.home_position()
        
        print("✅ Movement test completed") 