#!/usr/bin/env python3
"""
Simple Working Detector with Fallback
Handles YOLO detection with timeout and fallback to simple CV
"""

import cv2
import numpy as np
import time
import sys
import os
import subprocess
import tempfile
from pathlib import Path

class SimpleWorkingDetector:
    def __init__(self, config_path="cfg/yolo-cup-tiny.cfg", 
                 model_path="backup/yolo-cup-tiny_last.weights",
                 names_path="cup.names",
                 confidence_threshold=0.5):
        self.config_path = config_path
        self.model_path = model_path
        self.names_path = names_path
        self.conf_threshold = confidence_threshold
        
        # Check if files exist
        self.check_files()
        
    def check_files(self):
        """Check if required files exist"""
        files_to_check = [
            self.config_path,
            self.model_path,
            self.names_path
        ]
        
        for file_path in files_to_check:
            if not os.path.exists(file_path):
                print(f"⚠️  Warning: {file_path} not found")
    
    def detect_with_yolo(self, frame):
        """Detect cups using YOLO with timeout"""
        try:
            # Save frame to temporary file
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                temp_image_path = temp_file.name
                cv2.imwrite(temp_image_path, frame)
            
            # Get absolute paths
            abs_config_path = os.path.abspath(self.config_path)
            abs_model_path = os.path.abspath(self.model_path)
            abs_names_path = os.path.abspath(self.names_path)
            
            # Darknet command
            darknet_dir = "darknet"
            cmd = [
                "./darknet", "detect", abs_config_path, abs_model_path, temp_image_path,
                "-thresh", str(self.conf_threshold),
                "-names", abs_names_path
            ]
            
            # Run darknet with timeout
            result = subprocess.run(
                cmd, 
                cwd=darknet_dir, 
                capture_output=True, 
                text=True, 
                timeout=5  # 5 second timeout
            )
            
            # Clean up temp file
            os.unlink(temp_image_path)
            
            if result.returncode == 0:
                # Parse output for detections
                detections = self.parse_darknet_output(result.stdout)
                return detections
            else:
                print(f"❌ Darknet error: {result.stderr}")
                return []
                
        except subprocess.TimeoutExpired:
            print("⏰ YOLO detection timed out, using fallback")
            return []
        except Exception as e:
            print(f"❌ YOLO detection error: {e}")
            return []
    
    def parse_darknet_output(self, output):
        """Parse darknet output for detections"""
        detections = []
        lines = output.strip().split('\n')
        
        for line in lines:
            if 'cup' in line.lower() and '%' in line:
                # Parse detection line
                parts = line.split()
                if len(parts) >= 6:
                    try:
                        confidence = float(parts[1].replace('%', '')) / 100.0
                        x = int(float(parts[2]))
                        y = int(float(parts[3]))
                        w = int(float(parts[4]))
                        h = int(float(parts[5]))
                        
                        if confidence > self.conf_threshold:
                            detections.append({
                                'bbox': (x, y, w, h),
                                'confidence': confidence,
                                'center': (x + w//2, y + h//2)
                            })
                    except (ValueError, IndexError):
                        continue
        
        return detections
    
    def detect_with_simple_cv(self, frame):
        """Fallback detection using simple computer vision"""
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
        
        # Apply morphological operations
        kernel = np.ones((5,5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        detections = []
        for contour in contours:
            # Filter by area
            area = cv2.contourArea(contour)
            if area > 1000:  # Minimum area for cup
                # Get bounding rectangle
                x, y, w, h = cv2.boundingRect(contour)
                
                # Filter by aspect ratio
                aspect_ratio = w / h if h > 0 else 0
                if 0.3 < aspect_ratio < 3.0:
                    # Calculate confidence based on area
                    confidence = min(0.9, area / 10000)
                    
                    detections.append({
                        'bbox': (x, y, w, h),
                        'confidence': confidence,
                        'center': (x + w//2, y + h//2)
                    })
        
        return detections
    
    def detect(self, frame):
        """Main detection method with fallback"""
        # Try YOLO first
        yolo_detections = self.detect_with_yolo(frame)
        
        if yolo_detections:
            return yolo_detections
        
        # Fallback to simple CV
        print("🔄 Using simple CV fallback detection")
        return self.detect_with_simple_cv(frame)

def main():
    """Test the detector"""
    print("🔧 Simple Working Detector Test")
    print("=" * 40)
    
    # Initialize detector
    detector = SimpleWorkingDetector()
    
    # Initialize camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Could not open camera")
        return
    
    print("✅ Camera initialized")
    print("Press 'q' to quit")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        
        # Detect cups
        detections = detector.detect(frame)
        
        # Draw detections
        for detection in detections:
            x, y, w, h = detection['bbox']
            confidence = detection['confidence']
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, f"Cup: {confidence:.2f}", (x, y - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Draw status
        cv2.putText(frame, f"Detections: {len(detections)}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, "Press 'q' to quit", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        cv2.imshow('Simple Working Detector', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()