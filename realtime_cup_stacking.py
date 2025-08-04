#!/usr/bin/env python3
"""
Real-time Cup Stacking Robot
Uses YOLO detection to find cups in real-time and automatically stack them
"""

import cv2
import numpy as np
import time
import sys
import os
import threading
from collections import deque

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
    from Arm_Lib import Arm_Device
    from vision.cup_detector import CupDetector
    print("✅ All modules imported successfully")
except Exception as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

class RealtimeCupStacking:
    def __init__(self):
        self.camera = None
        self.detector = None
        self.robot = None
        self.running = False
        self.detection_thread = None
        self.robot_thread = None
        
        # Detection settings
        self.confidence_threshold = 0.5
        self.min_cup_size = 50  # minimum pixel size for cup detection
        self.max_cups_to_stack = 5
        
        # Robot settings
        self.pickup_speed = 2000
        self.placement_speed = 1500
        self.approach_speed = 1000
        
        # Stacking state
        self.cups_detected = []
        self.cups_stacked = 0
        self.stack_height = 0
        self.cup_height = 0.12  # meters per cup
        self.is_stacking = False
        
        # Position tracking
        self.detection_history = deque(maxlen=10)  # Track detections over time
        self.stable_detection_threshold = 3  # Need 3 consistent detections
        
        # Calibrated positions (you can adjust these)
        self.stack_position = [90, 90, 90, 90, 90, 30]  # Center stack position
        
    def initialize_camera(self):
        """Initialize camera for real-time detection"""
        print("📷 Initializing camera...")
        self.camera = cv2.VideoCapture(0)
        if not self.camera.isOpened():
            print("❌ Could not open camera")
            return False
        
        # Set camera properties
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.camera.set(cv2.CAP_PROP_FPS, 30)
        
        print("✅ Camera initialized")
        return True
    
    def initialize_detector(self):
        """Initialize YOLO cup detector"""
        print("🔍 Initializing YOLO detector...")
        try:
            # Look for the best available model weights
            model_paths = [
                "backup/yolo-cup-memory-optimized_final.weights",
                "backup/yolo-cup_final.weights", 
                "backup/yolo-cup-tiny_final.weights"
            ]
            
            model_path = None
            for path in model_paths:
                if os.path.exists(path):
                    model_path = path
                    break
            
            if model_path is None:
                raise FileNotFoundError("No YOLO model weights found in backup/ directory")
            
            print(f"📁 Using model: {model_path}")
            self.detector = CupDetector(model_path)
            print("✅ YOLO detector initialized")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize detector: {e}")
            return False
    
    def initialize_robot(self):
        """Initialize robot arm"""
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
            return True
        except Exception as e:
            print(f"❌ Robot initialization failed: {e}")
            return False
    
    def convert_detection_to_robot_coords(self, detection, frame_width, frame_height):
        """Convert camera detection to robot coordinates"""
        x, y, w, h = detection
        
        # Convert from pixel coordinates to robot coordinates
        # This is a simplified conversion - you may need to calibrate this
        
        # Normalize coordinates (0-1)
        center_x = (x + w/2) / frame_width
        center_y = (y + h/2) / frame_height
        
        # Convert to robot servo angles (simplified)
        # Base rotation (servo 1): 0-180 degrees
        base_angle = 60 + (center_x * 60)  # 60-120 degree range
        
        # Shoulder height (servo 2): 60-120 degrees
        shoulder_angle = 120 - (center_y * 60)  # Higher Y = lower shoulder
        
        # Elbow (servo 3): 90 degrees (fixed for now)
        elbow_angle = 90
        
        # Wrist rotation (servo 4): 90 degrees (fixed)
        wrist_rotation = 90
        
        # Wrist tilt (servo 5): 90 degrees (fixed)
        wrist_tilt = 90
        
        # Gripper (servo 6): 30 degrees (closed)
        gripper_angle = 30
        
        return [base_angle, shoulder_angle, elbow_angle, wrist_rotation, wrist_tilt, gripper_angle]
    
    def is_stable_detection(self, detection):
        """Check if detection is stable over multiple frames"""
        self.detection_history.append(detection)
        
        if len(self.detection_history) < self.stable_detection_threshold:
            return False
        
        # Check if recent detections are similar
        recent_detections = list(self.detection_history)[-self.stable_detection_threshold:]
        
        # Calculate average position
        avg_x = sum(d[0] for d in recent_detections) / len(recent_detections)
        avg_y = sum(d[1] for d in recent_detections) / len(recent_detections)
        
        # Check if all detections are within threshold
        threshold = 20  # pixels
        for det in recent_detections:
            if abs(det[0] - avg_x) > threshold or abs(det[1] - avg_y) > threshold:
                return False
        
        return True
    
    def detect_cups(self, frame):
        """Detect cups in the frame"""
        try:
            detections = self.detector.detect_cups(frame)
            valid_detections = []
            
            for detection in detections:
                x, y, w, h, confidence = detection
                
                # Filter by confidence and size
                if confidence > self.confidence_threshold and w > self.min_cup_size and h > self.min_cup_size:
                    valid_detections.append((x, y, w, h))
            
            return valid_detections
        except Exception as e:
            print(f"❌ Detection error: {e}")
            return []
    
    def pickup_cup(self, cup_position):
        """Pick up a cup at the specified position"""
        print(f"🥤 Picking up cup at position: {cup_position}")
        
        try:
            # Step 1: Move to approach position (slightly higher)
            approach_position = cup_position.copy()
            approach_position[2] += 10  # Move elbow up
            self.move_robot_to_position(approach_position, self.approach_speed)
            
            # Step 2: Open gripper
            print("   🤏 Opening gripper...")
            self.robot.Arm_serial_servo_write(6, 180, 1000)
            time.sleep(1)
            
            # Step 3: Move to pickup position
            self.move_robot_to_position(cup_position, self.pickup_speed)
            
            # Step 4: Close gripper
            print("   🤏 Closing gripper...")
            self.robot.Arm_serial_servo_write(6, 30, 1000)
            time.sleep(1)
            
            # Step 5: Move back to approach position
            self.move_robot_to_position(approach_position, self.pickup_speed)
            
            print("   ✅ Cup picked successfully!")
            return True
            
        except Exception as e:
            print(f"   ❌ Pickup failed: {e}")
            return False
    
    def place_cup_in_stack(self):
        """Place cup in the stacking position"""
        print("🏗️ Placing cup in stack...")
        
        try:
            # Calculate stack position with height adjustment
            stack_angles = self.stack_position.copy()
            stack_angles[2] -= int(self.stack_height * 100)  # Adjust for stack height
            
            # Step 1: Move to approach position above stack
            approach_stack = stack_angles.copy()
            approach_stack[2] += 10
            self.move_robot_to_position(approach_stack, self.placement_speed)
            
            # Step 2: Move to stack position
            self.move_robot_to_position(stack_angles, self.placement_speed)
            
            # Step 3: Open gripper
            print("   🤏 Releasing cup...")
            self.robot.Arm_serial_servo_write(6, 180, 1000)
            time.sleep(1)
            
            # Step 4: Move back to approach position
            self.move_robot_to_position(approach_stack, self.placement_speed)
            
            # Update stack tracking
            self.stack_height += self.cup_height
            self.cups_stacked += 1
            
            print(f"   ✅ Cup placed! Stack height: {self.stack_height:.3f}m")
            return True
            
        except Exception as e:
            print(f"   ❌ Placement failed: {e}")
            return False
    
    def move_robot_to_position(self, angles, speed=2000):
        """Move robot to specified servo angles"""
        self.robot.Arm_serial_servo_write6(
            angles[0], angles[1], angles[2],
            angles[3], angles[4], angles[5],
            speed
        )
        time.sleep(speed/1000 + 0.5)
    
    def stack_detected_cup(self, cup_detection, frame_width, frame_height):
        """Stack a single detected cup"""
        if self.is_stacking:
            return False
        
        self.is_stacking = True
        
        try:
            # Convert detection to robot coordinates
            robot_position = self.convert_detection_to_robot_coords(
                cup_detection, frame_width, frame_height
            )
            
            print(f"🎯 Converting detection to robot position: {robot_position}")
            
            # Pick up the cup
            if self.pickup_cup(robot_position):
                # Place in stack
                if self.place_cup_in_stack():
                    print(f"🎉 Successfully stacked cup {self.cups_stacked}!")
                else:
                    print("❌ Failed to place cup in stack")
            else:
                print("❌ Failed to pick up cup")
                
        except Exception as e:
            print(f"❌ Stacking error: {e}")
        finally:
            self.is_stacking = False
    
    def detection_loop(self):
        """Main detection and stacking loop"""
        print("🔄 Starting real-time detection loop...")
        
        while self.running:
            try:
                # Capture frame
                ret, frame = self.camera.read()
                if not ret:
                    print("❌ Could not read frame")
                    continue
                
                # Detect cups
                detections = self.detect_cups(frame)
                
                # Process detections
                if detections and not self.is_stacking and self.cups_stacked < self.max_cups_to_stack:
                    # Get the largest detection (closest cup)
                    largest_detection = max(detections, key=lambda d: d[2] * d[3])
                    
                    # Check if detection is stable
                    if self.is_stable_detection(largest_detection):
                        # Start stacking in a separate thread
                        stacking_thread = threading.Thread(
                            target=self.stack_detected_cup,
                            args=(largest_detection, frame.shape[1], frame.shape[0])
                        )
                        stacking_thread.start()
                
                # Draw detections on frame
                for detection in detections:
                    x, y, w, h = detection
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(frame, f"Cup", (x, y - 10), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                # Draw status information
                cv2.putText(frame, f"Cups Stacked: {self.cups_stacked}/{self.max_cups_to_stack}", 
                          (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(frame, f"Stack Height: {self.stack_height:.3f}m", 
                          (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                if self.is_stacking:
                    cv2.putText(frame, "STACKING...", (10, 90), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                # Show frame
                cv2.imshow('Real-time Cup Stacking', frame)
                
                # Check for key press
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("⏹️ Quit requested")
                    break
                elif key == ord('h'):
                    print("🏠 Moving to home position...")
                    self.robot.Arm_serial_servo_write6(90, 90, 90, 90, 90, 30, 3000)
                    time.sleep(3)
                
            except Exception as e:
                print(f"❌ Detection loop error: {e}")
                continue
    
    def start(self):
        """Start the real-time cup stacking system"""
        print("🚀 Starting Real-time Cup Stacking System")
        print("=" * 50)
        
        # Initialize components
        if not self.initialize_camera():
            return False
        
        if not self.initialize_detector():
            return False
        
        if not self.initialize_robot():
            return False
        
        print("\n🎯 System ready! Controls:")
        print("- 'q': Quit")
        print("- 'h': Home position")
        print("- Place cups in camera view to start stacking")
        print("- System will automatically detect and stack cups")
        
        # Start detection loop
        self.running = True
        try:
            self.detection_loop()
        except KeyboardInterrupt:
            print("\n⏹️ Interrupted by user")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        print("🧹 Cleaning up...")
        self.running = False
        
        if self.camera:
            self.camera.release()
        
        cv2.destroyAllWindows()
        
        if self.robot:
            # Return to home position
            try:
                self.robot.Arm_serial_servo_write6(90, 90, 90, 90, 90, 30, 3000)
                time.sleep(3)
            except:
                pass
        
        print("✅ Cleanup complete")

def main():
    """Main function"""
    print("🥤 Real-time Cup Stacking Robot")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('src/vision/cup_detector.py'):
        print("❌ Please run this script from the project root directory")
        return
    
    # Create and start the system
    system = RealtimeCupStacking()
    system.start()

if __name__ == "__main__":
    main() 