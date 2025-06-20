#!/usr/bin/env python3
"""
Script to validate YOLO labels and show statistics
"""

import os
import glob
from pathlib import Path
import cv2
import numpy as np

def validate_labels():
    images_dir = Path("dataset/images")
    labels_dir = Path("dataset/labels")
    
    # Get all image files
    image_files = sorted(glob.glob(str(images_dir / "*.jpg")))
    label_files = sorted(glob.glob(str(labels_dir / "*.txt")))
    
    print(f"Found {len(image_files)} images")
    print(f"Found {len(label_files)} label files")
    
    # Check for missing labels
    labeled_images = set()
    for label_file in label_files:
        img_name = Path(label_file).stem + ".jpg"
        labeled_images.add(img_name)
    
    missing_labels = []
    for img_file in image_files:
        img_name = Path(img_file).name
        if img_name not in labeled_images:
            missing_labels.append(img_name)
    
    if missing_labels:
        print(f"\n⚠️  {len(missing_labels)} images missing labels:")
        for img in missing_labels[:10]:  # Show first 10
            print(f"  - {img}")
        if len(missing_labels) > 10:
            print(f"  ... and {len(missing_labels) - 10} more")
    else:
        print("\n✓ All images have corresponding label files!")
    
    # Analyze label statistics
    total_boxes = 0
    for label_file in label_files:
        with open(label_file, 'r') as f:
            lines = f.readlines()
            total_boxes += len(lines)
    
    print(f"\n📊 Label Statistics:")
    print(f"  Total bounding boxes: {total_boxes}")
    print(f"  Average boxes per image: {total_boxes/len(label_files):.1f}")
    
    # Show sample of label format
    if label_files:
        print(f"\n📝 Sample label format (first label file):")
        with open(label_files[0], 'r') as f:
            content = f.read().strip()
            if content:
                print(f"  {Path(label_files[0]).name}: {content}")
            else:
                print(f"  {Path(label_files[0]).name}: (empty file)")

def visualize_sample_labels(num_samples=3):
    """Visualize a few sample labels to verify they're correct"""
    images_dir = Path("dataset/images")
    labels_dir = Path("dataset/labels")
    
    # Get sample files
    image_files = sorted(glob.glob(str(images_dir / "*.jpg")))[:num_samples]
    
    for img_file in image_files:
        img_name = Path(img_file).stem
        label_file = labels_dir / f"{img_name}.txt"
        
        if label_file.exists():
            # Load image
            img = cv2.imread(img_file)
            height, width = img.shape[:2]
            
            # Load labels
            with open(label_file, 'r') as f:
                lines = f.readlines()
            
            print(f"\n🔍 {img_name}.jpg:")
            print(f"  Image size: {width}x{height}")
            print(f"  Bounding boxes: {len(lines)}")
            
            for i, line in enumerate(lines):
                parts = line.strip().split()
                if len(parts) == 5:
                    class_id, x_center, y_center, w, h = map(float, parts)
                    print(f"    Box {i+1}: class={int(class_id)}, center=({x_center:.3f}, {y_center:.3f}), size=({w:.3f}, {h:.3f})")

if __name__ == "__main__":
    print("Validating YOLO labels...")
    validate_labels()
    print("\n" + "="*50)
    visualize_sample_labels() 