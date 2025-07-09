#!/usr/bin/env python3
"""
Jetson DOFBOT Pro Controller
Controls the DOFBOT Pro robotic arm running on Jetson board
"""

import time
import serial
import threading
from typing import Tuple, List, Optional
import numpy as np

class JetsonDOFBOTController:
    def __init__(self, port: str = '/dev/ttyUSB0', baudrate: int = 1000000):
        """
        Initialize the Jetson DOFBOT controller.
        
        Args:
            port: Serial port for servo communication
            baudrate: Baud rate for serial communication
        """
        self.port = port
        self.baudrate = baudrate
        self.serial: Optional[serial.Serial] = None
        self.connected = False
        
        # DOFBOT Pro servo IDs (6 servos)
        self.servo_ids = [1, 2, 3, 4, 5, 6]
        
        # Current servo positions
        self.current_positions = [90.0, 90.0, 90.0, 90.0, 90.0, 90.0]  # Default positions
        
        # Movement limits for each servo (min, max)
        self.servo_limits = [
            (0.0, 180.0),    # Base rotation
            (0.0, 180.0),    # Shoulder
            (0.0, 180.0),    # Elbow
            (0.0, 180.0),    # Wrist rotation
            (0.0, 180.0),    # Wrist pitch
            (0.0, 180.0),    # Gripper
        ]
        
    def connect(self) -> bool:
        """Connect to the DOFBOT servos."""
        try:
            print(f"🔌 Connecting to DOFBOT servos on {self.port}...")
            self.serial = serial.Serial(self.port, self.baudrate, timeout=1)
            self.connected = True
            print(f"✅ Connected to DOFBOT servos on {self.port}")
            
            # Initialize servos to default positions
            self.initialize_servos()
            return True
            
        except Exception as e:
            print(f"❌ Failed to connect to DOFBOT: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the DOFBOT."""
        if self.serial and self.serial.is_open:
            self.serial.close()
            self.connected = False
            print("Disconnected from DOFBOT")
    
    def initialize_servos(self):
        """Initialize all servos to default positions."""
        if not self.connected:
            return
            
        print("🔧 Initializing servos to default positions...")
        for i, servo_id in enumerate(self.servo_ids):
            self.move_servo(servo_id, self.current_positions[i])
            time.sleep(0.1)
        print("✅ Servos initialized")
    
    def move_servo(self, servo_id: int, angle: float, speed: int = 50):
        """
        Move a specific servo to an angle.
        
        Args:
            servo_id: Servo ID (1-6)
            angle: Target angle in degrees
            speed: Movement speed (0-100)
        """
        if not self.connected:
            print("❌ Not connected to DOFBOT")
            return False
            
        if servo_id < 1 or servo_id > 6:
            print("❌ Servo ID must be between 1 and 6")
            return False
        
        # Clamp angle to servo limits
        min_angle, max_angle = self.servo_limits[servo_id - 1]
        angle = max(min_angle, min(max_angle, angle))
        
        # Update current position
        self.current_positions[servo_id - 1] = angle
        
        # Send servo command (format depends on your servo controller)
        command = f"#{servo_id}P{int(angle)}T{int(speed * 10)}\n"
        
        try:
            if self.serial:
                self.serial.write(command.encode())
                self.serial.flush()
            return True
        except Exception as e:
            print(f"❌ Failed to move servo {servo_id}: {e}")
            return False
    
    def move_all_servos(self, angles: List[float], speed: int = 50):
        """
        Move all servos to specified angles.
        
        Args:
            angles: List of 6 angles for servos 1-6
            speed: Movement speed (0-100)
        """
        if len(angles) != 6:
            print("❌ Must provide exactly 6 angles")
            return False
            
        if not self.connected:
            print("❌ Not connected to DOFBOT")
            return False
        
        print(f"🤖 Moving all servos to angles: {angles}")
        
        # Move all servos simultaneously
        command = "#0P"
        for i, angle in enumerate(angles):
            # Clamp angle to limits
            min_angle, max_angle = self.servo_limits[i]
            clamped_angle = max(min_angle, min(max_angle, angle))
            self.current_positions[i] = clamped_angle
            command += f"{int(clamped_angle)}"
        command += f"T{int(speed * 10)}\n"
        
        try:
            if self.serial:
                self.serial.write(command.encode())
                self.serial.flush()
            return True
        except Exception as e:
            print(f"❌ Failed to move servos: {e}")
            return False
    
    def home_position(self):
        """Move to home position."""
        home_angles = [90.0, 90.0, 90.0, 90.0, 90.0, 90.0]  # Center positions
        print("🏠 Moving to home position...")
        return self.move_all_servos(home_angles)
    
    def open_gripper(self):
        """Open the gripper (servo 6)."""
        print("🤏 Opening gripper...")
        return self.move_servo(6, 180)  # Open position
    
    def close_gripper(self):
        """Close the gripper (servo 6)."""
        print("🤏 Closing gripper...")
        return self.move_servo(6, 0)  # Closed position
    
    def move_to_position(self, x: float, y: float, z: float):
        """
        Move end effector to 3D position using inverse kinematics.
        This is a simplified version - you may need to implement proper IK.
        
        Args:
            x: X coordinate
            y: Y coordinate  
            z: Z coordinate
        """
        if not self.connected:
            print("❌ Not connected to DOFBOT")
            return False
        
        print(f"🎯 Moving to position ({x}, {y}, {z})")
        
        # Simple inverse kinematics (you'll need to implement proper IK)
        # This is a placeholder - replace with actual IK calculations
        angles = self.simple_inverse_kinematics(x, y, z)
        
        if angles:
            return self.move_all_servos(angles)
        else:
            print("❌ Position unreachable")
            return False
    
    def simple_inverse_kinematics(self, x: float, y: float, z: float) -> Optional[List[float]]:
        """
        Simple inverse kinematics calculation.
        This is a placeholder - you need to implement proper IK for your DOFBOT.
        
        Args:
            x, y, z: Target position
            
        Returns:
            List of 6 servo angles or None if unreachable
        """
        # This is a simplified IK - replace with actual calculations
        # For now, return current positions as placeholder
        print("⚠️  Using placeholder IK - implement proper inverse kinematics")
        return self.current_positions.copy()
    
    def execute_stack_sequence(self, cup_positions: List[Tuple[float, float, float]]):
        """
        Execute the cup stacking sequence.
        
        Args:
            cup_positions: List of cup positions to stack
        """
        if not self.connected:
            print("❌ Not connected to DOFBOT")
            return False
            
        print(f"🎯 Executing stacking sequence for {len(cup_positions)} cups...")
        
        # Move to home position first
        self.home_position()
        time.sleep(2)
        
        # Define stack position
        stack_x, stack_y, stack_z = 150, 150, 50
        
        for i, (x, y, z) in enumerate(cup_positions):
            print(f"📦 Stacking cup {i+1}/{len(cup_positions)} at position ({x}, {y}, {z})")
            
            # Approach from above
            self.move_to_position(x, y, z + 30)
            time.sleep(1)
            
            # Open gripper
            self.open_gripper()
            time.sleep(0.5)
            
            # Move down to cup
            self.move_to_position(x, y, z)
            time.sleep(1)
            
            # Close gripper to grab cup
            self.close_gripper()
            time.sleep(1)
            
            # Lift cup
            self.move_to_position(x, y, z + 50)
            time.sleep(1)
            
            # Move to stack position
            self.move_to_position(stack_x, stack_y, stack_z + 50)
            time.sleep(1)
            
            # Lower to stack
            self.move_to_position(stack_x, stack_y, stack_z)
            time.sleep(1)
            
            # Release cup
            self.open_gripper()
            time.sleep(0.5)
            
            # Move up
            self.move_to_position(stack_x, stack_y, stack_z + 50)
            time.sleep(1)
        
        # Return to home position
        self.home_position()
        print("✅ Stacking sequence completed!")
        
        return True
    
    def get_current_positions(self) -> List[float]:
        """Get current servo positions."""
        return self.current_positions.copy()
    
    def set_servo_limits(self, servo_id: int, min_angle: float, max_angle: float):
        """Set movement limits for a servo."""
        if 1 <= servo_id <= 6:
            self.servo_limits[servo_id - 1] = (min_angle, max_angle)
            print(f"✅ Set servo {servo_id} limits: {min_angle}° to {max_angle}°")
        else:
            print("❌ Invalid servo ID")

if __name__ == "__main__":
    print("🤖 Testing Jetson DOFBOT Controller...")
    robot = JetsonDOFBOTController()
    
    if robot.connect():
        print("✅ Connection test successful!")
        
        # Test basic movements
        print("\n🧪 Testing basic movements...")
        robot.home_position()
        time.sleep(2)
        
        robot.open_gripper()
        time.sleep(1)
        
        robot.close_gripper()
        time.sleep(1)
        
        robot.disconnect()
    else:
        print("❌ Connection test failed.") 