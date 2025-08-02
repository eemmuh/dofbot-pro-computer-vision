#!/usr/bin/env python3
"""
Cup Stacking System Launcher
Easy-to-use script to run different components of the cup stacking system
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

def print_banner():
    """Print the system banner"""
    print("="*60)
    print("🥤 CUP STACKING SYSTEM LAUNCHER")
    print("="*60)
    print("Your trained YOLO model enables intelligent cup detection!")
    print("="*60)

def check_dependencies():
    """Check if required dependencies are available"""
    print("🔍 Checking dependencies...")
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ required")
        return False
    
    # Check required files
    required_files = [
        "backup/yolo-cup-memory-optimized_final.weights",
        "src/vision/cup_detector.py",
        "src/robot/dofbot_controller.py",
        "src/demo_cup_stacking_enhanced.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing required files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    
    print("✅ All dependencies available")
    return True

def run_yolo_test():
    """Run YOLO model testing (safe version)"""
    print("\n🧪 Testing YOLO Model (Safe Mode)...")
    
    # Test on a sample image if available
    test_images = [
        "test_detection_10.jpg",
        "dataset/valid/cup_001.jpg",
        "dataset/train/cup_001.jpg"
    ]
    
    test_image = None
    for img in test_images:
        if os.path.exists(img):
            test_image = img
            break
    
    if test_image:
        print(f"📸 Testing on image: {test_image}")
        cmd = [
            sys.executable, "test_yolo_model_safe.py",
            "--mode", "single",
            "--input", test_image
        ]
        subprocess.run(cmd)
    else:
        print("⚠️ No test images found, running safe camera test...")
        print("⚠️ This will run for 10 seconds with reduced resolution")
        cmd = [
            sys.executable, "test_yolo_model_safe.py",
            "--mode", "camera",
            "--duration", "10"
        ]
        subprocess.run(cmd)

def run_demo(mode="enhanced"):
    """Run the cup stacking demo"""
    print(f"\n🚀 Running {mode} demo...")
    
    if mode == "enhanced":
        cmd = [sys.executable, "src/demo_cup_stacking_enhanced.py"]
    elif mode == "basic":
        cmd = [sys.executable, "src/main.py"]
    else:
        print(f"❌ Unknown demo mode: {mode}")
        return
    
    subprocess.run(cmd)

def run_robot_test():
    """Test robot functionality"""
    print("\n🤖 Testing Robot...")
    cmd = [sys.executable, "src/robot/dofbot_controller.py"]
    subprocess.run(cmd)

def run_dataset_test():
    """Test on dataset (safe version)"""
    print("\n📊 Testing on Dataset (Safe Mode)...")
    
    dataset_paths = [
        "dataset/valid",
        "dataset/train",
        "dataset"
    ]
    
    dataset_path = None
    for path in dataset_paths:
        if os.path.exists(path):
            dataset_path = path
            break
    
    if dataset_path:
        print(f"📊 Testing on dataset: {dataset_path}")
        print("⚠️ Limited to 10 images for safety")
        cmd = [
            sys.executable, "test_yolo_model_safe.py",
            "--mode", "dataset",
            "--input", dataset_path,
            "--max-images", "10"
        ]
        subprocess.run(cmd)
    else:
        print("❌ No dataset found")

def show_menu():
    """Show interactive menu"""
    while True:
        print("\n" + "="*40)
        print("🎮 CUP STACKING SYSTEM MENU")
        print("="*40)
        print("1. 🧪 Test YOLO Model")
        print("2. 🚀 Run Enhanced Demo")
        print("3. 🤖 Test Robot")
        print("4. 📊 Test on Dataset")
        print("5. 📖 Show Guide")
        print("6. 🔧 System Info")
        print("0. 🚪 Exit")
        print("="*40)
        
        choice = input("Select option (0-6): ").strip()
        
        if choice == "1":
            run_yolo_test()
        elif choice == "2":
            run_demo("enhanced")
        elif choice == "3":
            run_robot_test()
        elif choice == "4":
            run_dataset_test()
        elif choice == "5":
            show_guide()
        elif choice == "6":
            show_system_info()
        elif choice == "0":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice, please try again")

def show_guide():
    """Show quick guide"""
    print("\n" + "="*50)
    print("📖 QUICK GUIDE")
    print("="*50)
    print("Your trained YOLO model provides:")
    print("• Real-time cup detection in camera feed")
    print("• High accuracy (100% confidence on clear images)")
    print("• Fast processing on Jetson Orin NX")
    print("• Position mapping for robot control")
    print()
    print("How to use:")
    print("1. Test your model first (option 1)")
    print("2. Run the enhanced demo (option 2)")
    print("3. Test robot if connected (option 3)")
    print()
    print("For detailed information, see CUP_STACKING_GUIDE.md")
    print("="*50)

def show_system_info():
    """Show system information"""
    print("\n" + "="*50)
    print("🔧 SYSTEM INFORMATION")
    print("="*50)
    
    # Model info
    model_path = "backup/yolo-cup-memory-optimized_final.weights"
    if os.path.exists(model_path):
        size = os.path.getsize(model_path) / (1024 * 1024)  # MB
        print(f"✅ YOLO Model: {model_path} ({size:.1f} MB)")
    else:
        print("❌ YOLO Model: Not found")
    
    # Dataset info
    if os.path.exists("dataset"):
        train_count = len(list(Path("dataset/train").glob("*.jpg"))) if os.path.exists("dataset/train") else 0
        valid_count = len(list(Path("dataset/valid").glob("*.jpg"))) if os.path.exists("dataset/valid") else 0
        print(f"📊 Dataset: {train_count} train, {valid_count} validation images")
    else:
        print("❌ Dataset: Not found")
    
    # Python info
    print(f"🐍 Python: {sys.version}")
    
    # Working directory
    print(f"📁 Working Directory: {os.getcwd()}")
    
    print("="*50)

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Cup Stacking System Launcher")
    parser.add_argument("--test", action="store_true", help="Run YOLO model test")
    parser.add_argument("--demo", action="store_true", help="Run enhanced demo")
    parser.add_argument("--robot", action="store_true", help="Test robot")
    parser.add_argument("--dataset", action="store_true", help="Test on dataset")
    parser.add_argument("--interactive", action="store_true", help="Run interactive menu")
    
    args = parser.parse_args()
    
    print_banner()
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Please fix missing dependencies before continuing")
        return
    
    # Handle command line arguments
    if args.test:
        run_yolo_test()
    elif args.demo:
        run_demo("enhanced")
    elif args.robot:
        run_robot_test()
    elif args.dataset:
        run_dataset_test()
    elif args.interactive or not any([args.test, args.demo, args.robot, args.dataset]):
        show_menu()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️ Interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc() 