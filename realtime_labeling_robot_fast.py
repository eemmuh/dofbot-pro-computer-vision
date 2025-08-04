#!/usr/bin/env python3
"""
Fast Real-time Cup Detection with Labeling and Robot Movement
Optimized version for better performance
"""

import cv2
import numpy as np
import time
import sys
import os
from typing import List, Tuple, Optional

# Add src directory to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from vision.cup_detector import CupDetector
from robot.dofbot_controller import DOFBOTController

class FastRealtimeLabelingRobot:
    def __init__(self, model_path: str, config_path: str, conf_threshold: float = 0.5):
        self.detector = None
        self.robot = None
        self.camera = None

        # Detection parameters
        self.model_path = model_path
        self.config_path = config_path
        self.conf_threshold = conf_threshold

        # Performance optimization
        self.detection_interval = 10  # Detect every 10 frames
        self.frame_count = 0
        self.last_detections = []
        self.last_detection_time = 0

        # Robot movement parameters
        self.robot_movement_enabled = True
        self.movement_throttle = 60  # Move robot every 60 frames
        self.last_movement_time = 0
        self.movement_cooldown = 3.0  # Seconds between movements

        # Display settings
        self.show_labels = True
        self.show_confidence = True
        self.show_bounding_boxes = True
        self.show_robot_status = True
        self.show_performance = True

        # Color scheme
        self.colors = {
            'high_confidence': (0, 255, 0),    # Green
            'medium_confidence': (0, 255, 255), # Yellow
            'low_confidence': (0, 0, 255),      # Red
            'highest_cup': (255, 0, 255),       # Magenta (highest confidence)
            'text': (255, 255, 255),            # White
            'background': (0, 0, 0),            # Black
            'performance': (0, 255, 255)        # Cyan
        }

    def initialize_systems(self):
        """Initialize camera, detector, and robot"""
        print("🔧 Initializing systems...")

        # Initialize cup detector
        try:
            self.detector = CupDetector(
                self.model_path,
                self.config_path,
                conf_threshold=self.conf_threshold
            )
            print("✅ Cup detector initialized")
        except Exception as e:
            print(f"❌ Failed to initialize detector: {e}")
            return False

        # Initialize robot
        try:
            self.robot = DOFBOTController()
            if not self.robot.connect():
                print("❌ Failed to connect to robot")
                return False
            print("✅ Robot connected")
        except Exception as e:
            print(f"❌ Failed to initialize robot: {e}")
            return False

        # Initialize camera
        try:
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                print("❌ Cannot open camera")
                return False

            # Set camera properties for better performance
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            self.camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer size
            print("✅ Camera initialized")
        except Exception as e:
            print(f"❌ Failed to initialize camera: {e}")
            return False

        return True

    def image_to_robot_coords(self, image_x: int, image_y: int, image_width: int, image_height: int) -> Tuple[float, float, float]:
        """
        Convert image coordinates to robot coordinates for table-mounted cups
        
        Args:
            image_x, image_y: Pixel coordinates in image
            image_width, image_height: Image dimensions
            
        Returns:
            (robot_x, robot_y, robot_z) in meters
        """
        # Normalize coordinates (0-1)
        norm_x = image_x / image_width
        norm_y = image_y / image_height
        
        # Convert to robot workspace coordinates for table
        # Robot home position points at ceiling, so we need to reach down to table
        robot_x = (norm_x - 0.5) * 0.3  # -0.15 to 0.15 meters (left/right)
        robot_y = 0.25 + norm_y * 0.15   # 0.25 to 0.40 meters from robot base
        robot_z = 0.05                   # 5cm above table surface (reach down from ceiling)
        
        return (robot_x, robot_y, robot_z)

    def get_confidence_color(self, confidence: float) -> Tuple[int, int, int]:
        """Get color based on confidence level"""
        if confidence >= 0.8:
            return self.colors['high_confidence']
        elif confidence >= 0.6:
            return self.colors['medium_confidence']
        else:
            return self.colors['low_confidence']

    def draw_cup_labels(self, frame: np.ndarray, detections: List[Tuple], highest_cup_idx: Optional[int] = None) -> np.ndarray:
        """Draw labels and bounding boxes for detected cups"""
        height, width = frame.shape[:2]

        for i, (x, y, w, h, confidence) in enumerate(detections):
            # Determine color (highlight highest confidence cup)
            if i == highest_cup_idx:
                color = self.colors['highest_cup']
                label_prefix = "🎯 "  # Target indicator
            else:
                color = self.get_confidence_color(confidence)
                label_prefix = ""

            # Draw bounding box
            if self.show_bounding_boxes:
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

            # Draw cup label
            if self.show_labels:
                label = f"{label_prefix}Cup {i+1}"
                cv2.putText(frame, label, (x, y - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            # Draw confidence score
            if self.show_confidence:
                conf_text = f"{confidence:.2f}"
                cv2.putText(frame, conf_text, (x, y + h + 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            # Draw center point
            center_x, center_y = x + w // 2, y + h // 2
            cv2.circle(frame, (center_x, center_y), 4, color, -1)

        return frame

    def draw_status_panel(self, frame: np.ndarray, detections: List[Tuple], fps: float, detection_fps: float):
        """Draw status panel with robot and detection info"""
        height, width = frame.shape[:2]

        # Create semi-transparent overlay
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (400, 220), self.colors['background'], -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

        # Draw status information
        y_offset = 30
        line_height = 25

        status_info = [
            f"Display FPS: {fps:.1f}",
            f"Detection FPS: {detection_fps:.1f}",
            f"Cups Detected: {len(detections)}",
            f"Robot Movement: {'ON' if self.robot_movement_enabled else 'OFF'}",
            f"Confidence Threshold: {self.conf_threshold}",
            f"Detection Interval: {self.detection_interval} frames"
        ]

        for info in status_info:
            cv2.putText(frame, info, (20, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.colors['text'], 1)
            y_offset += line_height

        # Show highest confidence cup info
        if detections:
            highest_idx = max(range(len(detections)), key=lambda i: detections[i][4])
            highest_conf = detections[highest_idx][4]
            cv2.putText(frame, f"Highest Confidence: {highest_conf:.3f}", (20, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.colors['highest_cup'], 1)

        return frame

    def move_robot_to_highest_confidence_cup(self, detections: List[Tuple], frame_width: int, frame_height: int):
        """Move robot to the cup with highest confidence"""
        if not self.robot_movement_enabled or not detections:
            return

        # Check cooldown
        current_time = time.time()
        if current_time - self.last_movement_time < self.movement_cooldown:
            return

        # Find highest confidence cup
        highest_idx = max(range(len(detections)), key=lambda i: detections[i][4])
        x, y, w, h, confidence = detections[highest_idx]

        # Convert to robot coordinates
        center_x, center_y = x + w // 2, y + h // 2
        robot_x, robot_y, robot_z = self.image_to_robot_coords(center_x, center_y, frame_width, frame_height)

        print(f"🤖 Moving robot to Cup {highest_idx + 1} (confidence: {confidence:.3f})")
        print(f"   Image coords: ({center_x}, {center_y})")
        print(f"   Robot coords: ({robot_x:.3f}, {robot_y:.3f}, {robot_z:.3f})")

        try:
            # Safety check: ensure robot can reach the position
            if abs(robot_x) > 0.15 or robot_y < 0.20 or robot_y > 0.40 or robot_z < 0.02:
                print(f"⚠️ Position out of safe range, skipping movement")
                return

            # Move robot to position above the cup (reach down from ceiling)
            self.robot.move_to_position(robot_x, robot_y, robot_z, speed=30)  # Slower speed for safety
            self.last_movement_time = current_time
            print(f"✅ Robot movement completed")

            # Optional: Add a small pause to let robot stabilize
            time.sleep(0.5)

        except Exception as e:
            print(f"❌ Robot movement failed: {e}")
            # Try to return to a safe position
            try:
                print("🔄 Attempting to return to safe position...")
                self.robot.home_position()
            except Exception as safe_e:
                print(f"⚠️ Failed to return to safe position: {safe_e}")

    def run_realtime_detection(self):
        """Run the optimized real-time detection with labeling and robot movement"""
        print("🎯 Starting Fast Real-time Cup Detection with Robot Movement")
        print("📋 Controls:")
        print("  - Press 'q' to quit")
        print("  - Press 'r' to toggle robot movement")
        print("  - Press 'l' to toggle labels")
        print("  - Press 'c' to toggle confidence display")
        print("  - Press 'b' to toggle bounding boxes")
        print("  - Press 's' to save screenshot")
        print("  - Press 'm' to manually move robot to highest cup")
        print("  - Press 'k' to enter calibration mode")
        print("  - Press '+' to increase detection interval")
        print("  - Press '-' to decrease detection interval")

        if not self.initialize_systems():
            print("❌ Failed to initialize systems")
            return

        start_time = time.time()
        frame_count = 0
        detection_count = 0
        last_detection_time = time.time()

        try:
            while True:
                # Capture frame
                ret, frame = self.camera.read()
                if not ret:
                    print("❌ Failed to capture frame")
                    break

                frame_count += 1
                frame_start_time = time.time()

                # Detect cups only every N frames for better performance
                if frame_count % self.detection_interval == 0:
                    try:
                        self.last_detections = self.detector.detect_cups(frame)
                        detection_count += 1
                        last_detection_time = time.time()
                    except Exception as e:
                        print(f"⚠️ Detection failed: {e}")
                        # Keep using last detections

                # Calculate FPS
                display_fps = 1.0 / (time.time() - frame_start_time) if frame_start_time > 0 else 0
                detection_fps = detection_count / (time.time() - start_time) if start_time > 0 else 0

                # Find highest confidence cup
                highest_cup_idx = None
                if self.last_detections:
                    highest_cup_idx = max(range(len(self.last_detections)), key=lambda i: self.last_detections[i][4])

                # Draw cup labels and bounding boxes
                frame = self.draw_cup_labels(frame, self.last_detections, highest_cup_idx)

                # Draw status panel
                frame = self.draw_status_panel(frame, self.last_detections, display_fps, detection_fps)

                # Move robot to highest confidence cup (throttled)
                if frame_count % self.movement_throttle == 0:
                    self.move_robot_to_highest_confidence_cup(self.last_detections, frame.shape[1], frame.shape[0])

                # Display frame
                cv2.imshow('Fast Real-time Cup Detection with Robot Movement', frame)

                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("👋 Quitting...")
                    break
                elif key == ord('r'):
                    self.robot_movement_enabled = not self.robot_movement_enabled
                    status = "ON" if self.robot_movement_enabled else "OFF"
                    print(f"🤖 Robot movement: {status}")
                elif key == ord('l'):
                    self.show_labels = not self.show_labels
                    status = "ON" if self.show_labels else "OFF"
                    print(f"🏷️ Labels: {status}")
                elif key == ord('c'):
                    self.show_confidence = not self.show_confidence
                    status = "ON" if self.show_confidence else "OFF"
                    print(f"📊 Confidence display: {status}")
                elif key == ord('b'):
                    self.show_bounding_boxes = not self.show_bounding_boxes
                    status = "ON" if self.show_bounding_boxes else "OFF"
                    print(f"📦 Bounding boxes: {status}")
                elif key == ord('s'):
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    filename = f"realtime_detection_{timestamp}.jpg"
                    cv2.imwrite(filename, frame)
                    print(f"📸 Screenshot saved: {filename}")
                elif key == ord('m'):
                    # Manual movement to highest cup
                    if self.last_detections:
                        self.move_robot_to_highest_confidence_cup(self.last_detections, frame.shape[1], frame.shape[0])
                    else:
                        print("❌ No cups detected for manual movement")
                elif key == ord('k'):
                    # Calibration mode
                    self.enter_calibration_mode(frame)
                elif key == ord('+') or key == ord('='):
                    self.detection_interval = min(30, self.detection_interval + 2)
                    print(f"🔍 Detection interval: {self.detection_interval} frames")
                elif key == ord('-') or key == ord('_'):
                    self.detection_interval = max(5, self.detection_interval - 2)
                    print(f"🔍 Detection interval: {self.detection_interval} frames")

                # Print status every 120 frames
                if frame_count % 120 == 0:
                    print(f"Frame {frame_count}: {len(self.last_detections)} cups detected, Display FPS: {display_fps:.1f}, Detection FPS: {detection_fps:.1f}")

        finally:
            self.camera.release()
            cv2.destroyAllWindows()

            # Return robot to home position
            if self.robot:
                try:
                    print("🏠 Returning robot to home position...")
                    self.robot.home_position()
                except Exception as e:
                    print(f"⚠️ Failed to return to home: {e}")

            # Print final summary
            total_time = time.time() - start_time
            print(f"\n⏱️ Session completed in {total_time:.1f} seconds")
            print(f"📊 Processed {frame_count} frames")
            print(f"🔍 Performed {detection_count} detections")

    def enter_calibration_mode(self, frame):
        """Enter calibration mode to fine-tune robot coordinates"""
        print("\n🔧 Entering Calibration Mode")
        print("Click on the image to test robot movement to that position")
        print("Press 'q' to exit calibration mode")

        # Create a window for calibration
        cv2.namedWindow('Calibration Mode')
        cv2.setMouseCallback('Calibration Mode', self.calibration_mouse_callback)

        calibration_frame = frame.copy()
        cv2.putText(calibration_frame, "Click to test robot position", (50, 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        cv2.putText(calibration_frame, "Press 'q' to exit", (50, 100),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

        while True:
            cv2.imshow('Calibration Mode', calibration_frame)
            key = cv2.waitKey(1) & 0xFF

            if key == ord('q'):
                break

        cv2.destroyWindow('Calibration Mode')
        print("✅ Exited calibration mode")

    def calibration_mouse_callback(self, event, x, y, flags, param):
        """Handle mouse clicks in calibration mode"""
        if event == cv2.EVENT_LBUTTONDOWN:
            # Convert clicked position to robot coordinates
            robot_x, robot_y, robot_z = self.image_to_robot_coords(x, y, 640, 480)

            print(f"🎯 Calibration click at ({x}, {y})")
            print(f"   Robot coords: ({robot_x:.3f}, {robot_y:.3f}, {robot_z:.3f})")

            # Ask user if they want to move robot
            response = input("Move robot to this position? (y/n): ").lower()
            if response == 'y':
                try:
                    self.robot.move_to_position(robot_x, robot_y, robot_z, speed=20)
                    print("✅ Robot moved to calibration position")
                except Exception as e:
                    print(f"❌ Robot movement failed: {e}")

def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description='Fast Real-time Cup Detection with Robot Movement')
    parser.add_argument('--model', default='backup/yolo-cup_final.weights',
                       help='Path to trained YOLO model')
    parser.add_argument('--config', default='cfg/yolo-cup.cfg',
                       help='Path to YOLO config file')
    parser.add_argument('--conf-threshold', type=float, default=0.5,
                       help='Confidence threshold for detections')
    parser.add_argument('--camera', type=int, default=0,
                       help='Camera index')
    parser.add_argument('--detection-interval', type=int, default=10,
                       help='Detect every N frames (higher = faster)')

    args = parser.parse_args()

    # Create and run real-time detection
    detector = FastRealtimeLabelingRobot(
        model_path=args.model,
        config_path=args.config,
        conf_threshold=args.conf_threshold
    )
    detector.detection_interval = args.detection_interval

    detector.run_realtime_detection()

if __name__ == "__main__":
    main() 