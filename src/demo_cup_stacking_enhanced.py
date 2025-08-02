#!/usr/bin/env python3
"""
Enhanced Cup Stacking Demo
Complete integration of vision, robot control, and stacking algorithms
"""

import cv2
import time
import numpy as np
import threading
from typing import List, Tuple, Optional
import argparse
import sys
import os

# Add src to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from vision.cup_detector import CupDetector
from robot.dofbot_controller import DOFBOTController
from robot.stacking_controller import StackingController

class CupStackingSystem:
    def __init__(self, model_path: str, camera_id: int = 0, conf_threshold: float = 0.5):
        """
        Initialize the complete cup stacking system
        
        Args:
            model_path: Path to trained YOLO weights
            camera_id: Camera device ID
            conf_threshold: Detection confidence threshold
        """
        self.camera_id = camera_id
        self.conf_threshold = conf_threshold
        self.running = False
        self.paused = False
        
        # Initialize components
        print("🔧 Initializing Cup Stacking System...")
        
        # Initialize camera
        self.cap = cv2.VideoCapture(camera_id)
        if not self.cap.isOpened():
            raise RuntimeError(f"Could not open camera {camera_id}")
        
        # Set camera properties for better performance
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        print("✅ Camera initialized")
        
        # Initialize cup detector
        try:
            self.detector = CupDetector(model_path=model_path, conf_threshold=conf_threshold)
            print("✅ Cup detector initialized")
        except Exception as e:
            print(f"❌ Failed to initialize cup detector: {e}")
            raise
        
        # Initialize robot controller
        try:
            self.robot = DOFBOTController()
            if not self.robot.connected:
                print("⚠️ Robot not connected - running in simulation mode")
                self.simulation_mode = True
            else:
                self.simulation_mode = False
                print("✅ Robot controller initialized")
        except Exception as e:
            print(f"⚠️ Robot initialization failed: {e}")
            self.simulation_mode = True
        
        # Initialize stacking controller
        if not self.simulation_mode:
            self.stacker = StackingController(self.robot)
            print("✅ Stacking controller initialized")
        else:
            self.stacker = None
        
        # System state
        self.current_frame = None
        self.detections = []
        self.cup_positions = []
        self.stack_count = 0
        self.total_cups_processed = 0
        
        # Threading for smooth UI
        self.frame_thread = None
        self.detection_thread = None
        
        print("🎉 Cup Stacking System Ready!")
    
    def start(self):
        """Start the cup stacking system"""
        self.running = True
        
        # Start frame capture thread
        self.frame_thread = threading.Thread(target=self._frame_capture_loop)
        self.frame_thread.daemon = True
        self.frame_thread.start()
        
        # Start detection thread
        self.detection_thread = threading.Thread(target=self._detection_loop)
        self.detection_thread.daemon = True
        self.detection_thread.start()
        
        print("🚀 System started - Press 'h' for help")
    
    def stop(self):
        """Stop the cup stacking system"""
        self.running = False
        
        if self.frame_thread:
            self.frame_thread.join(timeout=1)
        if self.detection_thread:
            self.detection_thread.join(timeout=1)
        
        self.cap.release()
        cv2.destroyAllWindows()
        
        if not self.simulation_mode and self.robot:
            self.robot.disconnect()
        
        print("🛑 System stopped")
    
    def _frame_capture_loop(self):
        """Thread for continuous frame capture"""
        while self.running:
            if not self.paused:
                ret, frame = self.cap.read()
                if ret:
                    self.current_frame = frame
                else:
                    print("⚠️ Failed to capture frame")
                    time.sleep(0.1)
            else:
                time.sleep(0.1)
    
    def _detection_loop(self):
        """Thread for continuous cup detection"""
        while self.running:
            if not self.paused and self.current_frame is not None:
                try:
                    # Detect cups
                    self.detections = self.detector.detect_cups(self.current_frame)
                    self.cup_positions = self.detector.get_cup_positions(self.current_frame)
                except Exception as e:
                    print(f"⚠️ Detection error: {e}")
                    self.detections = []
                    self.cup_positions = []
                
                # Limit detection frequency
                time.sleep(0.1)
            else:
                time.sleep(0.1)
    
    def execute_stack_sequence(self):
        """Execute the cup stacking sequence"""
        if self.simulation_mode:
            print("🎭 Simulation Mode: Would stack {} cups".format(len(self.cup_positions)))
            self._simulate_stacking()
            return
        
        if not self.cup_positions:
            print("❌ No cups detected for stacking")
            return
        
        print(f"🚀 Starting stacking sequence with {len(self.cup_positions)} cups...")
        
        try:
            # Execute stacking
            self.stacker.execute_stack_sequence(self.cup_positions)
            self.stack_count += 1
            self.total_cups_processed += len(self.cup_positions)
            print(f"✅ Stacking sequence completed! Total stacks: {self.stack_count}")
        except Exception as e:
            print(f"❌ Stacking sequence failed: {e}")
    
    def _simulate_stacking(self):
        """Simulate stacking sequence for demo purposes"""
        print("🎭 Simulating stacking sequence...")
        
        for i, (x, y, z) in enumerate(self.cup_positions):
            print(f"🎭 Simulating: Pick cup {i+1} at ({x:.2f}, {y:.2f}, {z:.2f})")
            time.sleep(0.5)
            print(f"🎭 Simulating: Place cup {i+1} in stack")
            time.sleep(0.5)
        
        print("🎭 Simulation completed!")
    
    def test_robot(self):
        """Test robot movements"""
        if self.simulation_mode:
            print("🎭 Simulation Mode: Would test robot movements")
            return
        
        print("🧪 Testing robot movements...")
        try:
            self.robot.test_servos()
            print("✅ Robot test completed")
        except Exception as e:
            print(f"❌ Robot test failed: {e}")
    
    def home_robot(self):
        """Move robot to home position"""
        if self.simulation_mode:
            print("🎭 Simulation Mode: Would move to home position")
            return
        
        print("🏠 Moving robot to home position...")
        try:
            self.robot.home_position()
            print("✅ Robot moved to home position")
        except Exception as e:
            print(f"❌ Failed to move to home position: {e}")
    
    def run_ui(self):
        """Run the main user interface"""
        print("\n" + "="*50)
        print("🥤 CUP STACKING SYSTEM - ENHANCED DEMO")
        print("="*50)
        print("Controls:")
        print("  'q' - Quit")
        print("  's' - Start stacking sequence")
        print("  't' - Test robot movements")
        print("  'h' - Home robot")
        print("  'p' - Pause/Resume detection")
        print("  'r' - Reset statistics")
        print("  'i' - Show system info")
        print("="*50)
        
        while self.running:
            if self.current_frame is not None:
                # Create display frame
                display_frame = self.current_frame.copy()
                
                # Draw detections
                if self.detections:
                    display_frame = self.detector.draw_detections(display_frame, self.detections)
                
                # Draw UI overlay
                self._draw_ui_overlay(display_frame)
                
                # Show frame
                cv2.imshow('Cup Stacking System - Enhanced', display_frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                self.execute_stack_sequence()
            elif key == ord('t'):
                self.test_robot()
            elif key == ord('h'):
                self.home_robot()
            elif key == ord('p'):
                self.paused = not self.paused
                status = "PAUSED" if self.paused else "RESUMED"
                print(f"⏸️ Detection {status}")
            elif key == ord('r'):
                self.stack_count = 0
                self.total_cups_processed = 0
                print("🔄 Statistics reset")
            elif key == ord('i'):
                self._show_system_info()
        
        self.stop()
    
    def _draw_ui_overlay(self, frame):
        """Draw UI overlay on frame"""
        height, width = frame.shape[:2]
        
        # Background for text
        cv2.rectangle(frame, (0, 0), (width, 80), (0, 0, 0), -1)
        cv2.rectangle(frame, (0, 0), (width, 80), (255, 255, 255), 2)
        
        # System status
        status = "SIMULATION" if self.simulation_mode else "ROBOT CONNECTED"
        status_color = (0, 255, 255) if self.simulation_mode else (0, 255, 0)
        cv2.putText(frame, f"Status: {status}", (10, 25), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)
        
        # Detection info
        cv2.putText(frame, f"Cups: {len(self.detections)}", (10, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Statistics
        cv2.putText(frame, f"Stacks: {self.stack_count} | Total: {self.total_cups_processed}", 
                   (width - 300, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Pause indicator
        if self.paused:
            cv2.putText(frame, "PAUSED", (width - 150, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        
        # Instructions
        cv2.putText(frame, "Press 's' to stack, 'q' to quit", (10, height - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    def _show_system_info(self):
        """Display system information"""
        print("\n" + "="*40)
        print("📊 SYSTEM INFORMATION")
        print("="*40)
        print(f"Camera ID: {self.camera_id}")
        print(f"Detection Threshold: {self.conf_threshold}")
        print(f"Robot Connected: {not self.simulation_mode}")
        print(f"Total Stacks: {self.stack_count}")
        print(f"Total Cups Processed: {self.total_cups_processed}")
        print(f"Current Detections: {len(self.detections)}")
        print("="*40)

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Enhanced Cup Stacking Demo")
    parser.add_argument("--model", default="backup/yolo-cup-memory-optimized_final.weights",
                       help="Path to YOLO model weights")
    parser.add_argument("--camera", type=int, default=0, help="Camera device ID")
    parser.add_argument("--conf", type=float, default=0.5, help="Detection confidence threshold")
    
    args = parser.parse_args()
    
    try:
        # Initialize system
        system = CupStackingSystem(
            model_path=args.model,
            camera_id=args.camera,
            conf_threshold=args.conf
        )
        
        # Start system
        system.start()
        
        # Run UI
        system.run_ui()
        
    except KeyboardInterrupt:
        print("\n⏹️ Interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 