#!/usr/bin/env python3
"""
Real-time Cup Stacking Robot (Calibrated)
Uses YOLO detection + calibrated positions for accurate cup stacking
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

# Try to import calibrated positions
try:
    from calibrated_cup_positions import CUP_POSITIONS, STACK_POSITION
    print("✅ Loaded calibrated positions")
    CALIBRATED_POSITIONS_AVAILABLE = True
except ImportError:
    print("⚠️ No calibrated positions found - using default positions")
    CALIBRATED_POSITIONS_AVAILABLE = False
    # Default positions
    CUP_POSITIONS = [
        [60, 90, 90, 90, 90, 30],   # Cup 1 - Left
        [90, 90, 90, 90, 90, 30],   # Cup 2 - Center
        [120, 90, 90, 90, 90, 30],  # Cup 3 - Right
    ]
    STACK_POSITION = [90, 90, 90, 90, 90, 30]

class CalibratedRealtimeCupStacking:
    def __init__(self):
        self.camera = None
        self.detector = None
        self.robot = None
        self.running = False
        
        # Detection settings
        self.confidence_threshold = 0.5
        self.min_cup_size = 50
        self.max_cups_to_stack = len(CUP_POSITIONS)
        
        # Robot settings
        self.pickup_speed = 2000
        self.placement_speed = 1500
        self.approach_speed = 1000
        
        # Stacking state
        self.cups_stacked = 0
        self.stack_height = 0
        self.cup_height = 0.12  # meters per cup
        self.is_stacking = False
        self.current_cup_index = 0
        
        # Position tracking
        self.detection_history = deque(maxlen=10)
        self.stable_detection_threshold = 3
        
        # Calibrated positions
        self.cup_positions = CUP_POSITIONS.copy()
        self.stack_position = STACK_POSITION.copy()
        
        # Manual fine-tuning mode
        self.manual_mode = False
        self.fine_tune_offset = [0, 0, 0, 0, 0, 0]  # Offset for each servo
        
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
    
    def get_calibrated_cup_position(self, cup_index):
        """Get calibrated position for a specific cup"""
        if cup_index < len(self.cup_positions):
            # Apply fine-tuning offset
            position = self.cup_positions[cup_index].copy()
            for i in range(6):
                position[i] += self.fine_tune_offset[i]
            return position
        else:
            print(f"❌ No calibrated position for cup {cup_index}")
            return None
    
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
    
    def stack_next_cup(self):
        """Stack the next cup in sequence"""
        print(f"🔍 stack_next_cup called - is_stacking: {self.is_stacking}, current_cup_index: {self.current_cup_index}")
        
        if self.is_stacking:
            print("⚠️ Already stacking, skipping...")
            return False
            
        if self.current_cup_index >= len(self.cup_positions):
            print("⚠️ All cups have been stacked!")
            return False
        
        self.is_stacking = True
        print("✅ Starting stacking sequence...")
        
        try:
            cup_number = self.current_cup_index + 1
            print(f"\n🎯 Stacking cup {cup_number}/{len(self.cup_positions)}")
            
            # Get calibrated position for this cup
            cup_position = self.get_calibrated_cup_position(self.current_cup_index)
            if not cup_position:
                print("❌ Could not get calibrated position")
                return False
            
            print(f"📍 Using calibrated position: {cup_position}")
            
            # Pick up the cup
            print("🤖 Starting pickup sequence...")
            if self.pickup_cup(cup_position):
                print("✅ Pickup successful, starting placement...")
                # Place in stack
                if self.place_cup_in_stack():
                    print(f"🎉 Successfully stacked cup {cup_number}!")
                    self.current_cup_index += 1
                    return True
                else:
                    print("❌ Failed to place cup in stack")
            else:
                print("❌ Failed to pick up cup")
                
        except Exception as e:
            print(f"❌ Stacking error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.is_stacking = False
            print("✅ Stacking sequence completed")
        
        return False
    
    def manual_fine_tune(self):
        """Enter manual fine-tuning mode"""
        print("🎮 Manual Fine-Tuning Mode")
        print("Controls:")
        print("- '1-6' + number: Adjust servo offset (e.g., '1 5' adds 5° to servo 1)")
        print("- 'reset': Reset all offsets to 0")
        print("- 'show': Show current offsets")
        print("- 'test': Test current cup position")
        print("- 'q': Exit fine-tuning")
        
        while True:
            command = input("\nEnter command: ").strip().lower()
            if command == 'q':
                break
            elif command == 'reset':
                self.fine_tune_offset = [0, 0, 0, 0, 0, 0]
                print("✅ Offsets reset to 0")
            elif command == 'show':
                print(f"Current offsets: {self.fine_tune_offset}")
            elif command == 'test':
                if self.current_cup_index < len(self.cup_positions):
                    position = self.get_calibrated_cup_position(self.current_cup_index)
                    print(f"Testing position: {position}")
                    self.move_robot_to_position(position, 2000)
                else:
                    print("❌ No more cups to test")
            elif len(command.split()) == 2:
                try:
                    servo_id = int(command.split()[0])
                    offset = int(command.split()[1])
                    if 1 <= servo_id <= 6:
                        self.fine_tune_offset[servo_id - 1] += offset
                        print(f"✅ Servo {servo_id} offset adjusted by {offset}°")
                    else:
                        print("❌ Servo ID must be 1-6")
                except:
                    print("❌ Invalid command")
            else:
                print("❌ Invalid command")
    
    def detection_loop(self):
        """Main detection and stacking loop"""
        print("🔄 Starting real-time detection loop...")
        print("💡 Tip: You can also type commands in the console (s, h, m, q)")
        
        # Start a separate thread for console input
        import threading
        console_thread = threading.Thread(target=self.console_input_loop, daemon=True)
        console_thread.start()
        
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
                if detections and not self.is_stacking and self.current_cup_index < len(self.cup_positions):
                    # Get the largest detection (closest cup)
                    largest_detection = max(detections, key=lambda d: d[2] * d[3])
                    
                    # Check if detection is stable
                    if self.is_stable_detection(largest_detection):
                        # Start stacking in a separate thread
                        stacking_thread = threading.Thread(target=self.stack_next_cup)
                        stacking_thread.start()
                
                # Draw detections on frame
                for detection in detections:
                    x, y, w, h = detection
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(frame, f"Cup", (x, y - 10), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                # Draw status information
                cv2.putText(frame, f"Cups Stacked: {self.cups_stacked}/{len(self.cup_positions)}", 
                          (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(frame, f"Stack Height: {self.stack_height:.3f}m", 
                          (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(frame, f"Next Cup: {self.current_cup_index + 1}", 
                          (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                if self.is_stacking:
                    cv2.putText(frame, "STACKING...", (10, 120), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                if self.manual_mode:
                    cv2.putText(frame, "MANUAL MODE", (10, 150), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                
                # Show frame
                cv2.imshow('Calibrated Real-time Cup Stacking', frame)
                
                # Check for key press (camera window)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("⏹️ Quit requested")
                    break
                elif key == ord('h'):
                    print("🏠 Moving to home position...")
                    self.robot.Arm_serial_servo_write6(90, 90, 90, 90, 90, 30, 3000)
                    time.sleep(3)
                elif key == ord('m'):
                    print("🎮 Entering manual fine-tuning mode...")
                    self.manual_fine_tune()
                elif key == ord('s'):
                    self.handle_stack_command()
                
            except Exception as e:
                print(f"❌ Detection loop error: {e}")
                continue
    
    def console_input_loop(self):
        """Handle console input in a separate thread"""
        while self.running:
            try:
                command = input().strip().lower()
                if command == 's':
                    self.handle_stack_command()
                elif command == 'h':
                    print("🏠 Moving to home position...")
                    self.robot.Arm_serial_servo_write6(90, 90, 90, 90, 90, 30, 3000)
                    time.sleep(3)
                elif command == 'm':
                    print("🎮 Entering manual fine-tuning mode...")
                    self.manual_fine_tune()
                elif command == 'q':
                    print("⏹️ Quit requested")
                    self.running = False
                    break
                elif command == 'status':
                    print(f"📊 Status: Cups stacked: {self.cups_stacked}/{len(self.cup_positions)}, Next cup: {self.current_cup_index + 1}")
                else:
                    print(f"❓ Unknown command: {command}")
            except EOFError:
                break
            except Exception as e:
                print(f"❌ Console input error: {e}")
    
    def handle_stack_command(self):
        """Handle the stack command from either camera window or console"""
        print("🔄 Starting stacking sequence...")
        if not self.is_stacking and self.current_cup_index < len(self.cup_positions):
            print(f"🎯 Manually starting cup {self.current_cup_index + 1}")
            # Run stacking directly instead of in thread for manual command
            self.stack_next_cup()
        else:
            if self.is_stacking:
                print("⚠️ Already stacking, please wait...")
            else:
                print("⚠️ All cups have been stacked!")
    
    def start(self):
        """Start the calibrated real-time cup stacking system"""
        print("🚀 Starting Calibrated Real-time Cup Stacking System")
        print("=" * 60)
        
        # Show calibrated positions
        print(f"📊 Using {len(self.cup_positions)} calibrated cup positions:")
        for i, pos in enumerate(self.cup_positions):
            print(f"   Cup {i+1}: {pos}")
        print(f"   Stack position: {self.stack_position}")
        
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
        print("- 'm': Manual fine-tuning mode")
        print("- 's': Start stacking sequence")
        print("- Place cups in camera view to start automatic stacking")
        print("- System will use calibrated positions for accurate picking")
        
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
    print("🥤 Calibrated Real-time Cup Stacking Robot")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists('src/vision/cup_detector.py'):
        print("❌ Please run this script from the project root directory")
        return
    
    # Create and start the system
    system = CalibratedRealtimeCupStacking()
    system.start()

if __name__ == "__main__":
    main() 