#!/usr/bin/env python3
"""
Convert LabelMe JSON files to YOLO format
"""

import json
import os
import glob
from pathlib import Path
import cv2

def convert_labelme_to_yolo():
    """Convert LabelMe JSON files to YOLO format"""
    
    images_dir = Path("dataset/images")
    labels_dir = Path("dataset/labels")
    
    # Get all JSON files
    json_files = glob.glob(str(labels_dir / "*.json"))
    
    if not json_files:
        print("No JSON files found. Make sure you've labeled some images with LabelMe first.")
        return
    
    print(f"Found {len(json_files)} JSON files to convert")
    
    converted_count = 0
    
    for json_file in json_files:
        try:
            # Read JSON file
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            # Get image filename
            image_name = data["imagePath"]
            image_path = images_dir / image_name
            
            # Read image to get dimensions
            if image_path.exists():
                img = cv2.imread(str(image_path))
                img_height, img_width = img.shape[:2]
            else:
                print(f"Warning: Image {image_name} not found, skipping {json_file}")
                continue
            
            # Create YOLO format filename
            base_name = Path(json_file).stem
            yolo_file = labels_dir / f"{base_name}.txt"
            
            # Convert annotations to YOLO format
            yolo_lines = []
            for shape in data["shapes"]:
                label = shape["label"]
                points = shape["points"]
                
                # Get bounding box from points
                x_coords = [p[0] for p in points]
                y_coords = [p[1] for p in points]
                
                x_min, x_max = min(x_coords), max(x_coords)
                y_min, y_max = min(y_coords), max(y_coords)
                
                # Convert to YOLO format (normalized coordinates)
                x_center = (x_min + x_max) / 2 / img_width
                y_center = (y_min + y_max) / 2 / img_height
                width = (x_max - x_min) / img_width
                height = (y_max - y_min) / img_height
                
                # Class ID for "cup" is 0
                class_id = 0
                
                # YOLO format: class_id x_center y_center width height
                yolo_line = f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}"
                yolo_lines.append(yolo_line)
            
            # Write YOLO format file
            with open(yolo_file, 'w') as f:
                f.write('\n'.join(yolo_lines))
            
            converted_count += 1
            print(f"✓ Converted {json_file} -> {yolo_file}")
            
        except Exception as e:
            print(f"Error converting {json_file}: {e}")
    
    print(f"\nConversion complete! Converted {converted_count} files to YOLO format")
    print("You can now delete the JSON files if you want to keep only YOLO format.")

if __name__ == "__main__":
    convert_labelme_to_yolo() 