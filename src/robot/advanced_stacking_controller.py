#!/usr/bin/env python3
"""
Advanced Cup Stacking Controller
Implements sophisticated stacking algorithms and patterns
"""

import time
import math
import numpy as np
from typing import List, Tuple, Optional, Dict, Any
from enum import Enum
from .dofbot_controller import DOFBOTController

class StackingPattern(Enum):
    """Different stacking patterns"""
    TOWER = "tower"           # Simple vertical stack
    PYRAMID = "pyramid"       # Pyramid formation
    CUSTOM = "custom"         # Custom arrangement
    SPIRAL = "spiral"         # Spiral pattern

class AdvancedStackingController:
    def __init__(self, robot: DOFBOTController):
        """
        Initialize advanced stacking controller
        
        Args:
            robot: Initialized DOFBOT controller
        """
        self.robot = robot
        
        # Physical parameters
        self.cup_diameter = 0.08  # 8cm cup diameter
        self.cup_height = 0.12    # 12cm cup height
        self.gripper_offset = 0.02  # 2cm gripper offset
        
        # Workspace parameters
        self.workspace_bounds = {
            'x': (-0.15, 0.15),   # Left/right limits
            'y': (0.20, 0.35),    # Distance from robot
            'z': (0.05, 0.25)     # Height limits
        }
        
        # Stacking area
        self.stack_center = (0.0, 0.25, 0.05)  # Center of stacking area
        
        # Movement parameters
        self.approach_height = 0.05  # 5cm above target
        self.pickup_speed = 50
        self.placement_speed = 30
        
        # Current stack state
        self.stack_history = []
        self.current_pattern = StackingPattern.TOWER
        
    def set_stacking_pattern(self, pattern: StackingPattern):
        """Set the stacking pattern"""
        self.current_pattern = pattern
        print(f"🎯 Stacking pattern set to: {pattern.value}")
    
    def calculate_stack_positions(self, num_cups: int, pattern: StackingPattern = None) -> List[Tuple[float, float, float]]:
        """
        Calculate positions for stacking cups in the specified pattern
        
        Args:
            num_cups: Number of cups to stack
            pattern: Stacking pattern (uses current pattern if None)
            
        Returns:
            List of (x, y, z) positions for each cup
        """
        if pattern is None:
            pattern = self.current_pattern
        
        positions = []
        base_x, base_y, base_z = self.stack_center
        
        if pattern == StackingPattern.TOWER:
            # Simple vertical stack
            for i in range(num_cups):
                z = base_z + (i * self.cup_height)
                positions.append((base_x, base_y, z))
                
        elif pattern == StackingPattern.PYRAMID:
            # Pyramid formation
            layer = 0
            cups_placed = 0
            
            while cups_placed < num_cups:
                cups_in_layer = min(layer + 1, num_cups - cups_placed)
                layer_width = cups_in_layer * self.cup_diameter
                
                # Center the layer
                start_x = base_x - (layer_width - self.cup_diameter) / 2
                
                for cup_in_layer in range(cups_in_layer):
                    x = start_x + (cup_in_layer * self.cup_diameter)
                    y = base_y
                    z = base_z + (layer * self.cup_height)
                    positions.append((x, y, z))
                    cups_placed += 1
                
                layer += 1
                
        elif pattern == StackingPattern.SPIRAL:
            # Spiral pattern
            radius = 0.02  # 2cm radius
            angle_step = 2 * math.pi / 6  # 6 cups per circle
            
            for i in range(num_cups):
                angle = i * angle_step
                radius_current = radius + (i // 6) * 0.01  # Increase radius every 6 cups
                
                x = base_x + radius_current * math.cos(angle)
                y = base_y + radius_current * math.sin(angle)
                z = base_z + (i // 6) * self.cup_height
                
                positions.append((x, y, z))
                
        elif pattern == StackingPattern.CUSTOM:
            # Custom arrangement - grid pattern
            grid_size = math.ceil(math.sqrt(num_cups))
            spacing = self.cup_diameter * 1.2  # 20% spacing between cups
            
            for i in range(num_cups):
                row = i // grid_size
                col = i % grid_size
                
                x = base_x + (col - grid_size/2) * spacing
                y = base_y + (row - grid_size/2) * spacing
                z = base_z
                
                positions.append((x, y, z))
        
        return positions
    
    def optimize_pickup_order(self, cup_positions: List[Tuple[float, float, float]]) -> List[int]:
        """
        Optimize the order of cup pickup for efficiency
        
        Args:
            cup_positions: List of cup positions from camera
            
        Returns:
            List of indices in optimal pickup order
        """
        if not cup_positions:
            return []
        
        # Convert to robot coordinates
        robot_positions = self.convert_camera_to_robot_coords(cup_positions)
        
        # Calculate distances from current robot position
        current_pos = (0, 0, 0)  # Approximate current position
        distances = []
        
        for i, pos in enumerate(robot_positions):
            dist = math.sqrt(sum((a - b) ** 2 for a, b in zip(pos, current_pos)))
            distances.append((dist, i))
        
        # Sort by distance (closest first)
        distances.sort()
        return [idx for _, idx in distances]
    
    def convert_camera_to_robot_coords(self, cup_positions: List[Tuple[float, float, float]]) -> List[Tuple[float, float, float]]:
        """
        Convert camera coordinates to robot coordinates with calibration
        
        Args:
            cup_positions: List of (x, y, z) positions from camera (normalized 0-1)
            
        Returns:
            List of (x, y, z) positions in robot coordinates (meters)
        """
        robot_positions = []
        
        for norm_x, norm_y, norm_z in cup_positions:
            # Convert normalized coordinates to robot workspace
            # This uses the workspace bounds defined in __init__
            
            x_min, x_max = self.workspace_bounds['x']
            y_min, y_max = self.workspace_bounds['y']
            z_min, z_max = self.workspace_bounds['z']
            
            # X: Left to right
            x = x_min + norm_x * (x_max - x_min)
            
            # Y: Distance from robot (inverted for camera)
            y = y_min + (1 - norm_y) * (y_max - y_min)
            
            # Z: Height (larger cups = closer = higher Z)
            z = z_min + norm_z * (z_max - z_min)
            
            robot_positions.append((x, y, z))
        
        return robot_positions
    
    def inverse_kinematics(self, x: float, y: float, z: float) -> Tuple[float, float, float, float, float]:
        """
        Calculate inverse kinematics for the robot arm
        
        Args:
            x, y, z: Target position in meters
            
        Returns:
            Tuple of (base, shoulder, elbow, wrist_rot, wrist_pitch) angles in degrees
        """
        # Simplified inverse kinematics for DOFBOT Pro
        # This should be replaced with proper IK calculations
        
        # Base rotation
        base_angle = math.degrees(math.atan2(x, y))
        
        # Calculate arm length and angles
        arm_length = math.sqrt(x**2 + y**2)
        target_height = z
        
        # Simplified shoulder and elbow calculation
        # This is a basic approximation - should use proper IK
        shoulder_angle = 45 + (target_height - 0.1) * 100  # Approximate
        elbow_angle = 90 - shoulder_angle  # Approximate
        
        # Wrist angles (simplified)
        wrist_rot = 90
        wrist_pitch = 90
        
        return (base_angle, shoulder_angle, elbow_angle, wrist_rot, wrist_pitch)
    
    def move_to_position_smooth(self, x: float, y: float, z: float, speed: int = 50):
        """
        Move robot to position with smooth motion
        
        Args:
            x, y, z: Target position in meters
            speed: Movement speed (0-100)
        """
        print(f"🤖 Moving to position: ({x:.3f}, {y:.3f}, {z:.3f})")
        
        # Calculate inverse kinematics
        base, shoulder, elbow, wrist_rot, wrist_pitch = self.inverse_kinematics(x, y, z)
        
        # Move servos with smooth motion
        self.robot.set_servo_position(1, base, speed)
        time.sleep(0.1)
        self.robot.set_servo_position(2, shoulder, speed)
        time.sleep(0.1)
        self.robot.set_servo_position(3, elbow, speed)
        time.sleep(0.1)
        self.robot.set_servo_position(4, wrist_rot, speed)
        time.sleep(0.1)
        self.robot.set_servo_position(5, wrist_pitch, speed)
        
        # Wait for movement to complete
        time.sleep(2)
    
    def pick_cup_precise(self, x: float, y: float, z: float):
        """
        Pick up a cup with precise positioning
        
        Args:
            x, y, z: Cup position in robot coordinates
        """
        print(f"🤏 Picking cup at ({x:.3f}, {y:.3f}, {z:.3f})")
        
        # Approach position (above and slightly back)
        approach_x = x
        approach_y = y - 0.02  # 2cm back
        approach_z = z + self.approach_height
        
        # Move to approach position
        self.move_to_position_smooth(approach_x, approach_y, approach_z, self.pickup_speed)
        
        # Open gripper
        self.robot.open_gripper()
        time.sleep(1)
        
        # Move to cup position
        self.move_to_position_smooth(x, y, z, self.pickup_speed)
        
        # Close gripper
        self.robot.close_gripper()
        time.sleep(1)
        
        # Verify grip (check if gripper closed properly)
        gripper_pos = self.robot.read_servo_position(6)
        if gripper_pos and gripper_pos > 50:  # If gripper is too open
            print("⚠️ Gripper may not have closed properly")
        
        # Lift cup
        self.move_to_position_smooth(x, y, z + self.approach_height, self.pickup_speed)
        
        print("✅ Cup picked successfully")
    
    def place_cup_precise(self, x: float, y: float, z: float):
        """
        Place a cup with precise positioning
        
        Args:
            x, y, z: Target position in robot coordinates
        """
        print(f"📦 Placing cup at ({x:.3f}, {y:.3f}, {z:.3f})")
        
        # Move to placement position (above target)
        self.move_to_position_smooth(x, y, z + self.approach_height, self.placement_speed)
        
        # Lower to placement height
        self.move_to_position_smooth(x, y, z, self.placement_speed)
        
        # Open gripper
        self.robot.open_gripper()
        time.sleep(1)
        
        # Lift gripper
        self.move_to_position_smooth(x, y, z + self.approach_height, self.placement_speed)
        
        # Record placement
        self.stack_history.append({
            'position': (x, y, z),
            'timestamp': time.time(),
            'pattern': self.current_pattern.value
        })
        
        print("✅ Cup placed successfully")
    
    def execute_advanced_stack_sequence(self, cup_positions: List[Tuple[float, float, float]], 
                                      pattern: StackingPattern = None):
        """
        Execute advanced stacking sequence with pattern selection
        
        Args:
            cup_positions: List of cup positions from camera
            pattern: Stacking pattern (uses current pattern if None)
        """
        if pattern:
            self.set_stacking_pattern(pattern)
        
        print(f"🚀 Starting Advanced Stacking Sequence")
        print(f"📊 Pattern: {self.current_pattern.value}")
        print(f"📊 Cups to stack: {len(cup_positions)}")
        
        if not cup_positions:
            print("❌ No cups detected")
            return
        
        try:
            # Optimize pickup order
            pickup_order = self.optimize_pickup_order(cup_positions)
            print(f"🎯 Optimized pickup order: {pickup_order}")
            
            # Calculate stack positions
            stack_positions = self.calculate_stack_positions(len(cup_positions), self.current_pattern)
            print(f"📐 Calculated {len(stack_positions)} stack positions")
            
            # Convert camera coordinates to robot coordinates
            robot_positions = self.convert_camera_to_robot_coords(cup_positions)
            
            # Execute stacking sequence
            for i, pickup_idx in enumerate(pickup_order):
                print(f"\n🥤 Processing cup {i+1}/{len(cup_positions)}")
                
                # Pick up cup
                pickup_x, pickup_y, pickup_z = robot_positions[pickup_idx]
                self.pick_cup_precise(pickup_x, pickup_y, pickup_z)
                
                # Place in stack
                stack_x, stack_y, stack_z = stack_positions[i]
                self.place_cup_precise(stack_x, stack_y, stack_z)
                
                print(f"✅ Cup {i+1} stacked at height {stack_z:.3f}m")
            
            # Return to home position
            print("\n🏠 Returning to home position")
            self.robot.home_position()
            
            print(f"🎉 Advanced stacking complete!")
            print(f"📊 Pattern: {self.current_pattern.value}")
            print(f"📊 Cups stacked: {len(cup_positions)}")
            print(f"📊 Total stacks: {len(self.stack_history)}")
            
        except Exception as e:
            print(f"❌ Advanced stacking sequence failed: {e}")
            # Try to return to home position
            try:
                self.robot.home_position()
            except:
                print("⚠️ Failed to return to home position")
    
    def get_stack_statistics(self) -> Dict[str, Any]:
        """Get statistics about stacking performance"""
        if not self.stack_history:
            return {"message": "No stacking history available"}
        
        total_cups = len(self.stack_history)
        patterns_used = {}
        
        for record in self.stack_history:
            pattern = record['pattern']
            patterns_used[pattern] = patterns_used.get(pattern, 0) + 1
        
        return {
            "total_cups_stacked": total_cups,
            "patterns_used": patterns_used,
            "current_pattern": self.current_pattern.value,
            "last_stack_time": self.stack_history[-1]['timestamp'] if self.stack_history else None
        }
    
    def clear_stack_history(self):
        """Clear stacking history"""
        self.stack_history.clear()
        print("🗑️ Stacking history cleared")
    
    def test_patterns(self):
        """Test different stacking patterns with simulation"""
        print("🧪 Testing Stacking Patterns")
        
        test_cups = 6  # Test with 6 cups
        
        for pattern in StackingPattern:
            print(f"\n🎯 Testing {pattern.value} pattern...")
            positions = self.calculate_stack_positions(test_cups, pattern)
            
            print(f"📐 Generated {len(positions)} positions:")
            for i, (x, y, z) in enumerate(positions):
                print(f"  Cup {i+1}: ({x:.3f}, {y:.3f}, {z:.3f})")
        
        print("\n✅ Pattern testing completed")
    
    def calibrate_camera(self):
        """Calibrate camera to robot coordinate system"""
        print("🎯 Camera Calibration")
        print("This would implement camera calibration using known reference points")
        print("For now, using simplified coordinate conversion")
        
        # TODO: Implement proper camera calibration
        # This would involve:
        # 1. Placing known reference objects
        # 2. Measuring their positions
        # 3. Calculating transformation matrix
        # 4. Storing calibration parameters
        
        print("⚠️ Camera calibration not implemented - using simplified conversion") 