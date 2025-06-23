#!/usr/bin/env python3
"""
AI-powered auto-labeling for cup detection
"""

import os
import glob
from pathlib import Path
import cv2
import numpy as np

def show_auto_labeling_options():
    """Show different auto-labeling options"""
    
    print("="*60)
    print("AI AUTO-LABELING OPTIONS FOR CUPS")
    print("="*60)
    
    print("\n1. 🚀 ROBOFLOW (Easiest & Free)")
    print("   - Upload images to roboflow.com")
    print("   - AI automatically detects cups")
    print("   - Export in YOLO format")
    print("   - Free tier: 1,000 images")
    print("   - Steps:")
    print("     a) Go to roboflow.com")
    print("     b) Create account")
    print("     c) Upload your 224 images")
    print("     d) Use 'Auto-Label' feature")
    print("     e) Download YOLO format labels")
    
    print("\n2. 🤖 LABELME AI ASSISTANCE")
    print("   - Use LabelMe with AI features")
    print("   - AI suggests bounding boxes")
    print("   - You verify and correct")
    print("   - Much faster than manual")
    print("   - Command: labelme --autolabel dataset/images")
    
    print("\n3. 🌐 GOOGLE VISION API")
    print("   - Professional AI detection")
    print("   - Very accurate for cups")
    print("   - Requires API key")
    print("   - May cost money")
    print("   - Best quality results")
    
    print("\n4. 🔧 OPENCV TEMPLATE MATCHING")
    print("   - Use your existing labeled images")
    print("   - Find similar cups in new images")
    print("   - Free and local")
    print("   - Less accurate than AI")
    
    print("\n5. 📦 ULTRALYTICS YOLO")
    print("   - Use pre-trained YOLO model")
    print("   - Detect cups automatically")
    print("   - Convert to your format")
    print("   - Good starting point")

def setup_roboflow_workflow():
    """Guide for using Roboflow auto-labeling"""
    
    print("\n" + "="*60)
    print("ROBOFLOW AUTO-LABELING WORKFLOW")
    print("="*60)
    
    print("\nStep 1: Prepare Images")
    print("- Your images are already ready (cup_001.jpg to cup_224.jpg)")
    print("- Make sure they're in dataset/images/")
    
    print("\nStep 2: Upload to Roboflow")
    print("1. Go to roboflow.com")
    print("2. Create free account")
    print("3. Create new project")
    print("4. Upload your 224 images")
    
    print("\nStep 3: Auto-Label")
    print("1. Go to 'Auto-Label' tab")
    print("2. Select 'Object Detection'")
    print("3. Choose 'COCO' model (includes cups)")
    print("4. Run auto-labeling")
    print("5. Review and correct if needed")
    
    print("\nStep 4: Export")
    print("1. Go to 'Export' tab")
    print("2. Choose 'YOLO' format")
    print("3. Download labels")
    print("4. Place .txt files in dataset/labels/")
    
    print("\nEstimated time: 30-60 minutes")
    print("Accuracy: 80-90% (very good for cups)")

def setup_labelme_ai():
    """Setup LabelMe with AI assistance"""
    
    print("\n" + "="*60)
    print("LABELME AI ASSISTANCE SETUP")
    print("="*60)
    
    print("\nStep 1: Install LabelMe with AI")
    print("pip install labelme[ai]")
    
    print("\nStep 2: Run with AI assistance")
    print("labelme --autolabel dataset/images --output dataset/labels")
    
    print("\nStep 3: Review and correct")
    print("- AI will suggest bounding boxes")
    print("- You verify and adjust if needed")
    print("- Much faster than manual labeling")
    
    print("\nBenefits:")
    print("- AI suggests boxes automatically")
    print("- You just need to verify/correct")
    print("- 5-10x faster than manual labeling")
    print("- Uses your existing LabelMe setup")

def create_template_matching():
    """Create template matching for similar cups"""
    
    print("\n" + "="*60)
    print("TEMPLATE MATCHING APPROACH")
    print("="*60)
    
    print("\nThis approach:")
    print("1. Uses your 66 labeled images as templates")
    print("2. Finds similar cups in unlabeled images")
    print("3. Creates bounding boxes automatically")
    print("4. You review and correct")
    
    print("\nPros:")
    print("- Free and local")
    print("- Uses your existing labels")
    print("- No external services needed")
    
    print("\nCons:")
    print("- Less accurate than AI")
    print("- Works best with similar cups")
    print("- May miss cups that look different")

def main():
    """Main function"""
    
    show_auto_labeling_options()
    
    print("\n" + "="*60)
    print("RECOMMENDED APPROACH")
    print("="*60)
    
    print("\nFor your 224 cup images, I recommend:")
    print("\n1. 🥇 TRY ROBOFLOW FIRST")
    print("   - Free and very accurate")
    print("   - Can handle all 224 images")
    print("   - Professional AI detection")
    print("   - Export directly to YOLO format")
    
    print("\n2. 🥈 FALLBACK: LABELME AI")
    print("   - If Roboflow doesn't work")
    print("   - Uses AI assistance")
    print("   - Much faster than manual")
    
    print("\n3. 🥉 LAST RESORT: Continue Manual")
    print("   - If AI methods don't work well")
    print("   - Your current approach is fine")
    print("   - 66 images already done")
    
    print("\nWould you like me to:")
    print("A) Guide you through Roboflow setup")
    print("B) Set up LabelMe with AI assistance")
    print("C) Create template matching script")
    print("D) Continue with manual labeling")

if __name__ == "__main__":
    main() 