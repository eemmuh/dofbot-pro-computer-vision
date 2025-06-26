import cv2
import numpy as np
import torch
from typing import List, Tuple, Optional
import os

class CupDetector:
    def __init__(self, model_path: str, conf_threshold: float = 0.5, nms_threshold: float = 0.4):
        """
        Initialize the cup detector with YOLO model.
        
        Args:
            model_path: Path to the YOLO model weights
            conf_threshold: Confidence threshold for detections
            nms_threshold: Non-maximum suppression threshold
        """
        self.conf_threshold = conf_threshold
        self.nms_threshold = nms_threshold
        self.model = self._load_model(model_path)
        self.class_names = ['cup']
        
    def _load_model(self, model_path: str):
        """Load the YOLO model using OpenCV DNN."""
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model weights not found: {model_path}")
            
        # Load YOLO model using OpenCV DNN
        net = cv2.dnn.readNetFromDarknet("yolo-cup.cfg", model_path)
        
        # Use GPU if available
        net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
        net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
        
        return net
    
    def detect_cups(self, frame: np.ndarray) -> List[Tuple[int, int, int, int, float]]:
        """
        Detect cups in the given frame.
        
        Args:
            frame: Input image frame
            
        Returns:
            List of detections in format (x, y, w, h, confidence)
        """
        height, width = frame.shape[:2]
        
        # Create blob from image
        blob = cv2.dnn.blobFromImage(frame, 1/255.0, (416, 416), swapRB=True, crop=False)
        self.model.setInput(blob)
        
        # Get detections
        layer_names = self.model.getLayerNames()
        output_layers = [layer_names[i - 1] for i in self.model.getUnconnectedOutLayers()]
        outputs = self.model.forward(output_layers)
        
        # Process detections
        boxes = []
        confidences = []
        
        for output in outputs:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                
                if confidence > self.conf_threshold:
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)
                    
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)
                    
                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
        
        # Apply non-maximum suppression
        indices = cv2.dnn.NMSBoxes(boxes, confidences, self.conf_threshold, self.nms_threshold)
        
        detections = []
        if len(indices) > 0:
            # Convert to numpy array and flatten if needed
            indices = np.array(indices).flatten()
            for i in indices:
                x, y, w, h = boxes[i]
                confidence = confidences[i]
                detections.append((x, y, w, h, confidence))
        
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