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
        # Look for config file in cfg directory
        config_path = os.path.join(os.path.dirname(model_dir), "cfg", "yolo-cup-memory-optimized.cfg")
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        self.config_path = config_path
        # Look for names and data files in the root directory
        root_dir = os.path.dirname(os.path.dirname(model_dir))
        self.names_path = os.path.join(root_dir, "cup.names")
        self.data_path = os.path.join(root_dir, "data", "cup.data")
        
        # Handle darknet names file issue - temporarily replace coco.names with our cup.names
        darknet_data_dir = os.path.join(root_dir, "darknet", "data")
        coco_names_path = os.path.join(darknet_data_dir, "coco.names")
        cup_names_path = os.path.join(darknet_data_dir, "cup.names")
        
        # Backup original coco.names if it exists and we haven't already
        if os.path.exists(coco_names_path) and not os.path.exists(coco_names_path + ".backup"):
            import shutil
            shutil.copy2(coco_names_path, coco_names_path + ".backup")
        
        # Copy our cup.names to replace coco.names temporarily
        if os.path.exists(coco_names_path):
            import shutil
            shutil.copy2(self.names_path, coco_names_path)
            print("✅ Temporarily replaced coco.names with cup.names for detection")
    
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
            # Use absolute paths for model and config files since darknet runs from its own directory
            abs_model_path = os.path.abspath(self.model_path)
            abs_config_path = os.path.abspath(self.config_path)
            
            cmd = [
                "./darknet", "detect", abs_config_path, abs_model_path, temp_image_path,
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
        
        # Look for any detection line (more flexible)
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Check if this line contains a detection (any class with percentage)
            if ':' in line and '%' in line:
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
                                        
                                        # Accept any detection (not just 'cup')
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
        """Restore original coco.names file if it was backed up"""
        try:
            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            darknet_data_dir = os.path.join(root_dir, "darknet", "data")
            coco_names_path = os.path.join(darknet_data_dir, "coco.names")
            coco_backup_path = coco_names_path + ".backup"
            
            if os.path.exists(coco_backup_path):
                import shutil
                shutil.copy2(coco_backup_path, coco_names_path)
                print("✅ Restored original coco.names file")
        except Exception as e:
            print(f"⚠️ Warning: Could not restore coco.names: {e}")
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        self.cleanup()