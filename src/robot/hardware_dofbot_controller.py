#!/usr/bin/env python3
"""
Hardware DOFBOT Pro Controller
Direct hardware control using Arm_Lib (the actual DOFBOT control library)
"""

import time
import sys
import os
from typing import Tuple, List, Optional

# Add Arm_Lib to path
sys.path.append('/home/jetson/software/Arm_Lib')

try:
    from Arm_Lib import Arm_Device
    ARM_LIB_AVAILABLE = True
except ImportError:
    ARM_LIB_AVAILABLE = False
    print("⚠️  Arm_Lib not available - using simulation mode")

class HardwareDOFBOTController:
    def __init__(self):
        """
        Initialize the hardware DOFBOT controller.
        Uses the actual Arm_Lib to control servos directly.
        """
        self.connected = False
        self.arm = None
        
        # Current servo positions (in degrees)
        self.current_positions = [90.0, 90.0, 90.0, 90.0, 90.0, 90.0]
        
        # Servo limits (in degrees) - typical DOFBOT limits
        self.servo_limits = [
            (0.0, 180.0),    # Base rotation
            (0.0, 180.0),    # Shoulder
            (0.0, 180.0),    # Elbow
            (0.0, 180.0),    # Wrist rotation
            (0.0, 180.0),    # Wrist pitch
            (0.0, 180.0),    # Gripper
        ]
        
    def connect(self) -> bool:
        """Initialize connection to DOFBOT hardware."""
        if not ARM_LIB_AVAILABLE:
            print("❌ Arm_Lib not available - cannot control DOFBOT")
            return False
            
        try:
            print("🔌 Initializing DOFBOT hardware connection...")
            
            # Create Arm_Device object
            self.arm = Arm_Device()
            time.sleep(0.1)  # Give it time to initialize
            
            # Test connection by reading servo positions
            if self.read_current_positions():
                self.connected = True
                print("✅ Connected to DOFBOT hardware successfully")
                
                # Initialize to home position
                self.initialize_servos()
                return True
            else:
                print("❌ Failed to read servo positions")
                return False
                
        except Exception as e:
            print(f"❌ Failed to initialize DOFBOT hardware: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from DOFBOT hardware."""
        if self.connected and self.arm:
            try:
                # Clean up Arm_Device object
                del self.arm
                self.connected = False
                print("✅ Disconnected from DOFBOT hardware")
            except Exception as e:
                print(f"❌ Error disconnecting: {e}")
    
    def read_current_positions(self) -> Optional[List[float]]:
        """Read current servo positions from hardware."""
        if not self.connected or not self.arm:
            return None
            
        try:
            # Read all servo positions
            positions = []
            for servo_id in range(1, 7):
                pos = self.arm.Arm_serial_servo_read(servo_id)
                if pos is not None:
                    positions.append(float(pos))
                else:
                    print(f"❌ Failed to read servo {servo_id}")
                    return None
            
            self.current_positions = positions
            return positions
            
        except Exception as e:
            print(f"Error reading servo positions: {e}")
            return None
    
    def move_servo(self, servo_id: int, angle_degrees: float, speed: int = 500):
        """
        Move a specific servo to an angle.
        
        Args:
            servo_id: Servo ID (1-6)
            angle_degrees: Target angle in degrees
            speed: Movement speed in milliseconds
        """
        if not self.connected or not self.arm:
            print("❌ Not connected to DOFBOT")
            return False
            
        if servo_id < 1 or servo_id > 6:
            print("❌ Servo ID must be between 1 and 6")
            return False
        
        # Clamp angle to servo limits
        min_angle, max_angle = self.servo_limits[servo_id - 1]
        angle_degrees = max(min_angle, min(max_angle, angle_degrees))
        
        print(f"🤖 Moving servo {servo_id} to {angle_degrees:.1f}° (speed: {speed}ms)")
        
        try:
            # Send servo command
            result = self.arm.Arm_serial_servo_write(servo_id, int(angle_degrees), speed)
            
            if result:
                # Update current position
                self.current_positions[servo_id - 1] = angle_degrees
                print(f"✅ Servo {servo_id} moved successfully")
                return True
            else:
                print(f"❌ Failed to move servo {servo_id}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to move servo {servo_id}: {e}")
            return False
    
    def move_all_servos(self, angles_degrees: List[float], speed: int = 500):
        """
        Move all servos to specified angles.
        
        Args:
            angles_degrees: List of 6 angles in degrees
            speed: Movement speed in milliseconds
        """
        if len(angles_degrees) != 6:
            print("❌ Must provide exactly 6 angles")
            return False
            
        if not self.connected or not self.arm:
            print("❌ Not connected to DOFBOT")
            return False
        
        print(f"🤖 Moving all servos to angles: {angles_degrees}")
        
        try:
            # Clamp angles to servo limits
            clamped_angles = []
            for i, angle in enumerate(angles_degrees):
                min_angle, max_angle = self.servo_limits[i]
                clamped_angles.append(max(min_angle, min(max_angle, angle)))
            
            # Move all servos
            success = True
            for i, angle in enumerate(clamped_angles):
                servo_id = i + 1
                if not self.move_servo(servo_id, angle, speed):
                    success = False
            
            if success:
                print("✅ All servos moved successfully")
                return True
            else:
                print("❌ Some servos failed to move")
                return False
                
        except Exception as e:
            print(f"❌ Failed to move servos: {e}")
            return False
    
    def initialize_servos(self):
        """Initialize all servos to default positions."""
        if not self.connected:
            return
            
        print("🔧 Initializing servos to default positions...")
        home_angles = [90.0, 90.0, 90.0, 90.0, 90.0, 90.0]  # Home position
        self.move_all_servos(home_angles)
        time.sleep(2)
        print("✅ Servos initialized")
    
    def home_position(self):
        """Move to home position."""
        home_angles = [90.0, 90.0, 90.0, 90.0, 90.0, 90.0]
        print("🏠 Moving to home position...")
        return self.move_all_servos(home_angles)
    
    def open_gripper(self):
        """Open the gripper (servo 6)."""
        print("🤏 Opening gripper...")
        return self.move_servo(6, 180.0)  # Open position
    
    def close_gripper(self):
        """Close the gripper (servo 6)."""
        print("🤏 Closing gripper...")
        return self.move_servo(6, 0.0)  # Closed position
    
    def execute_stack_sequence(self, cup_positions: List[Tuple[float, float, float]]):
        """
        Execute the cup stacking sequence.
        This is a simplified version - you'll need to implement proper inverse kinematics.
        
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
        
        # For now, just test basic movements
        print("🧪 Testing basic movements for stacking...")
        
        # Test gripper
        self.open_gripper()
        time.sleep(1)
        self.close_gripper()
        time.sleep(1)
        
        # Test some joint movements
        self.move_servo(1, 45.0)   # Base rotation
        time.sleep(1)
        self.move_servo(1, 135.0)  # Base rotation
        time.sleep(1)
        self.move_servo(1, 90.0)   # Back to center
        time.sleep(1)
        
        # Return to home position
        self.home_position()
        print("✅ Stacking sequence completed!")
        
        return True
    
    def get_current_positions(self) -> List[float]:
        """Get current servo positions in degrees."""
        return self.current_positions.copy()

if __name__ == "__main__":
    print("🤖 Testing Hardware DOFBOT Controller...")
    robot = HardwareDOFBOTController()
    
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
        
        # Test individual servo movements
        print("\n🧪 Testing individual servo movements...")
        for servo_id in range(1, 7):
            print(f"Testing servo {servo_id}...")
            robot.move_servo(servo_id, 45.0)
            time.sleep(1)
            robot.move_servo(servo_id, 135.0)
            time.sleep(1)
            robot.move_servo(servo_id, 90.0)
            time.sleep(1)
        
        robot.disconnect()
    else:
        print("❌ Connection test failed.") 