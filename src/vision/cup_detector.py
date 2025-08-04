#!/usr/bin/env python3
"""
Cup Detector using YOLO/Darknet
Detects red Solo cups in images using trained YOLO model
"""

import cv2
import numpy as np
import os
import subprocess
import tempfile
from typing import List, Tuple

class CupDetector:
    def __init__(self, model_path: str, config_path: str, conf_threshold: float = 0.5, nms_threshold: float = 0.4):
        """
        Initialize cup detector
        
        Args:
            model_path: Path to trained YOLO weights file
            config_path: Path to YOLO config file
            conf_threshold: Confidence threshold for detections
            nms_threshold: Non-maximum suppression threshold
        """
        self.model_path = model_path
        self.config_path = config_path
        self.conf_threshold = conf_threshold
        self.nms_threshold = nms_threshold
        
        # Get the names file path (cup.names)
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.names_path = os.path.join(root_dir, "cup.names")
        
        # Verify files exist
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model file not found: {self.model_path}")
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        if not os.path.exists(self.names_path):
            raise FileNotFoundError(f"Names file not found: {self.names_path}")
        
        print(f"✅ Cup detector initialized with:")
        print(f"   Model: {self.model_path}")
        print(f"   Config: {self.config_path}")
        print(f"   Names: {self.names_path}")
        print(f"   Confidence threshold: {self.conf_threshold}")
    
    def detect_cups(self, frame: np.ndarray) -> List[Tuple[int, int, int, int, float]]:
        """
        Detect cups in the given frame using Darknet.
        
        Args:
            frame: Input image frame
            
        Returns:
            List of detections in format (x, y, w, h, confidence)
        """
        # Save frame to temporary file
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
            cv2.imwrite(tmp_file.name, frame)
            temp_image_path = tmp_file.name
        
        try:
            # Run Darknet detection with explicit names file
            # Use absolute paths for model and config files since darknet runs from its own directory
            abs_model_path = os.path.abspath(self.model_path)
            abs_config_path = os.path.abspath(self.config_path)
            abs_names_path = os.path.abspath(self.names_path)
            
            cmd = [
                "./darknet", "detect", abs_config_path, abs_model_path, temp_image_path,
                "-thresh", str(self.conf_threshold),
                "-names", abs_names_path  # Explicitly specify the names file
            ]
            
            # Change to darknet directory for execution
            darknet_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "darknet")
            result = subprocess.run(cmd, cwd=darknet_dir, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"Darknet error: {result.stderr}")
                return []
            
            # Parse Darknet output
            detections = self._parse_darknet_output(result.stdout, frame.shape)
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_image_path):
                os.unlink(temp_image_path)
        
        return detections
    
    def _parse_darknet_output(self, output: str, frame_shape: Tuple[int, ...]) -> List[Tuple[int, int, int, int, float]]:
        """
        Parse Darknet detection output.
        
        Args:
            output: Darknet stdout output
            frame_shape: Original frame shape (height, width, channels)
            
        Returns:
            List of detections in format (x, y, w, h, confidence)
        """
        detections = []
        height, width = frame_shape[:2]
        
        lines = output.strip().split('\n')
        
        # Look for detection lines
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Check if this line contains a detection (cup class with percentage)
            if 'cup:' in line and '%' in line:
                # Parse the detection line
                parts = line.split(':')
                if len(parts) >= 2:
                    class_name = parts[0].strip()
                    confidence_str = parts[1].strip().replace('%', '')
                    
                    try:
                        confidence = float(confidence_str) / 100.0
                        
                        # Look for bounding box coordinates in previous lines
                        for j in range(max(0, i-5), i):  # Check last 5 lines
                            prev_line = lines[j].strip()
                            if prev_line and all(c.isdigit() or c in '.-' for c in prev_line):
                                coords = prev_line.split()
                                if len(coords) >= 4:
                                    try:
                                        center_x = float(coords[0]) * width
                                        center_y = float(coords[1]) * height
                                        w = float(coords[2]) * width
                                        h = float(coords[3]) * height
                                        
                                        x = int(center_x - w / 2)
                                        y = int(center_y - h / 2)
                                        
                                        detections.append((x, y, int(w), int(h), confidence))
                                        break
                                    except (ValueError, IndexError):
                                        continue
                    except ValueError:
                        continue
        
        return detections
    
    def get_cup_positions(self, frame: np.ndarray) -> List[Tuple[float, float, float]]:
        """
        Get 3D positions of detected cups.
        
        Args:
            frame: Input image frame
            
        Returns:
            List of (x, y, z) positions for each cup
        """
        detections = self.detect_cups(frame)
        positions = []
        
        for x, y, w, h, confidence in detections:
            # Calculate center of cup in image coordinates
            center_x = x + w // 2
            center_y = y + h // 2
            
            # TODO: Implement camera calibration to convert to 3D coordinates
            # For now, return normalized coordinates (0-1)
            height, width = frame.shape[:2]
            norm_x = center_x / width
            norm_y = center_y / height
            
            # Estimate Z based on cup size (larger = closer)
            # This is a simple heuristic - should be replaced with proper depth estimation
            max_size = max(width, height)
            norm_z = 1.0 - (w * h) / (max_size * max_size)  # Closer cups appear larger
            
            positions.append((norm_x, norm_y, norm_z))
        
        return positions
    
    def draw_detections(self, frame: np.ndarray, detections: List[Tuple[int, int, int, int, float]]) -> np.ndarray:
        """
        Draw detection boxes on the frame.
        
        Args:
            frame: Input frame
            detections: List of detections
            
        Returns:
            Frame with detection boxes drawn
        """
        for x, y, w, h, confidence in detections:
            # Draw bounding box
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Draw confidence score
            label = f"Cup: {confidence:.2f}"
            cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        return frame
    
    def cleanup(self):
        """Cleanup resources"""
        # No specific cleanup needed for this implementation
        pass
    
    def __del__(self):
        """Destructor"""
        self.cleanup()