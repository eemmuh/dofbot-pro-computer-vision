#!/usr/bin/env python3
"""
Check bounding box quality and tightness
"""

import os
import glob
from pathlib import Path
import cv2
import numpy as np

def analyze_box_quality():
    """Analyze the quality of bounding boxes"""
    
    images_dir = Path("dataset/images")
    labels_dir = Path("dataset/labels")
    
    # Get sample of labeled images
    label_files = glob.glob(str(labels_dir / "*.txt"))[:10]  # Check first 10
    
    print("Analyzing bounding box quality...")
    print("="*50)
    
    total_boxes = 0
    loose_boxes = 0
    
    for label_file in label_files:
        img_name = Path(label_file).stem + ".jpg"
        img_path = images_dir / img_name
        
        if not img_path.exists():
            continue
            
        # Load image
        img = cv2.imread(str(img_path))
        if img is None:
            continue
            
        height, width = img.shape[:2]
        
        # Load labels
        with open(label_file, 'r') as f:
            lines = f.readlines()
        
        print(f"\n📸 {img_name}:")
        print(f"  Image size: {width}x{height}")
        print(f"  Bounding boxes: {len(lines)}")
        
        for i, line in enumerate(lines):
            parts = line.strip().split()
            if len(parts) == 5:
                class_id, x_center, y_center, w, h = map(float, parts)
                
                # Calculate box area as percentage of image
                box_area = w * h
                image_area = 1.0  # Normalized coordinates
                box_percentage = box_area / image_area * 100
                
                # Check if box is reasonable size
                if box_percentage > 50:  # More than 50% of image
                    print(f"    ⚠️  Box {i+1}: {box_percentage:.1f}% of image (VERY LOOSE)")
                    loose_boxes += 1
                elif box_percentage > 25:  # More than 25% of image
                    print(f"    ⚠️  Box {i+1}: {box_percentage:.1f}% of image (LOOSE)")
                    loose_boxes += 1
                elif box_percentage > 10:  # More than 10% of image
                    print(f"    ✅ Box {i+1}: {box_percentage:.1f}% of image (REASONABLE)")
                else:
                    print(f"    ✅ Box {i+1}: {box_percentage:.1f}% of image (TIGHT)")
                
                total_boxes += 1
    
    print(f"\n" + "="*50)
    print("QUALITY SUMMARY:")
    print("="*50)
    print(f"Total boxes analyzed: {total_boxes}")
    print(f"Loose boxes (>25% of image): {loose_boxes}")
    print(f"Quality score: {((total_boxes - loose_boxes) / total_boxes * 100):.1f}%")
    
    if loose_boxes > total_boxes * 0.3:
        print("\n⚠️  WARNING: Many loose bounding boxes detected!")
        print("Recommendation: Consider re-labeling with tighter boxes")
    elif loose_boxes > 0:
        print("\n⚠️  Some loose bounding boxes detected")
        print("Recommendation: Use tighter boxes for future labeling")
    else:
        print("\n✅ Good quality bounding boxes!")

def show_box_examples():
    """Show examples of good vs bad bounding boxes"""
    
    print("\n" + "="*50)
    print("BOUNDING BOX GUIDELINES:")
    print("="*50)
    
    print("\n❌ TOO LOOSE (Bad):")
    print("┌─────────────────────┐")
    print("│   ┌─────┐          │")
    print("│   │ CUP │          │")
    print("│   └─────┘          │")
    print("└─────────────────────┘")
    print("- Includes lots of background")
    print("- Model learns wrong features")
    print("- Poor robot positioning")
    
    print("\n✅ TIGHT (Good):")
    print("┌─────┐")
    print("│ CUP │")
    print("└─────┘")
    print("- Minimal background")
    print("- Model learns cup features")
    print("- Accurate robot positioning")
    
    print("\n🎯 TIPS FOR BETTER LABELING:")
    print("- Zoom in when drawing boxes")
    print("- Follow the cup's edges closely")
    print("- Don't include table/surface")
    print("- Be consistent across images")
    print("- Aim for 5-15% of image area")

if __name__ == "__main__":
    analyze_box_quality()
    show_box_examples() 