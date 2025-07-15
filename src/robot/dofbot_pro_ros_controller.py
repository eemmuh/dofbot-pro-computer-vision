#!/usr/bin/env python3
"""
DOFBOT Pro ROS Controller
Uses ROS topics and services to control DOFBOT Pro hardware
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

    from dofbot_pro_info.msg import ArmJoint
    from dofbot_pro_info.srv import dofbot_pro_kinemarics, dofbot_pro_kinemaricsRequest, dofbot_pro_kinemaricsResponse
    from std_msgs.msg import Bool
    ROS_AVAILABLE = True
except ImportError:
    ROS_AVAILABLE = False
    print("⚠️  ROS not available - using simulation mode")

class DOFBOTProROSController:
    def __init__(self):
        """
        Initialize the DOFBOT Pro ROS controller.
        Uses ROS topics and services to control the hardware.
        """
        self.connected = False
        self.ros_initialized = False
        
        # ROS publishers and subscribers
        self.target_angle_pub = None
        self.buzzer_pub = None
        self.kinematics_service = None
        
        # Current joint positions (in degrees)
        self.current_positions = [90.0, 90.0, 90.0, 90.0, 90.0, 30.0]  # DOFBOT Pro default
        
        # Joint limits (in degrees) - DOFBOT Pro specific
        self.joint_limits = [
            (0, 180),    # Base rotation
            (0, 180),    # Shoulder
            (0, 180),    # Elbow
            (0, 180),    # Wrist rotation
            (0, 180),    # Wrist pitch
            (30, 180),   # Gripper (30-180 for DOFBOT Pro)
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
            
            # Wait for ROS services to be available
            print("⏳ Waiting for DOFBOT Pro ROS services...")
            rospy.wait_for_service('/get_kinemarics')
            
            # Create service proxy
            self.kinematics_service = rospy.ServiceProxy('/get_kinemarics', dofbot_pro_kinemarics)
            
            # Create publishers
            self.target_angle_pub = rospy.Publisher('TargetAngle', ArmJoint, queue_size=10)
            self.buzzer_pub = rospy.Publisher('Buzzer', Bool, queue_size=10)
            
            # Wait for publishers to be ready
            time.sleep(1)
            
            # Test connection by moving to home position
            if self.home_position():
                self.connected = True
                print("✅ Connected to DOFBOT Pro via ROS")
                return True
            else:
                print("❌ Failed to move to home position")
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
    
    def send_joint_command(self, joints: List[float], run_time: int = 2000) -> bool:
        """
        Send joint command to DOFBOT Pro.
        
        Args:
            joints: List of 6 joint angles in degrees
            run_time: Movement time in milliseconds
        """
        if not self.connected or not self.target_angle_pub:
            print("❌ Not connected to DOFBOT Pro")
            return False
            
        if len(joints) != 6:
            print("❌ Must provide exactly 6 joint angles")
            return False
        
        try:
            # Create ArmJoint message
            msg = ArmJoint()
            msg.joints = joints
            msg.run_time = run_time
            
            # Publish command
            self.target_angle_pub.publish(msg)
            
            # Update current positions
            self.current_positions = joints.copy()
            
            print(f"✅ Joint command sent: {joints}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send joint command: {e}")
            return False
    
    def send_single_joint_command(self, joint_id: int, angle: float, run_time: int = 2000) -> bool:
        """
        Send single joint command to DOFBOT Pro.
        
        Args:
            joint_id: Joint ID (1-6)
            angle: Target angle in degrees
            run_time: Movement time in milliseconds
        """
        if not self.connected or not self.target_angle_pub:
            print("❌ Not connected to DOFBOT Pro")
            return False
            
        if joint_id < 1 or joint_id > 6:
            print("❌ Joint ID must be between 1 and 6")
            return False
        
        # Clamp angle to joint limits
        min_angle, max_angle = self.joint_limits[joint_id - 1]
        angle = max(min_angle, min(max_angle, angle))
        
        try:
            # Create ArmJoint message for single joint
            msg = ArmJoint()
            msg.id = joint_id
            msg.angle = angle
            msg.run_time = run_time
            
            # Publish command
            self.target_angle_pub.publish(msg)
            
            # Update current position
            self.current_positions[joint_id - 1] = angle
            
            print(f"✅ Joint {joint_id} command sent: {angle}°")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send joint command: {e}")
            return False
    
    def move_servo(self, servo_id: int, angle_degrees: float, time_ms: int = 2000) -> bool:
        """
        Move a specific servo to an angle.
        
        Args:
            servo_id: Servo ID (1-6)
            angle_degrees: Target angle in degrees
            time_ms: Movement time in milliseconds
        """
        print(f"🤖 Moving servo {servo_id} to {angle_degrees:.1f}°")
        return self.send_single_joint_command(servo_id, angle_degrees, time_ms)
    
    def move_all_servos(self, angles_degrees: List[float], time_ms: int = 2000) -> bool:
        """
        Move all servos to specified angles.
        
        Args:
            angles_degrees: List of 6 angles in degrees
            time_ms: Movement time in milliseconds
        """
        print(f"🤖 Moving all servos to angles: {angles_degrees}")
        return self.send_joint_command(angles_degrees, time_ms)
    
    def home_position(self) -> bool:
        """Move to home position."""
        print("🏠 Moving to home position...")
        home_angles = [90.0, 90.0, 90.0, 90.0, 90.0, 30.0]  # DOFBOT Pro home
        return self.move_all_servos(home_angles, 3000)
    
    def open_gripper(self) -> bool:
        """Open the gripper (servo 6)."""
        print("🤏 Opening gripper...")
        return self.move_servo(6, 180.0, 1000)  # Open position
    
    def close_gripper(self) -> bool:
        """Close the gripper (servo 6)."""
        print("🤏 Closing gripper...")
        return self.move_servo(6, 30.0, 1000)  # Closed position
    
    def move_to_position(self, x: float, y: float, z: float) -> bool:
        """
        Move end effector to 3D position using inverse kinematics.
        
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
                # Extract joint angles from response
                joints = [
                    response.joint1,
                    response.joint2,
                    response.joint3,
                    response.joint4,
                    response.joint5,
                    response.joint6
                ]
                
                # Send joint command
                return self.send_joint_command(joints, 2000)
            else:
                print("❌ Position movement failed")
                return False
                
        except Exception as e:
            print(f"❌ Failed to move to position: {e}")
            return False
    
    def get_current_position(self) -> Optional[Tuple[float, float, float]]:
        """Get current end effector position."""
        try:
            if not self.kinematics_service:
                print("❌ Kinematics service not available")
                return None
                
            # Create request with current joint positions
            request = dofbot_pro_kinemaricsRequest()
            request.cur_joint1 = self.current_positions[0]
            request.cur_joint2 = self.current_positions[1]
            request.cur_joint3 = self.current_positions[2]
            request.cur_joint4 = self.current_positions[3]
            request.cur_joint5 = self.current_positions[4]
            request.cur_joint6 = self.current_positions[5]
            request.kin_name = "fk"  # Forward kinematics
            
            # Send request
            response = self.kinematics_service(request)
            
            if response:
                return (response.x, response.y, response.z)
            return None
            
        except Exception as e:
            print(f"Error getting current position: {e}")
            return None
    
    def get_current_joints(self) -> List[float]:
        """Get current joint positions."""
        return self.current_positions.copy()
    
    def execute_stack_sequence(self, cup_positions: List[Tuple[float, float, float]]) -> bool:
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
        time.sleep(3)
            
        # Define stack position
        stack_x, stack_y, stack_z = 0.15, 0.15, 0.05  # In meters
        
        for i, (x, y, z) in enumerate(cup_positions):
            print(f"📦 Stacking cup {i+1}/{len(cup_positions)} at position ({x}, {y}, {z})")
                
            # Approach from above
            self.move_to_position(x, y, z + 0.03)
            time.sleep(2)
                
            # Open gripper
            self.open_gripper()
            time.sleep(1)
                
            # Move down to cup
            self.move_to_position(x, y, z)
            time.sleep(2)
                
            # Close gripper to grab cup
            self.close_gripper()
            time.sleep(2)
                
            # Lift cup
            self.move_to_position(x, y, z + 0.05)
            time.sleep(2)
                
            # Move to stack position
            self.move_to_position(stack_x, stack_y, stack_z + 0.05)
            time.sleep(2)
                
            # Lower to stack
            self.move_to_position(stack_x, stack_y, stack_z)
            time.sleep(2)
            
            # Release cup
            self.open_gripper()
            time.sleep(1)
            
            # Move up
            self.move_to_position(stack_x, stack_y, stack_z + 0.05)
            time.sleep(2)
        
        # Return to home position
        self.home_position()
        print("✅ Stacking sequence completed!")
        
        return True
    
    def test_connection(self) -> bool:
        """Test the connection by moving to home position."""
        if not self.connected:
            return False
            
        print("🧪 Testing connection...")
        return self.home_position()

if __name__ == "__main__":
    print("🤖 Testing DOFBOT Pro ROS Controller...")
    robot = DOFBOTProROSController()
        
    if robot.connect():
        print("✅ Connection test successful!")
        
        # Test basic movements
        print("\n🧪 Testing basic movements...")
        robot.home_position()
        time.sleep(3)
            
        robot.open_gripper()
        time.sleep(2)
        
        robot.close_gripper()
        time.sleep(2)
        
        # Test individual servo
        robot.move_servo(1, 120.0)  # Move base
        time.sleep(2)
        robot.move_servo(1, 90.0)   # Return to center
        time.sleep(2)
        
        robot.disconnect()
    else:
        print("❌ Connection test failed.") 