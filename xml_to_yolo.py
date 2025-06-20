#!/usr/bin/env python3
"""
Convert XML (Pascal VOC) format to YOLO format
"""

import xml.etree.ElementTree as ET
import os
import glob
from pathlib import Path
import cv2

def convert_xml_to_yolo():
    """Convert XML files to YOLO format"""
    
    images_dir = Path("dataset/images")
    labels_dir = Path("dataset/labels")
    
    # Get all XML files
    xml_files = glob.glob(str(labels_dir / "*.xml"))
    
    if not xml_files:
        print("No XML files found in dataset/labels/")
        return
    
    print(f"Found {len(xml_files)} XML files to convert")
    
    converted_count = 0
    
    for xml_file in xml_files:
        try:
            # Parse XML file
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            # Get image filename
            filename_elem = root.find('filename')
            if filename_elem is None or filename_elem.text is None:
                print(f"Warning: No filename found in {xml_file}, skipping")
                continue
            filename = filename_elem.text
            
            # Get image dimensions
            size = root.find('size')
            if size is None:
                print(f"Warning: No size information in {xml_file}, skipping")
                continue
                
            width_elem = size.find('width')
            height_elem = size.find('height')
            if width_elem is None or height_elem is None or width_elem.text is None or height_elem.text is None:
                print(f"Warning: Invalid size information in {xml_file}, skipping")
                continue
                
            width = int(width_elem.text)
            height = int(height_elem.text)
            
            # Create YOLO format filename
            base_name = Path(xml_file).stem
            yolo_file = labels_dir / f"{base_name}.txt"
            
            # Convert annotations to YOLO format
            yolo_lines = []
            for obj in root.findall('object'):
                name_elem = obj.find('name')
                bndbox = obj.find('bndbox')
                
                if name_elem is None or bndbox is None:
                    continue
                    
                name = name_elem.text
                if name is None:
                    continue
                
                # Get bounding box coordinates
                xmin_elem = bndbox.find('xmin')
                ymin_elem = bndbox.find('ymin')
                xmax_elem = bndbox.find('xmax')
                ymax_elem = bndbox.find('ymax')
                
                if (xmin_elem is None or ymin_elem is None or 
                    xmax_elem is None or ymax_elem is None or
                    xmin_elem.text is None or ymin_elem.text is None or
                    xmax_elem.text is None or ymax_elem.text is None):
                    continue
                
                xmin = float(xmin_elem.text)
                ymin = float(ymin_elem.text)
                xmax = float(xmax_elem.text)
                ymax = float(ymax_elem.text)
                
                # Convert to YOLO format (normalized coordinates)
                x_center = (xmin + xmax) / 2 / width
                y_center = (ymin + ymax) / 2 / height
                box_width = (xmax - xmin) / width
                box_height = (ymax - ymin) / height
                
                # Class ID for "cup" is 0
                class_id = 0
                
                # YOLO format: class_id x_center y_center width height
                yolo_line = f"{class_id} {x_center:.6f} {y_center:.6f} {box_width:.6f} {box_height:.6f}"
                yolo_lines.append(yolo_line)
            
            # Write YOLO format file
            with open(yolo_file, 'w') as f:
                f.write('\n'.join(yolo_lines))
            
            # Remove original XML file
            os.remove(xml_file)
            
            converted_count += 1
            print(f"✓ Converted {xml_file} -> {yolo_file}")
            print(f"  Found {len(yolo_lines)} bounding boxes")
            
        except Exception as e:
            print(f"Error converting {xml_file}: {e}")
    
    print(f"\nConversion complete! Converted {converted_count} files to YOLO format")

if __name__ == "__main__":
    convert_xml_to_yolo() 