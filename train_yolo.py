#!/usr/bin/env python3
"""
YOLOv4 Training Script for Cup Detection
This script handles the complete training pipeline for the DOFBOT cup stacking project.
"""

import os
import subprocess
import time
import shutil
from pathlib import Path

def check_darknet_installation():
    """Check if Darknet is installed and accessible."""
    try:
        result = subprocess.run(['./darknet', 'detector', 'test'], 
                              capture_output=True, text=True)
        return True
    except FileNotFoundError:
        return False

def install_darknet():
    """Install Darknet for YOLO training."""
    print("Installing Darknet...")
    
    # Clone Darknet repository
    if not os.path.exists('darknet'):
        subprocess.run(['git', 'clone', 'https://github.com/AlexeyAB/darknet.git'])
    
    # Change to darknet directory
    os.chdir('darknet')
    
    # Compile Darknet
    print("Compiling Darknet...")
    subprocess.run(['make'])
    
    # Return to project root
    os.chdir('..')
    
    print("Darknet installation complete!")

def create_training_config():
    """Create the training configuration files."""
    print("Creating training configuration...")
    
    # Create cup.data file
    cup_data_content = """classes = 1
train = dataset/train.txt
valid = dataset/valid.txt
names = cup.names
backup = backup/
"""
    
    with open('cup.data', 'w') as f:
        f.write(cup_data_content)
    
    # Create train.txt and valid.txt
    train_images = []
    valid_images = []
    
    # Get training images
    train_dir = Path('dataset/train')
    for img_file in train_dir.glob('*.jpg'):
        train_images.append(str(img_file.absolute()))
    
    # Get validation images
    valid_dir = Path('dataset/valid')
    for img_file in valid_dir.glob('*.jpg'):
        valid_images.append(str(img_file.absolute()))
    
    # Write train.txt
    with open('dataset/train.txt', 'w') as f:
        for img_path in train_images:
            f.write(f"{img_path}\n")
    
    # Write valid.txt
    with open('dataset/valid.txt', 'w') as f:
        for img_path in valid_images:
            f.write(f"{img_path}\n")
    
    print(f"Training configuration created:")
    print(f"  - Training images: {len(train_images)}")
    print(f"  - Validation images: {len(valid_images)}")

def download_pretrained_weights():
    """Download pre-trained YOLOv4 weights if not present."""
    weights_path = 'yolov4.weights'
    
    if not os.path.exists(weights_path):
        print("Downloading pre-trained YOLOv4 weights...")
        print("This may take a few minutes (250MB download)...")
        
        # Download weights
        subprocess.run(['wget', 'https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v3_optimal/yolov4.weights'])
        
        if os.path.exists(weights_path):
            print("Pre-trained weights downloaded successfully!")
        else:
            print("Failed to download weights. Please download manually from:")
            print("https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v3_optimal/yolov4.weights")
    else:
        print("Pre-trained weights already present.")

def start_training():
    """Start the YOLO training process."""
    print("\n" + "="*50)
    print("STARTING YOLOv4 TRAINING")
    print("="*50)
    
    # Check if we're in the right directory
    if not os.path.exists('darknet'):
        print("Error: Darknet not found. Please run install_darknet() first.")
        return
    
    # Create backup directory
    os.makedirs('backup', exist_ok=True)
    
    # Start training
    print("Starting training with transfer learning...")
    print("Training will continue until you stop it (Ctrl+C)")
    print("Monitor the loss values - they should decrease over time")
    print("Weights will be saved every 1000 iterations in backup/ folder")
    
    try:
        # Run training command
        cmd = ['./darknet/darknet', 'detector', 'train', 'cup.data', 'yolo-cup.cfg', 'yolov4.weights']
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\nTraining stopped by user.")
        print("Check the backup/ folder for your trained weights.")

def test_model(weights_path):
    """Test the trained model on validation images."""
    print(f"\nTesting model: {weights_path}")
    
    if not os.path.exists(weights_path):
        print(f"Error: Weights file not found: {weights_path}")
        return
    
    # Test on validation images
    cmd = ['./darknet/darknet', 'detector', 'test', 'cup.data', 'yolo-cup.cfg', weights_path]
    subprocess.run(cmd)

def main():
    """Main training pipeline."""
    print("YOLOv4 Training Pipeline for Cup Detection")
    print("="*50)
    
    # Check and install Darknet
    if not check_darknet_installation():
        print("Darknet not found. Installing...")
        install_darknet()
    else:
        print("Darknet already installed.")
    
    # Create training configuration
    create_training_config()
    
    # Download pre-trained weights
    download_pretrained_weights()
    
    # Ask user what to do
    print("\nWhat would you like to do?")
    print("1. Start training")
    print("2. Test existing model")
    print("3. Exit")
    
    choice = input("Enter your choice (1-3): ").strip()
    
    if choice == '1':
        start_training()
    elif choice == '2':
        weights_path = input("Enter path to weights file (e.g., backup/yolo-cup_final.weights): ").strip()
        test_model(weights_path)
    elif choice == '3':
        print("Exiting...")
    else:
        print("Invalid choice. Exiting...")

if __name__ == "__main__":
    main() 