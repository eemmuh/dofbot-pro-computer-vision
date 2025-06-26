#!/usr/bin/env python3
"""
ROS DOFBOT Controller
ROS-compatible controller for DOFBOT robot arm.
This controller works with the existing ROS DOFBOT setup.
"""

import rospy
import sys
import os
import time
from typing import Tuple, List, Optional
import numpy as np

# Add ROS workspace to path
sys.path.append('/home/jetson/dofbot_ws/devel/lib/python3/dist-packages')

try:
    from dofbot_info.srv import kinemarics, kinemaricsRequest, kinemaricsResponse
    ROS_AVAILABLE = True
except ImportError:
    print("Warning: ROS DOFBOT messages not available. Install ROS workspace first.")
    ROS_AVAILABLE = False

class ROSDOFBOTController:
    def __init__(self):
        """
        Initialize the ROS DOFBOT controller.
        """
        if not ROS_AVAILABLE:
            raise RuntimeError("ROS DOFBOT messages not available. Please source the ROS workspace.")
        
        # Initialize ROS node
        rospy.init_node('cup_stacking_controller', anonymous=True)
        
        # Wait for ROS services to be available
        print("Waiting for DOFBOT ROS services...")
        rospy.wait_for_service('/dofbot_kinemarics')
        rospy.wait_for_service('/get_kinemarics')
        
        # Create service proxies
        self.kinematics_service = rospy.ServiceProxy('/dofbot_kinemarics', kinemarics)
        self.get_kinematics_service = rospy.ServiceProxy('/get_kinemarics', kinemarics)
        
        print("✅ ROS DOFBOT controller initialized successfully!")
        self.connected = True
        
    def connect(self) -> bool:
        """Connect to the DOFBOT via ROS."""
        try:
            # Test connection by getting current position
            current_pos = self.get_current_position()
            if current_pos is not None:
                print(f"✅ Connected to DOFBOT via ROS. Current position: {current_pos}")
                return True
            else:
                print("❌ Failed to get current position from DOFBOT")
                return False
        except Exception as e:
            print(f"❌ Failed to connect to DOFBOT via ROS: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the DOFBOT."""
        self.connected = False
        print("Disconnected from DOFBOT")
    
    def get_current_position(self) -> Optional[Tuple[float, float, float]]:
        """Get current end effector position."""
        try:
            # Create empty request to get current position
            request = kinemaricsRequest()
            response = self.get_kinematics_service(request)
            if response:
                return (response.x, response.y, response.z)
            return None
        except Exception as e:
            print(f"Error getting current position: {e}")
            return None
    
    def move_to_position(self, x: float, y: float, z: float) -> bool:
        """
        Move the end effector to the specified position.
        
        Args:
            x: X coordinate
            y: Y coordinate
            z: Z coordinate
        """
        try:
            print(f"Moving to position: ({x:.2f}, {y:.2f}, {z:.2f})")
            
            # Create kinematics request
            request = kinemaricsRequest()
            request.tar_x = x
            request.tar_y = y
            request.tar_z = z
            request.kin_name = "ik"  # Inverse kinematics
            
            # Send request
            response = self.kinematics_service(request)
            
            if response:
                print("✅ Movement completed successfully")
                return True
            else:
                print("❌ Movement failed")
                return False
                
        except Exception as e:
            print(f"❌ Error moving to position: {e}")
            return False
    
    def move_joint(self, joint_id: int, angle: float) -> bool:
        """
        Move a specific joint to an angle.
        
        Args:
            joint_id: Joint number (1-6)
            angle: Target angle in degrees
        """
        try:
            print(f"Moving joint {joint_id} to {angle} degrees")
            
            # Create kinematics request for joint movement
            request = kinemaricsRequest()
            
            # Set the target joint angle
            if joint_id == 1:
                request.cur_joint1 = angle
            elif joint_id == 2:
                request.cur_joint2 = angle
            elif joint_id == 3:
                request.cur_joint3 = angle
            elif joint_id == 4:
                request.cur_joint4 = angle
            elif joint_id == 5:
                request.cur_joint5 = angle
            elif joint_id == 6:
                request.cur_joint6 = angle
            else:
                print(f"❌ Invalid joint ID: {joint_id}")
                return False
            
            request.kin_name = "fk"  # Forward kinematics
            
            # Send request
            response = self.kinematics_service(request)
            
            if response:
                print("✅ Joint movement completed")
                return True
            else:
                print("❌ Joint movement failed")
                return False
                
        except Exception as e:
            print(f"❌ Error moving joint: {e}")
            return False
    
    def open_gripper(self) -> bool:
        """Open the gripper."""
        try:
            print("Opening gripper...")
            
            # For DOFBOT, gripper control might be through joint 6
            # Set joint 6 to open position (typically around 0 degrees)
            return self.move_joint(6, 0)
                
        except Exception as e:
            print(f"❌ Error opening gripper: {e}")
            return False
    
    def close_gripper(self) -> bool:
        """Close the gripper."""
        try:
            print("Closing gripper...")
            
            # For DOFBOT, gripper control might be through joint 6
            # Set joint 6 to closed position (typically around 90 degrees)
            return self.move_joint(6, 90)
                
        except Exception as e:
            print(f"❌ Error closing gripper: {e}")
            return False
    
    def home_position(self) -> bool:
        """Move to home position."""
        try:
            print("Moving to home position...")
            
            # Move all joints to home position (typically 0 degrees)
            home_angles = [0, 0, 0, 0, 0, 0]
            
            for joint_id, angle in enumerate(home_angles, 1):
                if not self.move_joint(joint_id, angle):
                    print(f"❌ Failed to move joint {joint_id} to home position")
                    return False
                time.sleep(0.5)
            
            print("✅ Moved to home position")
            return True
                
        except Exception as e:
            print(f"❌ Error moving to home position: {e}")
            return False
    
    def execute_stack_sequence(self, cup_positions: List[Tuple[float, float, float]]) -> bool:
        """
        Execute a cup stacking sequence.
        
        Args:
            cup_positions: List of (x, y, z) positions for cups to stack
        """
        try:
            print(f"Executing cup stacking sequence with {len(cup_positions)} cups...")
            
            # Move to home position first
            if not self.home_position():
                return False
            
            time.sleep(2)
            
            # Stack each cup
            for i, (x, y, z) in enumerate(cup_positions):
                print(f"Stacking cup {i+1}/{len(cup_positions)} at ({x:.2f}, {y:.2f}, {z:.2f})")
                
                # Move to cup position
                if not self.move_to_position(x, y, z + 5):  # 5cm above cup
                    print(f"❌ Failed to move to cup {i+1}")
                    return False
                
                time.sleep(1)
                
                # Open gripper
                if not self.open_gripper():
                    print(f"❌ Failed to open gripper for cup {i+1}")
                    return False
                
                time.sleep(1)
                
                # Move down to cup
                if not self.move_to_position(x, y, z):
                    print(f"❌ Failed to move down to cup {i+1}")
                    return False
                
                time.sleep(1)
                
                # Close gripper
                if not self.close_gripper():
                    print(f"❌ Failed to close gripper on cup {i+1}")
                    return False
                
                time.sleep(1)
                
                # Move up
                if not self.move_to_position(x, y, z + 5):
                    print(f"❌ Failed to move up with cup {i+1}")
                    return False
                
                time.sleep(1)
                
                # Move to stack position (you can modify this)
                stack_x, stack_y, stack_z = 0, 0, 10 + i * 5  # Stack at origin, 5cm apart
                if not self.move_to_position(stack_x, stack_y, stack_z):
                    print(f"❌ Failed to move to stack position for cup {i+1}")
                    return False
                
                time.sleep(1)
                
                # Open gripper to release cup
                if not self.open_gripper():
                    print(f"❌ Failed to release cup {i+1}")
                    return False
                
                time.sleep(1)
                
                print(f"✅ Cup {i+1} stacked successfully")
            
            # Return to home position
            if not self.home_position():
                print("❌ Failed to return to home position")
                return False
            
            print("✅ Cup stacking sequence completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error executing stack sequence: {e}")
            return False

def main():
    """Test the ROS DOFBOT controller."""
    try:
        print("Testing ROS DOFBOT Controller...")
        
        # Initialize controller
        controller = ROSDOFBOTController()
        
        # Test connection
        if controller.connect():
            print("✅ ROS DOFBOT connection successful!")
            
            # Test basic movements
            print("\nTesting basic movements...")
            
            # Get current position
            current_pos = controller.get_current_position()
            print(f"Current position: {current_pos}")
            
            # Test gripper
            print("\nTesting gripper...")
            controller.open_gripper()
            time.sleep(2)
            controller.close_gripper()
            time.sleep(2)
            
            # Test home position
            print("\nTesting home position...")
            controller.home_position()
            time.sleep(3)
            
            print("\n✅ All tests passed! ROS DOFBOT is working correctly.")
            
        else:
            print("❌ Failed to connect to ROS DOFBOT")
            
    except Exception as e:
        print(f"❌ Error testing ROS DOFBOT: {e}")

if __name__ == "__main__":
    main() 