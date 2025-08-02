#!/usr/bin/env python3
"""
Complete Cup Stacking Robot
Detects cups and performs actual picking and stacking
"""

import sys
import os
import cv2
import time
import numpy as np
import threading

# Add src directory to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

# Fix smbus import issue
try:
    import smbus2 as smbus
    sys.modules['smbus'] = smbus
    print("✅ smbus compatibility fixed")
except ImportError:
    print("❌ smbus2 not available")
    sys.exit(1)

# Import our modules
try:
    from vision.cup_detector import CupDetector
    from Arm_Lib import Arm_Device
    print("✅ All modules imported successfully")
except Exception as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

class CupStackingRobot:
    def __init__(self):
        self.robot = None
        self.detector = None
        self.camera = None
        self.camera_available = False
        
        # Robot workspace parameters (in meters)
        self.workspace_bounds = {
            'x': (-0.15, 0.15),  # Left to right
            'y': (0.20, 0.35),   # Front to back
            'z': (0.05, 0.25)    # Bottom to top
        }
        
        # Stacking position (center of workspace)
        self.stack_center = (0.0, 0.25, 0.05)
        
        # Cup parameters
        self.cup_height = 0.12  # meters
        self.cup_diameter = 0.08  # meters
        self.gripper_offset = 0.02  # meters
        
        # Movement parameters
        self.approach_height = 0.05  # meters above cup
        self.pickup_speed = 50  # servo speed
        self.placement_speed = 30  # servo speed
        
        # Stack tracking
        self.stack_height = 0.0
        self.cups_stacked = 0
        
    def initialize_components(self):
        """Initialize robot, detector, and camera"""
        print("🔧 Initializing components...")
        
        # Initialize YOLO detector
        model_path = "backup/yolo-cup-memory-optimized_final.weights"
        if os.path.exists(model_path):
            print("✅ YOLO model found")
            self.detector = CupDetector(model_path=model_path, conf_threshold=0.5)
            print("✅ YOLO detector initialized")
        else:
            print(f"❌ YOLO model not found: {model_path}")
            return False
        
        # Initialize camera
        print("📷 Initializing camera...")
        self.camera = cv2.VideoCapture(0)
        if self.camera.isOpened():
            self.camera_available = True
            print("✅ Camera initialized")
        else:
            print("⚠️ Camera not available - using simulation mode")
        
        # Initialize robot
        print("🤖 Initializing robot...")
        try:
            self.robot = Arm_Device()
            time.sleep(0.1)
            print("✅ Robot connected")
            
            # Move to home position
            print("🏠 Moving to home position...")
            self.robot.Arm_serial_servo_write6(90, 90, 90, 90, 90, 30, 3000)
            time.sleep(3)
            print("✅ Home position reached")
            
        except Exception as e:
            print(f"❌ Robot initialization failed: {e}")
            return False
        
        return True
    
    def camera_to_robot_coordinates(self, x, y, confidence):
        """Convert camera coordinates to robot coordinates"""
        # This is a simplified conversion - you'll need to calibrate this
        # Camera coordinates are typically (0,0) at top-left, (width,height) at bottom-right
        
        # Get camera frame size
        if self.camera_available:
            width = int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
        else:
            width, height = 640, 480  # Default values
        
        # Convert to normalized coordinates (-1 to 1)
        x_norm = (x - width/2) / (width/2)
        y_norm = (y - height/2) / (height/2)
        
        # Convert to robot workspace coordinates
        robot_x = x_norm * (self.workspace_bounds['x'][1] - self.workspace_bounds['x'][0]) / 2
        robot_y = self.workspace_bounds['y'][0] + (1 - y_norm) * (self.workspace_bounds['y'][1] - self.workspace_bounds['y'][0])
        robot_z = self.workspace_bounds['z'][0]  # Cups are on the table
        
        return robot_x, robot_y, robot_z
    
    def inverse_kinematics(self, x, y, z):
        """Convert 3D coordinates to servo angles (simplified)"""
        # This is a simplified IK - you'll need to calibrate for your specific robot
        
        # Base rotation (servo 1)
        base_angle = 90 + np.arctan2(x, y) * 180 / np.pi
        
        # Shoulder angle (servo 2) - simplified
        distance = np.sqrt(x**2 + y**2)
        shoulder_angle = 90 + (distance - 0.15) * 50  # Simplified calculation
        
        # Elbow angle (servo 3) - simplified
        elbow_angle = 90 - (z - 0.05) * 100  # Simplified calculation
        
        # Wrist angles (servos 4, 5) - keep neutral
        wrist_angle = 90
        wrist_rotate = 90
        
        # Gripper (servo 6) - keep closed
        gripper_angle = 30
        
        return [base_angle, shoulder_angle, elbow_angle, wrist_angle, wrist_rotate, gripper_angle]
    
    def move_to_position(self, x, y, z, speed=2000):
        """Move robot to 3D position"""
        angles = self.inverse_kinematics(x, y, z)
        print(f"🤖 Moving to ({x:.3f}, {y:.3f}, {z:.3f})")
        print(f"   Servo angles: {[f'{a:.1f}°' for a in angles]}")
        
        self.robot.Arm_serial_servo_write6(
            angles[0], angles[1], angles[2], 
            angles[3], angles[4], angles[5], 
            speed
        )
        time.sleep(speed/1000 + 0.5)  # Wait for movement to complete
    
    def pick_cup(self, x, y, z):
        """Pick up a cup at the specified position"""
        print(f"🥤 Picking cup at ({x:.3f}, {y:.3f}, {z:.3f})")
        
        # Approach position (above the cup)
        approach_x, approach_y, approach_z = x, y, z + self.approach_height
        self.move_to_position(approach_x, approach_y, approach_z, self.pickup_speed)
        
        # Open gripper
        print("🤏 Opening gripper...")
        self.robot.Arm_serial_servo_write(6, 180, 1000)
        time.sleep(1)
        
        # Move down to cup
        self.move_to_position(x, y, z, self.pickup_speed)
        
        # Close gripper
        print("🤏 Closing gripper...")
        self.robot.Arm_serial_servo_write(6, 30, 1000)
        time.sleep(1)
        
        # Lift up
        self.move_to_position(approach_x, approach_y, approach_z, self.pickup_speed)
        
        print("✅ Cup picked successfully!")
    
    def place_cup_in_stack(self, cup_number):
        """Place cup in the stacking position"""
        print(f"🏗️ Placing cup {cup_number} in stack")
        
        # Calculate stack position
        stack_x, stack_y, stack_z = self.stack_center
        stack_z += self.stack_height  # Add current stack height
        
        # Approach stack position
        approach_x, approach_y, approach_z = stack_x, stack_y, stack_z + self.approach_height
        self.move_to_position(approach_x, approach_y, approach_z, self.placement_speed)
        
        # Move to placement position
        self.move_to_position(stack_x, stack_y, stack_z, self.placement_speed)
        
        # Open gripper to release cup
        print("🤏 Releasing cup...")
        self.robot.Arm_serial_servo_write(6, 180, 1000)
        time.sleep(1)
        
        # Move up
        self.move_to_position(approach_x, approach_y, approach_z, self.placement_speed)
        
        # Update stack tracking
        self.stack_height += self.cup_height
        self.cups_stacked += 1
        
        print(f"✅ Cup {cup_number} placed in stack! (Stack height: {self.stack_height:.3f}m)")
    
    def detect_and_stack_cups(self):
        """Main cup detection and stacking loop"""
        print("🎯 Starting cup detection and stacking...")
        
        if not self.camera_available:
            print("⚠️ No camera - using simulated cup positions")
            # Simulate cup positions
            simulated_cups = [
                (0.25, 0.30, 0.05),
                (0.45, 0.30, 0.05), 
                (0.65, 0.30, 0.05)
            ]
            
            for i, (x, y, z) in enumerate(simulated_cups):
                print(f"\n🥤 Processing simulated cup {i+1}")
                self.pick_cup(x, y, z)
                self.place_cup_in_stack(i+1)
                time.sleep(1)
            
            print(f"🎉 Stacking complete! {self.cups_stacked} cups stacked")
            return
        
        # Real camera-based detection
        while True:
            ret, frame = self.camera.read()
            if not ret:
                print("❌ Could not read camera frame")
                continue
            
            # Detect cups
            detections = self.detector.detect_cups(frame)
            
            if not detections:
                print("🔍 No cups detected - waiting...")
                cv2.imshow('Cup Detection', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                continue
            
            print(f"📊 Found {len(detections)} cups")
            
            # Process each detected cup
            for i, detection in enumerate(detections):
                if i >= 5:  # Limit to 5 cups for safety
                    break
                
                # Get cup position in camera coordinates
                x_cam = detection['x']
                y_cam = detection['y']
                confidence = detection['confidence']
                
                # Convert to robot coordinates
                x_robot, y_robot, z_robot = self.camera_to_robot_coordinates(x_cam, y_cam, confidence)
                
                print(f"\n🥤 Processing cup {i+1} (confidence: {confidence:.2f})")
                print(f"   Camera: ({x_cam}, {y_cam}) -> Robot: ({x_robot:.3f}, {y_robot:.3f}, {z_robot:.3f})")
                
                # Check if position is within workspace
                if (self.workspace_bounds['x'][0] <= x_robot <= self.workspace_bounds['x'][1] and
                    self.workspace_bounds['y'][0] <= y_robot <= self.workspace_bounds['y'][1]):
                    
                    # Pick and stack the cup
                    self.pick_cup(x_robot, y_robot, z_robot)
                    self.place_cup_in_stack(i+1)
                    time.sleep(1)
                else:
                    print(f"⚠️ Cup {i+1} outside workspace bounds - skipping")
            
            # Show detection results
            result_frame = self.detector.draw_detections(frame.copy(), detections)
            cv2.imshow('Cup Detection', result_frame)
            
            # Check for quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        print(f"🎉 Stacking complete! {self.cups_stacked} cups stacked")
    
    def run_interactive_mode(self):
        """Run interactive mode with manual controls"""
        print("🎮 Interactive Mode")
        print("Controls:")
        print("- Press 'd' to detect and stack cups")
        print("- Press 'h' to home position")
        print("- Press 'o' to open gripper")
        print("- Press 'c' to close gripper")
        print("- Press 't' to test movement")
        print("- Press 'q' to quit")
        
        while True:
            if self.camera_available:
                ret, frame = self.camera.read()
                if ret:
                    cv2.imshow('Cup Stacking Robot', frame)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                break
            elif key == ord('d'):
                self.detect_and_stack_cups()
            elif key == ord('h'):
                print("🏠 Moving to home position...")
                self.robot.Arm_serial_servo_write6(90, 90, 90, 90, 90, 30, 3000)
                time.sleep(3)
            elif key == ord('o'):
                print("🤏 Opening gripper...")
                self.robot.Arm_serial_servo_write(6, 180, 1000)
            elif key == ord('c'):
                print("🤏 Closing gripper...")
                self.robot.Arm_serial_servo_write(6, 30, 1000)
            elif key == ord('t'):
                print("🧪 Testing movement...")
                self.move_to_position(0.1, 0.25, 0.1)
                time.sleep(2)
                self.move_to_position(-0.1, 0.25, 0.1)
                time.sleep(2)
                self.move_to_position(0, 0.25, 0.1)
    
    def cleanup(self):
        """Cleanup resources"""
        print("🧹 Cleaning up...")
        
        if self.camera_available:
            self.camera.release()
        
        cv2.destroyAllWindows()
        
        if self.robot:
            print("🏠 Returning to home position...")
            self.robot.Arm_serial_servo_write6(90, 90, 90, 90, 90, 30, 3000)
            time.sleep(3)
        
        print("✅ Cleanup complete!")

def main():
    """Main function"""
    print("🥤 Cup Stacking Robot")
    print("=" * 50)
    
    robot = CupStackingRobot()
    
    if not robot.initialize_components():
        print("❌ Failed to initialize components")
        return
    
    try:
        # Ask user for mode
        print("\n🎯 Choose mode:")
        print("1. Automatic stacking (detect and stack all cups)")
        print("2. Interactive mode (manual control)")
        
        choice = input("Enter choice (1 or 2): ").strip()
        
        if choice == '1':
            robot.detect_and_stack_cups()
        elif choice == '2':
            robot.run_interactive_mode()
        else:
            print("❌ Invalid choice")
    
    except KeyboardInterrupt:
        print("\n⏹️ Interrupted by user")
    
    finally:
        robot.cleanup()

if __name__ == "__main__":
    main() 