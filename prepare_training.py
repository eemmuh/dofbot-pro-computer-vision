#!/usr/bin/env python3
"""
Prepare dataset for YOLO training after labeling is complete
"""

import os
import glob
import random
from pathlib import Path
import shutil

def create_training_structure():
    """Create proper directory structure for YOLO training"""
    
    print("Preparing dataset for YOLO training...")
    
    # Create training directories
    train_dir = Path("dataset/train")
    valid_dir = Path("dataset/valid")
    
    train_dir.mkdir(exist_ok=True)
    (train_dir / "images").mkdir(exist_ok=True)
    (train_dir / "labels").mkdir(exist_ok=True)
    
    valid_dir.mkdir(exist_ok=True)
    (valid_dir / "images").mkdir(exist_ok=True)
    (valid_dir / "labels").mkdir(exist_ok=True)
    
    # Get all labeled images
    images_dir = Path("dataset/images")
    labels_dir = Path("dataset/labels")
    
    labeled_images = []
    for label_file in glob.glob(str(labels_dir / "*.txt")):
        img_name = Path(label_file).stem + ".jpg"
        img_path = images_dir / img_name
        if img_path.exists():
            labeled_images.append(img_name)
    
    print(f"Found {len(labeled_images)} labeled images")
    
    # Shuffle for random split
    random.shuffle(labeled_images)
    
    # Split 80% train, 20% validation
    split_idx = int(len(labeled_images) * 0.8)
    train_images = labeled_images[:split_idx]
    valid_images = labeled_images[split_idx:]
    
    print(f"Training images: {len(train_images)}")
    print(f"Validation images: {len(valid_images)}")
    
    # Copy training images and labels
    for img_name in train_images:
        # Copy image
        src_img = images_dir / img_name
        dst_img = train_dir / "images" / img_name
        shutil.copy2(src_img, dst_img)
        
        # Copy label
        label_name = Path(img_name).stem + ".txt"
        src_label = labels_dir / label_name
        dst_label = train_dir / "labels" / label_name
        shutil.copy2(src_label, dst_label)
    
    # Copy validation images and labels
    for img_name in valid_images:
        # Copy image
        src_img = images_dir / img_name
        dst_img = valid_dir / "images" / img_name
        shutil.copy2(src_img, dst_img)
        
        # Copy label
        label_name = Path(img_name).stem + ".txt"
        src_label = labels_dir / label_name
        dst_label = valid_dir / "labels" / label_name
        shutil.copy2(src_label, dst_label)
    
    print("✓ Dataset split complete!")

def create_data_file():
    """Create YOLO data file"""
    
    data_content = """classes = 1
train = dataset/train/train.txt
valid = dataset/valid/valid.txt
names = cup.names
backup = backup/
"""
    
    with open("cup.data", "w") as f:
        f.write(data_content)
    
    print("✓ Created cup.data file")

def create_train_valid_lists():
    """Create train.txt and valid.txt files"""
    
    # Create train.txt
    train_images = list(Path("dataset/train/images").glob("*.jpg"))
    with open("dataset/train/train.txt", "w") as f:
        for img_path in train_images:
            f.write(str(img_path.absolute()) + "\n")
    
    # Create valid.txt
    valid_images = list(Path("dataset/valid/images").glob("*.jpg"))
    with open("dataset/valid/valid.txt", "w") as f:
        for img_path in valid_images:
            f.write(str(img_path.absolute()) + "\n")
    
    print(f"✓ Created train.txt ({len(train_images)} images)")
    print(f"✓ Created valid.txt ({len(valid_images)} images)")

def download_pretrained_weights():
    """Download pre-trained weights for transfer learning"""
    
    import urllib.request
    
    print("Downloading pre-trained weights...")
    
    # YOLO v4 weights
    weights_url = "https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v3_optimal/yolov4.weights"
    
    if not os.path.exists("yolov4.weights"):
        print("Downloading yolov4.weights (250MB)...")
        urllib.request.urlretrieve(weights_url, "yolov4.weights")
        print("✓ Downloaded yolov4.weights")
    else:
        print("✓ yolov4.weights already exists")

def main():
    """Main preparation function"""
    
    print("="*60)
    print("PREPARING DATASET FOR YOLO TRAINING")
    print("="*60)
    
    # Step 1: Create training structure
    create_training_structure()
    
    # Step 2: Create data file
    create_data_file()
    
    # Step 3: Create train/valid lists
    create_train_valid_lists()
    
    # Step 4: Download pre-trained weights
    download_pretrained_weights()
    
    print("\n" + "="*60)
    print("DATASET PREPARATION COMPLETE!")
    print("="*60)
    print("\nNext steps:")
    print("1. Install Darknet:")
    print("   git clone https://github.com/AlexeyAB/darknet.git")
    print("   cd darknet && make")
    print("\n2. Start training:")
    print("   ./darknet detector train cup.data yolo-cup.cfg yolov4.weights")
    print("\n3. Monitor training:")
    print("   - Check backup/ folder for saved weights")
    print("   - Training will save every 1000 iterations")
    print("   - Stop when loss plateaus (usually 2000-4000 iterations)")
    print("\n4. Test your model:")
    print("   ./darknet detector test cup.data yolo-cup.cfg backup/yolo-cup_final.weights")

if __name__ == "__main__":
    main() 

    