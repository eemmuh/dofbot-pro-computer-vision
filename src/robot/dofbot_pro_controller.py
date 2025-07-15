#!/usr/bin/env python3
"""
DOFBOT Pro ROS Controller
Controls the DOFBOT Pro using ROS (Robot Operating System)
"""

import time
import threading
from typing import Tuple, List, Optional
import numpy as np

try:
    import rospy
    import sys
    import os

    # Add DOFBOT Pro workspace to path
    sys.path.append('/home/jetson/dofbot_pro_ws/devel/lib/python3/dist-packages')

    from dofbot_pro_info.srv import dofbot_pro_kinemarics, dofbot_pro_kinemaricsRequest, dofbot_pro_kinemaricsResponse
    ROS_AVAILABLE = True
except ImportError:
    ROS_AVAILABLE = False
    print("⚠️  ROS not available - using simulation mode")

class DOFBOTProController:
    def __init__(self):
        """
        Initialize the DOFBOT Pro controller.
        Uses the actual DOFBOT Pro kinematics services.
        """
        self.connected = False
        self.ros_initialized = False
        
        # ROS service proxies
        self.kinematics_service = None
        
        # Current joint positions (in degrees)
        self.current_positions = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        
        # Joint limits (in degrees) - DOFBOT Pro specific
        self.joint_limits = [
            (-180.0, 180.0),   # Base rotation
            (-90.0, 90.0),     # Shoulder
            (-90.0, 90.0),     # Elbow
            (-180.0, 180.0),   # Wrist rotation
            (-90.0, 90.0),     # Wrist pitch
            (0.0, 180.0),      # Gripper
        ]
        
    def connect(self) -> bool:
        """Initialize ROS and connect to DOFBOT Pro."""
        if not ROS_AVAILABLE:
            print("❌ ROS not available - cannot control DOFBOT Pro")
            return False
            
        try:
            print("🔌 Initializing ROS for DOFBOT Pro...")
            
            # Initialize ROS node
            rospy.init_node('dofbot_pro_cup_stacking_controller', anonymous=True)
            self.ros_initialized = True
            
            # Wait for DOFBOT Pro services to be available
            print("⏳ Waiting for DOFBOT Pro ROS services...")
            rospy.wait_for_service('/get_kinemarics')
            
            # Create service proxy
            self.kinematics_service = rospy.ServiceProxy('/get_kinemarics', dofbot_pro_kinemarics)
            
            # Test connection by getting current position
            if self.get_current_position():
                self.connected = True
                print("✅ Connected to DOFBOT Pro via ROS")
                
                # Initialize to home position
                self.initialize_servos()
                return True
            else:
                print("❌ Failed to get current position from DOFBOT Pro")
                return False
                
        except Exception as e:
            print(f"❌ Failed to initialize ROS: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from ROS."""
        if self.ros_initialized:
            try:
                rospy.signal_shutdown("DOFBOT Pro controller shutting down")
                self.connected = False
                print("✅ Disconnected from ROS")
            except Exception as e:
                print(f"❌ Error disconnecting from ROS: {e}")
    
    def get_current_position(self) -> Optional[Tuple[float, float, float]]:
        """Get current end effector position."""
        try:
            if not self.kinematics_service:
                print("❌ Kinematics service not available")
                return None
                
            # Create empty request to get current position
            request = dofbot_pro_kinemaricsRequest()
            response = self.kinematics_service(request)
            if response:
                return (response.x, response.y, response.z)
            return None
        except Exception as e:
            print(f"Error getting current position: {e}")
            return None
    
    def get_current_joints(self) -> Optional[List[float]]:
        """Get current joint positions."""
        try:
            if not self.kinematics_service:
                print("❌ Kinematics service not available")
                return None
                
            # Create request to get current joint positions
            request = dofbot_pro_kinemaricsRequest()
            response = self.kinematics_service(request)
            if response:
                joints = [
                    response.joint1,
                    response.joint2,
                    response.joint3,
                    response.joint4,
                    response.joint5,
                    response.joint6
                ]
                self.current_positions = joints
                return joints
            return None
        except Exception as e:
            print(f"Error getting current joints: {e}")
            return None
    
    def move_servo(self, servo_id: int, angle_degrees: float, speed: float = 1.0):
        """
        Move a specific servo to an angle.
        
        Args:
            servo_id: Servo ID (1-6)
            angle_degrees: Target angle in degrees
            speed: Movement speed (0.1-1.0)
        """
        if not self.connected:
            print("❌ Not connected to DOFBOT Pro")
            return False
            
        if servo_id < 1 or servo_id > 6:
            print("❌ Servo ID must be between 1 and 6")
            return False
        
        # Clamp angle to joint limits
        min_angle, max_angle = self.joint_limits[servo_id - 1]
        angle_degrees = max(min_angle, min(max_angle, angle_degrees))
        
        print(f"🤖 Moving servo {servo_id} to {angle_degrees:.1f}°")
        
        try:
            if not self.kinematics_service:
                print("❌ Kinematics service not available")
                return False
                
            # Get current joint positions
            current_joints = self.get_current_joints()
            if not current_joints:
                print("❌ Failed to get current joint positions")
                return False
            
            # Create kinematics request
            request = dofbot_pro_kinemaricsRequest()
            
            # Set target joint angle
            if servo_id == 1:
                request.cur_joint1 = angle_degrees
            elif servo_id == 2:
                request.cur_joint2 = angle_degrees
            elif servo_id == 3:
                request.cur_joint3 = angle_degrees
            elif servo_id == 4:
                request.cur_joint4 = angle_degrees
            elif servo_id == 5:
                request.cur_joint5 = angle_degrees
            elif servo_id == 6:
                request.cur_joint6 = angle_degrees
            
            # Set other joints to current positions
            request.cur_joint1 = current_joints[0] if servo_id != 1 else angle_degrees
            request.cur_joint2 = current_joints[1] if servo_id != 2 else angle_degrees
            request.cur_joint3 = current_joints[2] if servo_id != 3 else angle_degrees
            request.cur_joint4 = current_joints[3] if servo_id != 4 else angle_degrees
            request.cur_joint5 = current_joints[4] if servo_id != 5 else angle_degrees
            request.cur_joint6 = current_joints[5] if servo_id != 6 else angle_degrees
            
            request.kin_name = "fk"  # Forward kinematics
            
            # Send request
            response = self.kinematics_service(request)
            
            if response:
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
    
    def move_all_servos(self, angles_degrees: List[float], speed: float = 1.0):
        """
        Move all servos to specified angles.
        
        Args:
            angles_degrees: List of 6 angles in degrees
            speed: Movement speed (0.1-1.0)
        """
        if len(angles_degrees) != 6:
            print("❌ Must provide exactly 6 angles")
            return False
            
        if not self.connected:
            print("❌ Not connected to DOFBOT Pro")
            return False
        
        print(f"🤖 Moving all servos to angles: {angles_degrees}")
        
        try:
            if not self.kinematics_service:
                print("❌ Kinematics service not available")
                return False
            
            # Clamp angles to joint limits
            clamped_angles = []
            for i, angle in enumerate(angles_degrees):
                min_angle, max_angle = self.joint_limits[i]
                clamped_angles.append(max(min_angle, min(max_angle, angle)))
            
            # Create kinematics request
            request = dofbot_pro_kinemaricsRequest()
            request.cur_joint1 = clamped_angles[0]
            request.cur_joint2 = clamped_angles[1]
            request.cur_joint3 = clamped_angles[2]
            request.cur_joint4 = clamped_angles[3]
            request.cur_joint5 = clamped_angles[4]
            request.cur_joint6 = clamped_angles[5]
            request.kin_name = "fk"  # Forward kinematics
            
            # Send request
            response = self.kinematics_service(request)
            
            if response:
                # Update current positions
                self.current_positions = clamped_angles.copy()
                print("✅ All servos moved successfully")
                return True
            else:
                print("❌ Failed to move servos")
                return False
                
        except Exception as e:
            print(f"❌ Failed to move servos: {e}")
            return False
    
    def initialize_servos(self):
        """Initialize all servos to default positions."""
        if not self.connected:
            return
            
        print("🔧 Initializing servos to default positions...")
        home_angles = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]  # Home position in degrees
        self.move_all_servos(home_angles)
        time.sleep(2)
        print("✅ Servos initialized")
    
    def home_position(self):
        """Move to home position."""
        home_angles = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
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
    
    def move_to_position(self, x: float, y: float, z: float):
        """
        Move end effector to 3D position using inverse kinematics.
        This uses the DOFBOT Pro's built-in IK solver.
        
        Args:
            x: X coordinate
            y: Y coordinate  
            z: Z coordinate
        """
        if not self.connected:
            print("❌ Not connected to DOFBOT Pro")
            return False
    
        print(f"🎯 Moving to position ({x}, {y}, {z})")
        
        try:
            if not self.kinematics_service:
                print("❌ Kinematics service not available")
                return False
                
            # Create kinematics request for inverse kinematics
            request = dofbot_pro_kinemaricsRequest()
            request.tar_x = x
            request.tar_y = y
            request.tar_z = z
            request.Roll = 0.0    # Default roll
            request.Pitch = 0.0   # Default pitch
            request.Yaw = 0.0     # Default yaw
            request.kin_name = "ik"  # Inverse kinematics
            
            # Send request
            response = self.kinematics_service(request)
            
            if response:
                print("✅ Position movement completed")
                return True
            else:
                print("❌ Position movement failed")
                return False
                
        except Exception as e:
            print(f"❌ Failed to move to position: {e}")
            return False
    
    def execute_stack_sequence(self, cup_positions: List[Tuple[float, float, float]]):
        """
        Execute the cup stacking sequence.
        
        Args:
            cup_positions: List of cup positions to stack
        """
        if not self.connected:
            print("❌ Not connected to DOFBOT Pro")
            return False
            
        print(f"🎯 Executing stacking sequence for {len(cup_positions)} cups...")
        
        # Move to home position first
        self.home_position()
        time.sleep(2)
            
        # Define stack position
        stack_x, stack_y, stack_z = 0.15, 0.15, 0.05  # In meters
        
        for i, (x, y, z) in enumerate(cup_positions):
            print(f"📦 Stacking cup {i+1}/{len(cup_positions)} at position ({x}, {y}, {z})")
                
            # Approach from above
            self.move_to_position(x, y, z + 0.03)
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
            self.move_to_position(x, y, z + 0.05)
            time.sleep(1)
                
            # Move to stack position
            self.move_to_position(stack_x, stack_y, stack_z + 0.05)
            time.sleep(1)
                
            # Lower to stack
            self.move_to_position(stack_x, stack_y, stack_z)
            time.sleep(1)
            
            # Release cup
            self.open_gripper()
            time.sleep(0.5)
            
            # Move up
            self.move_to_position(stack_x, stack_y, stack_z + 0.05)
            time.sleep(1)
        
        # Return to home position
        self.home_position()
        print("✅ Stacking sequence completed!")
        
        return True
    
    def get_current_positions(self) -> List[float]:
        """Get current joint positions in degrees."""
        return self.current_positions.copy()

if __name__ == "__main__":
    print("🤖 Testing DOFBOT Pro Controller...")
    robot = DOFBOTProController()
        
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