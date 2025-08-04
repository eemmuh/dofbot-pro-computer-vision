#!/usr/bin/env python3
"""
Simple Cup Detection with Working Controls
No threading - everything in main loop for reliable control
"""

import cv2
import numpy as np
import time
import sys
import os
import argparse

# Add src directory to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from vision.cup_detector import CupDetector
from robot.dofbot_controller import DOFBOTController

class SimpleCupDetection:
    def __init__(self, model_path: str, config_path: str, conf_threshold: float = 0.5):
        self.detector = None
        self.robot = None
        self.camera = None
        
        # Detection parameters
        self.model_path = model_path
        self.config_path = config_path
        self.conf_threshold = conf_threshold
        
        # Display settings
        self.show_labels = True
        self.show_confidence = True
        self.show_bounding_boxes = True
        self.camera_flipped = True
        
        # Robot settings
        self.robot_enabled = True
        self.robot_connected = False
        
        # Color scheme
        self.colors = {
            'high_confidence': (0, 255, 0),    # Green
            'medium_confidence': (0, 255, 255), # Yellow
            'low_confidence': (0, 0, 255),      # Red
            'text': (255, 255, 255),            # White
            'background': (0, 0, 0)             # Black
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
            if self.robot.connect():
                self.robot_connected = True
                print("✅ Robot connected")
            else:
                print("⚠️ Robot not connected - running without robot")
                self.robot_connected = False
        except Exception as e:
            print(f"⚠️ Robot initialization failed: {e}")
            self.robot_connected = False

        # Initialize camera
        try:
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                print("❌ Cannot open camera")
                return False

            # Set camera properties
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            print("✅ Camera initialized")
        except Exception as e:
            print(f"❌ Failed to initialize camera: {e}")
            return False

        return True

    def draw_detections(self, frame, detections):
        """Draw detections on frame"""
        for i, (x, y, w, h, confidence) in enumerate(detections):
            # Get color based on confidence
            if confidence >= 0.8:
                color = self.colors['high_confidence']
            elif confidence >= 0.6:
                color = self.colors['medium_confidence']
            else:
                color = self.colors['low_confidence']

            # Draw bounding box
            if self.show_bounding_boxes:
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

            # Draw cup label
            if self.show_labels:
                label = f"Cup {i+1}"
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

    def draw_status_panel(self, frame, detections, fps):
        """Draw status panel"""
        height, width = frame.shape[:2]

        # Create semi-transparent overlay
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (350, 150), self.colors['background'], -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

        # Draw status information
        y_offset = 30
        line_height = 25

        status_info = [
            f"FPS: {fps:.1f}",
            f"Cups Detected: {len(detections)}",
            f"Robot: {'CONNECTED' if self.robot_connected else 'DISCONNECTED'}",
            f"Camera Flip: {'ON' if self.camera_flipped else 'OFF'}",
            f"Confidence Threshold: {self.conf_threshold}"
        ]

        for info in status_info:
            cv2.putText(frame, info, (20, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.colors['text'], 1)
            y_offset += line_height

        return frame

    def test_robot(self):
        """Test robot movements"""
        if not self.robot_connected:
            print("❌ Robot not connected")
            return

        print("🧪 Testing robot movements...")
        try:
            # Move to a test position
            self.robot.move_to_position(0.0, 0.25, 0.10, speed=30)
            time.sleep(2)
            
            # Return to home
            self.robot.home_position()
            print("✅ Robot test completed")
        except Exception as e:
            print(f"❌ Robot test failed: {e}")

    def home_robot(self):
        """Home the robot"""
        if not self.robot_connected:
            print("❌ Robot not connected")
            return

        print("🏠 Homing robot...")
        try:
            self.robot.home_position()
            print("✅ Robot homed")
        except Exception as e:
            print(f"❌ Robot homing failed: {e}")

    def run(self):
        """Main run loop"""
        print("🎯 Starting Simple Cup Detection")
        print("📋 Controls:")
        print("  - Press 'q' to quit")
        print("  - Press 't' to test robot")
        print("  - Press 'h' to home robot")
        print("  - Press 'f' to toggle camera flip")
        print("  - Press 'l' to toggle labels")
        print("  - Press 'c' to toggle confidence")
        print("  - Press 'b' to toggle bounding boxes")
        print("  - Press 's' to save screenshot")

        if not self.initialize_systems():
            print("❌ Failed to initialize systems")
            return

        frame_count = 0
        start_time = time.time()

        try:
            while True:
                # Capture frame
                ret, frame = self.camera.read()
                if not ret:
                    print("❌ Failed to capture frame")
                    break

                frame_count += 1
                frame_start_time = time.time()

                # Flip camera if needed
                if self.camera_flipped:
                    frame = cv2.flip(frame, 0)

                # Detect cups
                try:
                    detections = self.detector.detect_cups(frame)
                except Exception as e:
                    print(f"⚠️ Detection failed: {e}")
                    detections = []

                # Calculate FPS
                fps = 1.0 / (time.time() - frame_start_time) if frame_start_time > 0 else 0

                # Draw detections
                frame = self.draw_detections(frame, detections)

                # Draw status panel
                frame = self.draw_status_panel(frame, detections, fps)

                # Display frame
                cv2.imshow('Simple Cup Detection', frame)

                # Handle key presses - use longer wait time for better responsiveness
                key = cv2.waitKey(50) & 0xFF  # Wait 50ms
                
                if key != 255:  # Key was pressed
                    print(f"🔑 Key pressed: {chr(key)}")

                if key == ord('q'):
                    print("👋 Quitting...")
                    break
                elif key == ord('t'):
                    self.test_robot()
                elif key == ord('h'):
                    self.home_robot()
                elif key == ord('f'):
                    self.camera_flipped = not self.camera_flipped
                    status = "ON" if self.camera_flipped else "OFF"
                    print(f"🔄 Camera flip: {status}")
                elif key == ord('l'):
                    self.show_labels = not self.show_labels
                    status = "ON" if self.show_labels else "OFF"
                    print(f"🏷️ Labels: {status}")
                elif key == ord('c'):
                    self.show_confidence = not self.show_confidence
                    status = "ON" if self.show_confidence else "OFF"
                    print(f"📊 Confidence: {status}")
                elif key == ord('b'):
                    self.show_bounding_boxes = not self.show_bounding_boxes
                    status = "ON" if self.show_bounding_boxes else "OFF"
                    print(f"📦 Bounding boxes: {status}")
                elif key == ord('s'):
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    filename = f"cup_detection_{timestamp}.jpg"
                    cv2.imwrite(filename, frame)
                    print(f"📸 Screenshot saved: {filename}")

                # Print status every 60 frames
                if frame_count % 60 == 0:
                    print(f"Frame {frame_count}: {len(detections)} cups detected, FPS: {fps:.1f}")

        finally:
            self.camera.release()
            cv2.destroyAllWindows()

            # Return robot to home position
            if self.robot_connected:
                try:
                    print("🏠 Returning robot to home position...")
                    self.robot.home_position()
                except Exception as e:
                    print(f"⚠️ Failed to return to home: {e}")

            # Print final summary
            total_time = time.time() - start_time
            print(f"\n⏱️ Session completed in {total_time:.1f} seconds")
            print(f"📊 Processed {frame_count} frames")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Simple Cup Detection with Working Controls')
    parser.add_argument('--model', default='backup/yolo-cup-memory-optimized_final.weights',
                       help='Path to trained YOLO model')
    parser.add_argument('--config', default='cfg/yolo-cup-memory-optimized.cfg',
                       help='Path to YOLO config file')
    parser.add_argument('--conf-threshold', type=float, default=0.5,
                       help='Confidence threshold for detections')

    args = parser.parse_args()

    # Create and run detection
    detector = SimpleCupDetection(
        model_path=args.model,
        config_path=args.config,
        conf_threshold=args.conf_threshold
    )

    detector.run()

if __name__ == "__main__":
    main() 