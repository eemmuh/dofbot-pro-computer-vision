#!/usr/bin/env python3
"""
GPIO DOFBOT Pro Controller
Controls the DOFBOT Pro using GPIO PWM signals for servo control
"""

import time
import threading
from typing import Tuple, List, Optional
import numpy as np

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    print("⚠️  RPi.GPIO not available - using simulation mode")

class GPIODOFBOTController:
    def __init__(self):
        """
        Initialize the GPIO DOFBOT controller.
        Uses PWM signals on GPIO pins to control servos directly.
        """
        self.connected = False
        
        # DOFBOT Pro servo GPIO pins (you may need to adjust these)
        self.servo_pins = {
            1: 18,  # Base rotation
            2: 19,  # Shoulder
            3: 20,  # Elbow
            4: 21,  # Wrist rotation
            5: 22,  # Wrist pitch
            6: 23,  # Gripper
        }
        
        # PWM objects for each servo
        self.pwm_objects = {}
        
        # Current servo positions (0-180 degrees)
        self.current_positions = [90.0, 90.0, 90.0, 90.0, 90.0, 90.0]
        
        # Servo limits (min, max) in degrees
        self.servo_limits = [
            (0.0, 180.0),    # Base rotation
            (0.0, 180.0),    # Shoulder
            (0.0, 180.0),    # Elbow
            (0.0, 180.0),    # Wrist rotation
            (0.0, 180.0),    # Wrist pitch
            (0.0, 180.0),    # Gripper
        ]
        
        # PWM frequency (50Hz is standard for servos)
        self.pwm_freq = 50
        
    def connect(self) -> bool:
        """Initialize GPIO and PWM for servo control."""
        if not GPIO_AVAILABLE:
            print("❌ RPi.GPIO not available - cannot control servos")
            return False
            
        try:
            print("🔌 Initializing GPIO for DOFBOT servos...")
            
            # Set GPIO mode
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            
            # Initialize PWM for each servo
            for servo_id, pin in self.servo_pins.items():
                GPIO.setup(pin, GPIO.OUT)
                pwm = GPIO.PWM(pin, self.pwm_freq)
                pwm.start(0)  # Start with 0% duty cycle
                self.pwm_objects[servo_id] = pwm
                print(f"✅ Initialized servo {servo_id} on GPIO {pin}")
            
            self.connected = True
            print("✅ GPIO DOFBOT controller initialized successfully")
            
            # Initialize servos to default positions
            self.initialize_servos()
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize GPIO: {e}")
            return False
    
    def disconnect(self):
        """Clean up GPIO."""
        if self.connected and GPIO_AVAILABLE:
            try:
                # Stop all PWM
                for pwm in self.pwm_objects.values():
                    pwm.stop()
                
                # Clean up GPIO
                GPIO.cleanup()
                self.connected = False
                print("✅ GPIO cleaned up")
            except Exception as e:
                print(f"❌ Error cleaning up GPIO: {e}")
    
    def angle_to_duty_cycle(self, angle: float) -> float:
        """
        Convert angle (0-180) to duty cycle (0-100).
        Servos typically use 1-2ms pulse width (5-10% duty cycle at 50Hz).
        """
        # Map 0-180 degrees to 2.5-12.5% duty cycle
        # This gives 0.5ms to 2.5ms pulse width
        duty_cycle = 2.5 + (angle / 180.0) * 10.0
        return max(0.0, min(100.0, duty_cycle))
    
    def move_servo(self, servo_id: int, angle: float, speed: float = 1.0):
        """
        Move a specific servo to an angle.
        
        Args:
            servo_id: Servo ID (1-6)
            angle: Target angle in degrees (0-180)
            speed: Movement speed (0.1-1.0)
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
        
        # Get current and target positions
        current_angle = self.current_positions[servo_id - 1]
        target_angle = angle
        
        print(f"🤖 Moving servo {servo_id} from {current_angle:.1f}° to {target_angle:.1f}°")
        
        if GPIO_AVAILABLE and servo_id in self.pwm_objects:
            # Smooth movement
            steps = int(abs(target_angle - current_angle) / speed)
            if steps > 0:
                step_size = (target_angle - current_angle) / steps
                
                for i in range(steps + 1):
                    current_pos = current_angle + (step_size * i)
                    duty_cycle = self.angle_to_duty_cycle(current_pos)
                    self.pwm_objects[servo_id].ChangeDutyCycle(duty_cycle)
                    time.sleep(0.02)  # 20ms delay for smooth movement
            
            # Update current position
            self.current_positions[servo_id - 1] = target_angle
            return True
        else:
            print(f"⚠️  Servo {servo_id} not available - simulation mode")
            self.current_positions[servo_id - 1] = target_angle
            return True
    
    def move_all_servos(self, angles: List[float], speed: float = 1.0):
        """
        Move all servos to specified angles.
        
        Args:
            angles: List of 6 angles for servos 1-6
            speed: Movement speed (0.1-1.0)
        """
        if len(angles) != 6:
            print("❌ Must provide exactly 6 angles")
            return False
            
        if not self.connected:
            print("❌ Not connected to DOFBOT")
            return False
        
        print(f"🤖 Moving all servos to angles: {angles}")
        
        # Move all servos simultaneously
        for i, angle in enumerate(angles):
            servo_id = i + 1
            self.move_servo(servo_id, angle, speed)
        
        return True
    
    def initialize_servos(self):
        """Initialize all servos to default positions."""
        if not self.connected:
            return
            
        print("🔧 Initializing servos to default positions...")
        for i, servo_id in enumerate(self.servo_pins.keys()):
            self.move_servo(servo_id, self.current_positions[i])
            time.sleep(0.1)
        print("✅ Servos initialized")
    
    def home_position(self):
        """Move to home position."""
        home_angles = [90.0, 90.0, 90.0, 90.0, 90.0, 90.0]
        print("🏠 Moving to home position...")
        return self.move_all_servos(home_angles)
    
    def open_gripper(self):
        """Open the gripper (servo 6)."""
        print("🤏 Opening gripper...")
        return self.move_servo(6, 180.0)
    
    def close_gripper(self):
        """Close the gripper (servo 6)."""
        print("🤏 Closing gripper...")
        return self.move_servo(6, 0.0)
    
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
    print("🤖 Testing GPIO DOFBOT Controller...")
    robot = GPIODOFBOTController()
    
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