import cv2
import numpy as np
import subprocess
import tempfile
import os
from typing import List, Tuple, Optional

class CupDetector:
    def __init__(self, model_path: str, conf_threshold: float = 0.5, nms_threshold: float = 0.4):
        """
        Initialize the cup detector with YOLO model using Darknet.
        
        Args:
            model_path: Path to the YOLO model weights
            conf_threshold: Confidence threshold for detections
            nms_threshold: Non-maximum suppression threshold
        """
        self.conf_threshold = conf_threshold
        self.nms_threshold = nms_threshold
        self.model_path = model_path
        self.class_names = ['cup']
        
        # Verify model files exist
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model weights not found: {model_path}")
        
        # Get the directory containing the model for config file
        model_dir = os.path.dirname(model_path)
        config_path = os.path.join(model_dir, "yolo-cup-memory-optimized.cfg")
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        self.config_path = config_path
        self.names_path = os.path.join(model_dir, "cup.names")
        self.data_path = os.path.join(model_dir, "cup.data")
    
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
            # Run Darknet detection
            cmd = [
                "./darknet", "detect", self.config_path, self.model_path, temp_image_path,
                "-thresh", str(self.conf_threshold)
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
        for line in lines:
            if 'cup:' in line.lower() and '%' in line:
                # Parse line like "cup: 76%"
                parts = line.split(':')
                if len(parts) >= 2:
                    confidence_str = parts[1].strip().replace('%', '')
                    try:
                        confidence = float(confidence_str) / 100.0
                        
                        # Look for bounding box coordinates in previous lines
                        # Darknet typically outputs coordinates before the class label
                        for i, prev_line in enumerate(lines[:lines.index(line)]):
                            if prev_line.strip() and all(c.isdigit() or c in '.-' for c in prev_line.strip()):
                                coords = prev_line.strip().split()
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