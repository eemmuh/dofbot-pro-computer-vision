#!/usr/bin/env python3
"""
Real-time Cup Sorting Robot
Uses YOLO detection to find cups in real-time and automatically sort them into different zones
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

class RealtimeCupSorting:
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
        self.max_cups_to_sort = 10
        
        # Robot settings
        self.pickup_speed = 2000
        self.placement_speed = 1500
        self.approach_speed = 1000
        
        # Sorting state
        self.cups_detected = []
        self.cups_sorted = 0
        self.is_sorting = False
        
        # Position tracking
        self.detection_history = deque(maxlen=10)  # Track detections over time
        self.stable_detection_threshold = 3  # Need 3 consistent detections
        
        # Sorting zones - define 3 zones (left, center, right)
        self.sorting_zones = {
            'left': {
                'name': 'Left Zone',
                'position': [60, 90, 90, 90, 90, 30],  # Left side
                'color': (0, 255, 0),  # Green
                'count': 0
            },
            'center': {
                'name': 'Center Zone', 
                'position': [90, 90, 90, 90, 90, 30],  # Center
                'color': (255, 0, 0),  # Blue
                'count': 0
            },
            'right': {
                'name': 'Right Zone',
                'position': [120, 90, 90, 90, 90, 30],  # Right side
                'color': (0, 0, 255),  # Red
                'count': 0
            }
        }
        
        # Sorting criteria
        self.sorting_mode = 'position'  # 'position', 'size', 'color'
        
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
            
            # Look for config files
            config_paths = [
                "cfg/yolo-cup-memory-optimized.cfg",
                "cfg/yolo-cup.cfg",
                "cfg/yolo-cup-tiny.cfg"
            ]
            
            model_path = None
            for path in model_paths:
                if os.path.exists(path):
                    model_path = path
                    break
            
            config_path = None
            for path in config_paths:
                if os.path.exists(path):
                    config_path = path
                    break
            
            if model_path is None:
                print("❌ No YOLO model weights found")
                return False
            
            if config_path is None:
                print("❌ No YOLO config file found")
                return False
            
            self.detector = CupDetector(model_path, config_path)
            print(f"✅ YOLO detector initialized with {model_path}")
            print(f"   Config: {config_path}")
            return True
            
        except Exception as e:
            print(f"❌ Detector initialization failed: {e}")
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
    
    def determine_sorting_zone(self, detection, frame_width, frame_height):
        """Determine which zone to sort a cup into based on sorting criteria"""
        x, y, w, h = detection
        center_x = (x + w/2) / frame_width  # Normalized 0-1
        
        if self.sorting_mode == 'position':
            # Sort by horizontal position
            if center_x < 0.33:
                return 'left'
            elif center_x < 0.66:
                return 'center'
            else:
                return 'right'
        
        elif self.sorting_mode == 'size':
            # Sort by cup size (area)
            area = w * h
            if area < 5000:  # Small cups
                return 'left'
            elif area < 15000:  # Medium cups
                return 'center'
            else:  # Large cups
                return 'right'
        
        elif self.sorting_mode == 'color':
            # Sort by color (if cups are different colors)
            # This would require additional color detection logic
            return 'center'  # Default for now
        
        else:
            return 'center'  # Default fallback
    
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
    
    def place_cup_in_zone(self, zone_name):
        """Place cup in the specified sorting zone"""
        if zone_name not in self.sorting_zones:
            print(f"❌ Invalid zone: {zone_name}")
            return False
        
        zone = self.sorting_zones[zone_name]
        print(f"📦 Placing cup in {zone['name']}...")
        
        try:
            # Step 1: Move to approach position above zone
            approach_position = zone['position'].copy()
            approach_position[2] += 10  # Move elbow up
            self.move_robot_to_position(approach_position, self.approach_speed)
            
            # Step 2: Move to placement position
            self.move_robot_to_position(zone['position'], self.placement_speed)
            
            # Step 3: Open gripper
            print("   🤏 Releasing cup...")
            self.robot.Arm_serial_servo_write(6, 180, 1000)
            time.sleep(1)
            
            # Step 4: Move back to approach position
            self.move_robot_to_position(approach_position, self.placement_speed)
            
            # Update zone count
            zone['count'] += 1
            self.cups_sorted += 1
            
            print(f"   ✅ Cup placed in {zone['name']}!")
            print(f"   📊 Zone count: {zone['count']} cups")
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
    
    def sort_detected_cup(self, cup_detection, frame_width, frame_height):
        """Sort a detected cup into appropriate zone"""
        if self.is_sorting:
            return
        
        self.is_sorting = True
        
        try:
            # Determine which zone to sort into
            zone_name = self.determine_sorting_zone(cup_detection, frame_width, frame_height)
            zone = self.sorting_zones[zone_name]
            
            print(f"🎯 Sorting cup into {zone['name']}...")
            
            # Convert detection to robot coordinates
            cup_position = self.convert_detection_to_robot_coords(cup_detection, frame_width, frame_height)
            
            # Pick up the cup
            if self.pickup_cup(cup_position):
                # Place in sorting zone
                if self.place_cup_in_zone(zone_name):
                    print(f"🎉 Successfully sorted cup into {zone['name']}!")
                else:
                    print("❌ Failed to place cup in zone")
            else:
                print("❌ Failed to pick up cup")
                
        except Exception as e:
            print(f"❌ Sorting error: {e}")
        finally:
            self.is_sorting = False
    
    def detection_loop(self):
        """Main detection and sorting loop"""
        print("🔍 Starting detection loop...")
        
        while self.running:
            try:
                ret, frame = self.camera.read()
                if not ret:
                    print("❌ Failed to read camera frame")
                    continue
                
                # Detect cups
                detections = self.detect_cups(frame)
                
                # Draw detection zones on frame
                frame_height, frame_width = frame.shape[:2]
                
                # Draw sorting zones
                for zone_name, zone in self.sorting_zones.items():
                    # Calculate zone boundaries on frame
                    if zone_name == 'left':
                        x1, x2 = 0, frame_width // 3
                    elif zone_name == 'center':
                        x1, x2 = frame_width // 3, 2 * frame_width // 3
                    else:  # right
                        x1, x2 = 2 * frame_width // 3, frame_width
                    
                    # Draw zone rectangle
                    cv2.rectangle(frame, (x1, 0), (x2, frame_height), zone['color'], 2)
                    
                    # Draw zone label
                    label = f"{zone['name']}: {zone['count']}"
                    cv2.putText(frame, label, (x1 + 10, 30), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, zone['color'], 2)
                
                # Process detections
                for detection in detections:
                    x, y, w, h = detection
                    
                    # Draw detection box
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 0), 2)
                    
                    # Determine zone for this detection
                    zone_name = self.determine_sorting_zone(detection, frame_width, frame_height)
                    zone = self.sorting_zones[zone_name]
                    
                    # Draw zone indicator
                    cv2.putText(frame, zone_name.upper(), (x, y - 10), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.6, zone['color'], 2)
                    
                    # Check if detection is stable and ready for sorting
                    if self.is_stable_detection(detection) and not self.is_sorting:
                        # Start sorting in a separate thread
                        sorting_thread = threading.Thread(
                            target=self.sort_detected_cup,
                            args=(detection, frame_width, frame_height)
                        )
                        sorting_thread.daemon = True
                        sorting_thread.start()
                
                # Draw sorting mode and statistics
                cv2.putText(frame, f"Mode: {self.sorting_mode.upper()}", (10, frame_height - 60), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                cv2.putText(frame, f"Sorted: {self.cups_sorted}", (10, frame_height - 40), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                cv2.putText(frame, f"Detected: {len(detections)}", (10, frame_height - 20), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                # Display frame
                cv2.imshow('Cup Sorting System', frame)
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('1'):
                    self.sorting_mode = 'position'
                    print("🎯 Sorting mode: Position")
                elif key == ord('2'):
                    self.sorting_mode = 'size'
                    print("🎯 Sorting mode: Size")
                elif key == ord('3'):
                    self.sorting_mode = 'color'
                    print("🎯 Sorting mode: Color")
                elif key == ord('r'):
                    # Reset counts
                    for zone in self.sorting_zones.values():
                        zone['count'] = 0
                    self.cups_sorted = 0
                    print("🔄 Reset sorting counts")
                
            except Exception as e:
                print(f"❌ Detection loop error: {e}")
                continue
    
    def start(self):
        """Start the cup sorting system"""
        print("🚀 Starting Cup Sorting System")
        print("=" * 50)
        print("Controls:")
        print("- '1': Sort by position (left/center/right)")
        print("- '2': Sort by size (small/medium/large)")
        print("- '3': Sort by color (if implemented)")
        print("- 'r': Reset counts")
        print("- 'q': Quit")
        print("=" * 50)
        
        if not self.initialize_camera():
            return
        
        if not self.initialize_detector():
            return
        
        if not self.initialize_robot():
            return
        
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
            self.robot.Arm_serial_servo_write6(90, 90, 90, 90, 90, 30, 3000)
            time.sleep(3)
        
        print("✅ Cleanup complete")

def main():
    """Main function"""
    print("🥤 Real-time Cup Sorting Robot")
    print("=" * 50)
    
    sorter = RealtimeCupSorting()
    sorter.start()

if __name__ == "__main__":
    main() 