#!/usr/bin/env python3
"""
Improved Real-time Cup Sorting Robot
Optimized for uniform cups (same size and color)
Uses practical sorting criteria that work well with identical cups
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

class ImprovedCupSorting:
    def __init__(self):
        self.camera = None
        self.detector = None
        self.robot = None
        self.running = False
        self.detection_thread = None
        self.robot_thread = None
        
        # Detection settings
        self.confidence_threshold = 0.5
        self.min_cup_size = 50
        self.max_cups_to_sort = 15
        
        # Robot settings
        self.pickup_speed = 2000
        self.placement_speed = 1500
        self.approach_speed = 1000
        
        # Sorting state
        self.cups_detected = []
        self.cups_sorted = 0
        self.is_sorting = False
        
        # Position tracking
        self.detection_history = deque(maxlen=10)
        self.stable_detection_threshold = 3
        
        # Improved sorting zones for uniform cups
        self.sorting_zones = {
            'left': {
                'name': 'Left Zone',
                'position': [60, 90, 90, 90, 90, 30],
                'color': (0, 255, 0),  # Green
                'count': 0,
                'max_capacity': 5
            },
            'center': {
                'name': 'Center Zone', 
                'position': [90, 90, 90, 90, 90, 30],
                'color': (255, 0, 0),  # Blue
                'count': 0,
                'max_capacity': 5
            },
            'right': {
                'name': 'Right Zone',
                'position': [120, 90, 90, 90, 90, 30],
                'color': (0, 0, 255),  # Red
                'count': 0,
                'max_capacity': 5
            }
        }
        
        # Sorting criteria optimized for uniform cups
        self.sorting_mode = 'position'  # 'position', 'distance', 'pattern', 'random'
        
        # Pattern tracking for arrangement-based sorting
        self.pattern_history = deque(maxlen=20)
        
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
        center_x = (x + w/2) / frame_width
        center_y = (y + h/2) / frame_height
        
        # Convert to robot servo angles
        base_angle = 60 + (center_x * 60)  # 60-120 degree range
        shoulder_angle = 120 - (center_y * 60)  # Higher Y = lower shoulder
        elbow_angle = 90
        wrist_rotation = 90
        wrist_tilt = 90
        gripper_angle = 30
        
        return [base_angle, shoulder_angle, elbow_angle, wrist_rotation, wrist_tilt, gripper_angle]
    
    def determine_sorting_zone_improved(self, detection, frame_width, frame_height):
        """Determine sorting zone using improved criteria for uniform cups"""
        x, y, w, h = detection
        center_x = (x + w/2) / frame_width
        center_y = (y + h/2) / frame_height
        
        if self.sorting_mode == 'position':
            # Sort by horizontal position (most reliable for uniform cups)
            if center_x < 0.33:
                return 'left'
            elif center_x < 0.66:
                return 'center'
            else:
                return 'right'
        
        elif self.sorting_mode == 'distance':
            # Sort by distance from camera center (closest first)
            distance_from_center = abs(center_x - 0.5)
            if distance_from_center < 0.15:  # Close to center
                return 'center'
            elif center_x < 0.5:  # Left side
                return 'left'
            else:  # Right side
                return 'right'
        
        elif self.sorting_mode == 'pattern':
            # Sort based on arrangement patterns
            # This creates interesting patterns like alternating zones
            total_cups_sorted = sum(zone['count'] for zone in self.sorting_zones.values())
            if total_cups_sorted % 3 == 0:
                return 'left'
            elif total_cups_sorted % 3 == 1:
                return 'center'
            else:
                return 'right'
        
        elif self.sorting_mode == 'random':
            # Random sorting for variety
            import random
            zones = list(self.sorting_zones.keys())
            return random.choice(zones)
        
        elif self.sorting_mode == 'capacity':
            # Sort to balance zone capacities
            available_zones = []
            for zone_name, zone in self.sorting_zones.items():
                if zone['count'] < zone['max_capacity']:
                    available_zones.append(zone_name)
            
            if available_zones:
                # Choose zone with most available space
                return min(available_zones, key=lambda z: self.sorting_zones[z]['count'])
            else:
                return 'center'  # Default if all zones are full
        
        else:
            return 'center'  # Default fallback
    
    def is_stable_detection(self, detection):
        """Check if detection is stable over multiple frames"""
        self.detection_history.append(detection)
        
        if len(self.detection_history) < self.stable_detection_threshold:
            return False
        
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
        
        # Check if zone is at capacity
        if zone['count'] >= zone['max_capacity']:
            print(f"⚠️ {zone['name']} is at capacity ({zone['count']}/{zone['max_capacity']})")
            return False
        
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
            print(f"   📊 Zone count: {zone['count']}/{zone['max_capacity']}")
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
            zone_name = self.determine_sorting_zone_improved(cup_detection, frame_width, frame_height)
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
                
                # Draw sorting zones with capacity indicators
                for zone_name, zone in self.sorting_zones.items():
                    # Calculate zone boundaries on frame
                    if zone_name == 'left':
                        x1, x2 = 0, frame_width // 3
                    elif zone_name == 'center':
                        x1, x2 = frame_width // 3, 2 * frame_width // 3
                    else:  # right
                        x1, x2 = 2 * frame_width // 3, frame_width
                    
                    # Draw zone rectangle
                    color = zone['color']
                    if zone['count'] >= zone['max_capacity']:
                        color = (128, 128, 128)  # Gray when full
                    
                    cv2.rectangle(frame, (x1, 0), (x2, frame_height), color, 2)
                    
                    # Draw zone label with capacity
                    label = f"{zone['name']}: {zone['count']}/{zone['max_capacity']}"
                    cv2.putText(frame, label, (x1 + 10, 30), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                
                # Process detections
                for detection in detections:
                    x, y, w, h = detection
                    
                    # Draw detection box
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 0), 2)
                    
                    # Determine zone for this detection
                    zone_name = self.determine_sorting_zone_improved(detection, frame_width, frame_height)
                    zone = self.sorting_zones[zone_name]
                    
                    # Draw zone indicator
                    color = zone['color']
                    if zone['count'] >= zone['max_capacity']:
                        color = (128, 128, 128)  # Gray when full
                    
                    cv2.putText(frame, zone_name.upper(), (x, y - 10), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                    
                    # Check if detection is stable and ready for sorting
                    if self.is_stable_detection(detection) and not self.is_sorting:
                        # Only sort if target zone has capacity
                        if zone['count'] < zone['max_capacity']:
                            # Start sorting in a separate thread
                            sorting_thread = threading.Thread(
                                target=self.sort_detected_cup,
                                args=(detection, frame_width, frame_height)
                            )
                            sorting_thread.daemon = True
                            sorting_thread.start()
                
                # Draw sorting mode and statistics
                cv2.putText(frame, f"Mode: {self.sorting_mode.upper()}", (10, frame_height - 80), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                cv2.putText(frame, f"Sorted: {self.cups_sorted}", (10, frame_height - 60), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                cv2.putText(frame, f"Detected: {len(detections)}", (10, frame_height - 40), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                # Show total capacity
                total_capacity = sum(zone['max_capacity'] for zone in self.sorting_zones.values())
                cv2.putText(frame, f"Capacity: {self.cups_sorted}/{total_capacity}", (10, frame_height - 20), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                # Display frame
                cv2.imshow('Improved Cup Sorting System', frame)
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('1'):
                    self.sorting_mode = 'position'
                    print("🎯 Sorting mode: Position")
                elif key == ord('2'):
                    self.sorting_mode = 'distance'
                    print("🎯 Sorting mode: Distance")
                elif key == ord('3'):
                    self.sorting_mode = 'pattern'
                    print("🎯 Sorting mode: Pattern")
                elif key == ord('4'):
                    self.sorting_mode = 'random'
                    print("🎯 Sorting mode: Random")
                elif key == ord('5'):
                    self.sorting_mode = 'capacity'
                    print("🎯 Sorting mode: Capacity")
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
        """Start the improved cup sorting system"""
        print("🚀 Starting Improved Cup Sorting System")
        print("=" * 60)
        print("Controls:")
        print("- '1': Sort by position (left/center/right)")
        print("- '2': Sort by distance from center")
        print("- '3': Sort by pattern (alternating zones)")
        print("- '4': Sort randomly")
        print("- '5': Sort by capacity (balance zones)")
        print("- 'r': Reset counts")
        print("- 'q': Quit")
        print("=" * 60)
        print("Features:")
        print("- Zone capacity limits (5 cups per zone)")
        print("- Visual capacity indicators")
        print("- Optimized for uniform cups")
        print("- Multiple sorting strategies")
        print("=" * 60)
        
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
    print("🥤 Improved Real-time Cup Sorting Robot")
    print("=" * 60)
    print("Optimized for uniform cups (same size and color)")
    print("=" * 60)
    
    sorter = ImprovedCupSorting()
    sorter.start()

if __name__ == "__main__":
    main() 