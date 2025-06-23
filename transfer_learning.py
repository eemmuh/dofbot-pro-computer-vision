#!/usr/bin/env python3
"""
Transfer learning approach for cup detection
Use pre-trained model + small amount of labeled data
"""

import os
import glob
from pathlib import Path
import random

def create_small_dataset():
    """Create a smaller dataset for transfer learning"""
    
    images_dir = Path("dataset/images")
    labels_dir = Path("dataset/labels")
    
    # Get all labeled images
    labeled_images = []
    for label_file in glob.glob(str(labels_dir / "*.txt")):
        img_name = Path(label_file).stem + ".jpg"
        img_path = images_dir / img_name
        if img_path.exists():
            labeled_images.append(img_name)
    
    print(f"Found {len(labeled_images)} labeled images")
    
    # Select subset for transfer learning (e.g., 20-30 images)
    subset_size = min(30, len(labeled_images))
    selected_images = random.sample(labeled_images, subset_size)
    
    # Create transfer learning dataset
    transfer_dir = Path("dataset/transfer_learning")
    transfer_dir.mkdir(exist_ok=True)
    (transfer_dir / "images").mkdir(exist_ok=True)
    (transfer_dir / "labels").mkdir(exist_ok=True)
    
    # Copy selected images and labels
    for img_name in selected_images:
        # Copy image
        src_img = images_dir / img_name
        dst_img = transfer_dir / "images" / img_name
        if src_img.exists():
            import shutil
            shutil.copy2(src_img, dst_img)
        
        # Copy label
        label_name = Path(img_name).stem + ".txt"
        src_label = labels_dir / label_name
        dst_label = transfer_dir / "labels" / label_name
        if src_label.exists():
            shutil.copy2(src_label, dst_label)
    
    print(f"✓ Created transfer learning dataset with {len(selected_images)} images")
    return selected_images

def create_transfer_learning_config():
    """Create YOLO config for transfer learning"""
    
    config_content = """[net]
batch=16
subdivisions=8
width=416
height=416
channels=3
momentum=0.9
decay=0.0005
angle=0
saturation = 1.5
exposure = 1.5
hue=.1

learning_rate=0.0001
burn_in=100
max_batches=2000
policy=steps
steps=1600,1800
scales=.1,.1

[convolutional]
batch_normalize=1
filters=32
size=3
stride=1
pad=1
activation=leaky

[yolo]
mask = 0,1,2
anchors = 10,13,  16,30,  33,23,  30,61,  62,45,  59,119,  116,90,  156,198,  373,326
classes=1
num=9
jitter=.3
ignore_thresh = .7
truth_thresh = 1
random=1
"""
    
    with open("yolo-cup-transfer.cfg", "w") as f:
        f.write(config_content)
    
    print("✓ Created transfer learning config: yolo-cup-transfer.cfg")

def create_data_file():
    """Create data file for transfer learning"""
    
    data_content = """classes = 1
train = dataset/transfer_learning/train.txt
valid = dataset/transfer_learning/valid.txt
names = cup.names
backup = backup/
"""
    
    with open("cup-transfer.data", "w") as f:
        f.write(data_content)
    
    print("✓ Created data file: cup-transfer.data")

def split_train_valid():
    """Split transfer learning dataset into train/valid"""
    
    transfer_dir = Path("dataset/transfer_learning")
    images_dir = transfer_dir / "images"
    
    # Get all images
    images = list(images_dir.glob("*.jpg"))
    random.shuffle(images)
    
    # Split 80% train, 20% validation
    split_idx = int(len(images) * 0.8)
    train_images = images[:split_idx]
    valid_images = images[split_idx:]
    
    # Create train.txt
    with open("dataset/transfer_learning/train.txt", "w") as f:
        for img_path in train_images:
            f.write(str(img_path.absolute()) + "\n")
    
    # Create valid.txt
    with open("dataset/transfer_learning/valid.txt", "w") as f:
        for img_path in valid_images:
            f.write(str(img_path.absolute()) + "\n")
    
    print(f"✓ Split dataset: {len(train_images)} train, {len(valid_images)} validation")

def main():
    """Main transfer learning setup"""
    
    print("Setting up transfer learning for cup detection...")
    print("This approach uses pre-trained weights + small labeled dataset")
    
    # Create small dataset
    selected_images = create_small_dataset()
    
    # Create config files
    create_transfer_learning_config()
    create_data_file()
    
    # Split into train/valid
    split_train_valid()
    
    print("\n" + "="*50)
    print("TRANSFER LEARNING SETUP COMPLETE!")
    print("="*50)
    print("\nNext steps:")
    print("1. Download pre-trained weights:")
    print("   wget https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v3_optimal/yolov4.weights")
    print("\n2. Train with transfer learning:")
    print("   ./darknet detector train cup-transfer.data yolo-cup-transfer.cfg yolov4.weights")
    print("\n3. This will train much faster with fewer images!")
    print("\nBenefits:")
    print("- Only need 20-30 labeled images instead of 224")
    print("- Faster training (fewer epochs needed)")
    print("- Better performance than training from scratch")
    print("- Can improve with more data later")

if __name__ == "__main__":
    main() 