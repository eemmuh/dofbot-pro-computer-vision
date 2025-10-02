#!/usr/bin/env python3
"""
Manual Position Adjuster for Cup Detection
Allows real-time adjustment of robot position to see cups on table
"""

import cv2
import numpy as np
import time
import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

# Fix smbus import issue
try:
    import smbus2 as smbus
    sys.modules['smbus'] = smbus
except ImportError:
    print("❌ smbus2 not available")
    sys.exit(1)

# Import robot control
try:
    from Arm_Lib import Arm_Device
except Exception as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

class ManualPositionAdjuster:
    def __init__(self):
        self.robot = None
        self.camera = None
        self.running = False
        
        # Start with a position level with cups on table
        self.current_position = [90, 15, 20, 90, 90, 30]  # Level with cups on table
        
        # Adjustment step size
        self.step_size = 5  # degrees per adjustment
        
    def initialize_systems(self):
        """Initialize robot and camera"""
        print("🔧 Initializing systems for manual position adjustment...")
        
        # Initialize robot
        try:
            self.robot = Arm_Device()
            time.sleep(0.1)
            print("✅ Robot connected")
        except Exception as e:
            print(f"❌ Robot initialization failed: {e}")
            return False
        
        # Initialize camera
        try:
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                print("❌ Could not open camera")
                return False
            
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            print("✅ Camera initialized")
        except Exception as e:
            print(f"❌ Camera initialization failed: {e}")
            return False
        
        return True
    
    def move_robot_smooth(self, angles, speed=2000):
        """Move robot with smooth motion"""
        for i, angle in enumerate(angles):
            self.robot.Arm_serial_servo_write(i+1, int(angle), speed)
            time.sleep(0.1)
        time.sleep(speed/1000 + 0.5)
    
    def adjust_position(self, direction):
        """Adjust robot position based on direction"""
        adjustments = {
            'w': [0, -self.step_size, 0, 0, 0, 0],  # Shoulder up
            's': [0, self.step_size, 0, 0, 0, 0],   # Shoulder down
            'a': [-self.step_size, 0, 0, 0, 0, 0],  # Base left
            'd': [self.step_size, 0, 0, 0, 0, 0],   # Base right
            'q': [0, 0, -self.step_size, 0, 0, 0],  # Elbow down
            'e': [0, 0, self.step_size, 0, 0, 0],   # Elbow up
            'r': [0, 0, 0, -self.step_size, 0, 0],  # Wrist rotation left
            't': [0, 0, 0, self.step_size, 0, 0],   # Wrist rotation right
            'f': [0, 0, 0, 0, -self.step_size, 0],   # Wrist tilt down
            'g': [0, 0, 0, 0, self.step_size, 0]     # Wrist tilt up
        }
        
        if direction in adjustments:
            adjustment = adjustments[direction]
            self.current_position = [max(0, min(180, a + b)) for a, b in zip(self.current_position, adjustment)]
            self.move_robot_smooth(self.current_position)
            print(f"Adjusted: {direction} -> {self.current_position}")
    
    def detect_cups_simple(self, frame):
        """Simple cup detection using computer vision"""
        # Convert to HSV for better color detection
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Define range for red cups (adjust these values for your cups)
        lower_red1 = np.array([0, 50, 50])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 50, 50])
        upper_red2 = np.array([180, 255, 255])
        
        # Create masks for red color
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask = mask1 + mask2
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        detections = []
        for contour in contours:
            # Filter by area
            area = cv2.contourArea(contour)
            if area > 1000:  # Minimum area for cup
                # Get bounding rectangle
                x, y, w, h = cv2.boundingRect(contour)
                
                # Filter by aspect ratio (cups are roughly rectangular)
                aspect_ratio = w / h if h > 0 else 0
                if 0.3 < aspect_ratio < 3.0:  # Reasonable aspect ratio
                    # Calculate confidence based on area
                    confidence = min(0.9, area / 10000)
                    detections.append((x, y, w, h, confidence))
        
        return detections
    
    def run_manual_adjustment(self):
        """Interactive manual position adjustment"""
        print("🎯 Manual Position Adjustment for Cup Detection")
        print("=" * 60)
        print("Instructions:")
        print("1. Position cups on your table")
        print("2. Use keys to adjust robot position until camera sees cups clearly")
        print("3. Press 's' to save the optimal position")
        print("4. Press 'q' to quit")
        print("")
        print("Controls:")
        print("  W/S: Shoulder up/down (most important for seeing table)")
        print("  A/D: Base left/right") 
        print("  Q/E: Elbow down/up")
        print("  R/T: Wrist rotation left/right")
        print("  F/G: Wrist tilt down/up")
        print("  S: Save position")
        print("  Q: Quit")
        print("")
        
        # Start with very low position
        print(f"Starting with very low position: {self.current_position}")
        self.move_robot_smooth(self.current_position)
        print("Adjust until you can see cups clearly in the camera view...")
        
        while True:
            # Capture and display frame
            ret, frame = self.camera.read()
            if not ret:
                continue
            
            # Detect cups
            detections = self.detect_cups_simple(frame)
            
            # Draw detections
            for detection in detections:
                x, y, w, h, confidence = detection
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, f"Cup: {confidence:.2f}", (x, y - 10), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Draw current position and instructions
            cv2.putText(frame, f"Position: {self.current_position}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f"Cups Detected: {len(detections)}", 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, "W/S:Shoulder A/D:Base Q/E:Elbow R/T:Wrist F/G:Tilt", 
                       (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            cv2.putText(frame, "S:Save Q:Quit", 
                       (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            
            cv2.imshow('Manual Position Adjustment', frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                # Save optimal position
                self.save_optimal_position()
                break
            elif key in ['w', 's', 'a', 'd', 'q', 'e', 'r', 't', 'f', 'g']:
                # Adjust position
                self.adjust_position(key)
        
        cv2.destroyAllWindows()
    
    def save_optimal_position(self):
        """Save the optimal home position"""
        print(f"💾 Saving optimal home position: {self.current_position}")
        
        # Save to file
        with open("optimal_home_position.txt", "w") as f:
            f.write(f"# Optimal Home Position for Cup Detection\n")
            f.write(f"# Found using manual_position_adjuster.py\n")
            f.write(f"# Format: [base, shoulder, elbow, wrist_rotation, wrist_tilt, gripper]\n")
            f.write(f"optimal_home_position = {self.current_position}\n")
            f.write(f"\n# Usage in your code:\n")
            f.write(f"# self.home_position = {self.current_position}\n")
        
        print("✅ Optimal position saved to optimal_home_position.txt")
        print("✅ Use this position in your cup stacking code!")
    
    def cleanup(self):
        """Cleanup resources"""
        if self.camera:
            self.camera.release()
        cv2.destroyAllWindows()

def main():
    """Main function"""
    print("🎯 Manual Position Adjustment for Cup Detection")
    print("=" * 60)
    print("✅ Adjust robot position until camera can see cups on table!")
    
    adjuster = ManualPositionAdjuster()
    
    if not adjuster.initialize_systems():
        print("❌ Failed to initialize systems")
        return
    
    try:
        # Run manual adjustment
        adjuster.run_manual_adjustment()
        
    finally:
        adjuster.cleanup()

if __name__ == "__main__":
    main()