#!/usr/bin/env python3
"""
Cup Stacking Demo
Combines YOLO cup detection with DOFBOT robot control
"""

import cv2
import time
import sys
import numpy as np
sys.path.append('src')

from vision.cup_detector import CupDetector
from robot.jetson_dofbot_controller import JetsonDOFBOTController

class CupStackingDemo:
    def __init__(self):
        self.cap = None
        self.detector = None
        self.robot = None
        self.running = False
        
    def initialize_system(self):
        """Initialize camera, detector, and robot."""
        print("🚀 Initializing Cup Stacking System...")
        
        # Initialize camera
        print("📷 Initializing camera...")
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("❌ Error: Could not open camera")
            return False
        print("✅ Camera initialized")
        
        # Initialize cup detector
        print("🔍 Initializing cup detector...")
        try:
            model_path = "backup/yolo-cup_final.weights"
            self.detector = CupDetector(model_path=model_path, conf_threshold=0.5)
            print("✅ Cup detector initialized")
        except Exception as e:
            print(f"❌ Error initializing cup detector: {e}")
            print("⚠️  Make sure you have trained the YOLO model first")
            return False
        
        # Initialize robot
        print("🤖 Initializing Jetson DOFBOT controller...")
        self.robot = JetsonDOFBOTController()
        if not self.robot.connect():
            print("❌ Error: Could not connect to DOFBOT")
            print("Please run 'python3 test_dofbot_connection.py' to test connection")
            return False
        print("✅ DOFBOT connected successfully")
        
        return True
    
    def run_demo(self):
        """Run the main demo loop."""
        print("\n🎯 Cup Stacking Demo Started!")
        print("Controls:")
        print("  'q' - Quit")
        print("  's' - Start stacking sequence")
        print("  'h' - Move to home position")
        print("  'g' - Toggle gripper")
        print("  '1-6' - Move individual joints")
        
        self.running = True
        
        try:
            while self.running:
                # Capture frame
                if self.cap is None:
                    print("Error: Camera not initialized")
                    break
                    
                ret, frame = self.cap.read()
                if not ret:
                    print("Error: Could not read frame")
                    break
                
                # Detect cups
                if self.detector is None:
                    print("Error: Detector not initialized")
                    break
                    
                detections = self.detector.detect_cups(frame)
                cup_positions = self.detector.get_cup_positions(frame)
                
                # Draw detections on frame
                frame_with_detections = self.detector.draw_detections(frame.copy(), detections)
                
                # Display cup count and instructions
                cv2.putText(frame_with_detections, f"Cups detected: {len(detections)}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(frame_with_detections, "Press 's' to stack, 'q' to quit", 
                           (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # Display frame
                cv2.imshow('Cup Stacking Demo', frame_with_detections)
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                self.handle_key_press(key, cup_positions)
                
        except KeyboardInterrupt:
            print("\n⚠️  Demo interrupted by user")
        finally:
            self.cleanup()
    
    def handle_key_press(self, key, cup_positions):
        """Handle keyboard input."""
        if self.robot is None:
            print("❌ Robot not initialized")
            return
            
        if key == ord('q'):
            self.running = False
        elif key == ord('s') and len(cup_positions) > 0:
            print(f"\n🤖 Starting stacking sequence with {len(cup_positions)} cups...")
            self.execute_stack_sequence(cup_positions)
        elif key == ord('h'):
            print("\n🏠 Moving to home position...")
            self.robot.home_position()
        elif key == ord('g'):
            print("\n🤏 Toggling gripper...")
            # Simple gripper toggle (you might want to track state)
            self.robot.open_gripper()
            time.sleep(0.5)
            self.robot.close_gripper()
        elif key in [ord('1'), ord('2'), ord('3'), ord('4'), ord('5'), ord('6')]:
            servo_id = int(chr(key))
            angle = 45.0  # Default angle
            print(f"\n🔄 Moving servo {servo_id} to {angle} degrees...")
            self.robot.move_servo(servo_id, angle)
    
    def execute_stack_sequence(self, cup_positions):
        """Execute the cup stacking sequence."""
        if self.robot is None:
            print("❌ Robot not initialized")
            return
            
        if not self.robot.connected:
            print("❌ Robot not connected")
            return
        
        print("🎯 Executing stacking sequence...")
        
        # Move to home position first
        self.robot.home_position()
        time.sleep(2)
        
        # Define stack position (adjust based on your setup)
        stack_x, stack_y, stack_z = 150, 150, 50
        
        for i, (x, y, z) in enumerate(cup_positions):
            print(f"📦 Stacking cup {i+1}/{len(cup_positions)} at position ({x}, {y}, {z})")
            
            # Approach from above
            self.robot.move_to_position(x, y, z + 30)
            time.sleep(1)
            
            # Open gripper
            self.robot.open_gripper()
            time.sleep(0.5)
            
            # Move down to cup
            self.robot.move_to_position(x, y, z)
            time.sleep(1)
            
            # Close gripper to grab cup
            self.robot.close_gripper()
            time.sleep(1)
            
            # Lift cup
            self.robot.move_to_position(x, y, z + 50)
            time.sleep(1)
            
            # Move to stack position
            self.robot.move_to_position(stack_x, stack_y, stack_z + 50)
            time.sleep(1)
            
            # Lower to stack
            self.robot.move_to_position(stack_x, stack_y, stack_z)
            time.sleep(1)
            
            # Release cup
            self.robot.open_gripper()
            time.sleep(0.5)
            
            # Move up
            self.robot.move_to_position(stack_x, stack_y, stack_z + 50)
            time.sleep(1)
        
        # Return to home position
        self.robot.home_position()
        print("✅ Stacking sequence completed!")
    
    def cleanup(self):
        """Clean up resources."""
        print("\n🧹 Cleaning up...")
        
        if self.cap:
            self.cap.release()
        
        if self.robot:
            self.robot.disconnect()
        
        cv2.destroyAllWindows()
        print("✅ Cleanup complete")

def main():
    print("🤖 Cup Stacking Demo")
    print("=" * 40)
    
    demo = CupStackingDemo()
    
    if not demo.initialize_system():
        print("❌ Failed to initialize system")
        return
    
    demo.run_demo()

if __name__ == "__main__":
    main() 