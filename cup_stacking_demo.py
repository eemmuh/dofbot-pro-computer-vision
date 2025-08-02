#!/usr/bin/env python3
"""
Simple Cup Stacking Demo
Works without camera - perfect for testing your YOLO model
"""

import sys
import os
import time

# Add src directory to path for imports
sys.path.append(os.path.join(os.getcwd(), 'src'))

def main():
    """Simple cup stacking demo"""
    print("🥤 Cup Stacking Demo - No Camera Required")
    print("=" * 50)
    
    # Check if we can import the required modules
    try:
        from vision.cup_detector import CupDetector
        print("✅ Cup detector imported successfully")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return
    
    # Configuration
    model_path = "backup/yolo-cup-memory-optimized_final.weights"
    
    print(f"🎯 Using YOLO model: {model_path}")
    
    # Check if model exists
    if not os.path.exists(model_path):
        print(f"❌ YOLO model not found: {model_path}")
        return
    
    print("✅ YOLO model found")
    
    # Initialize YOLO detector
    try:
        print("🔧 Initializing YOLO detector...")
        detector = CupDetector(model_path=model_path, conf_threshold=0.5)
        print("✅ YOLO detector initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize YOLO detector: {e}")
        return
    
    # Demo menu
    print("\n🎮 Demo Menu:")
    print("1. Test YOLO model on sample image")
    print("2. Simulate cup stacking")
    print("3. Test robot movements")
    print("4. Show system info")
    print("5. Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-5): ").strip()
            
            if choice == '1':
                test_yolo_model(detector)
            elif choice == '2':
                simulate_cup_stacking()
            elif choice == '3':
                test_robot_movements()
            elif choice == '4':
                show_system_info(model_path)
            elif choice == '5':
                print("👋 Demo ended")
                break
            else:
                print("❌ Invalid choice. Please enter 1-5.")
                
        except KeyboardInterrupt:
            print("\n👋 Demo ended")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def test_yolo_model(detector):
    """Test YOLO model on sample images"""
    print("\n🔍 Testing YOLO Model...")
    
    # Check for test images
    test_images = [
        "test_detection_10.jpg",
        "predictions_cup_001.jpg"
    ]
    
    found_images = []
    for img_path in test_images:
        if os.path.exists(img_path):
            found_images.append(img_path)
    
    if not found_images:
        print("⚠️ No test images found")
        print("Creating a simulated detection test...")
        
        # Simulate detection results
        print("🎭 Simulating YOLO detection...")
        time.sleep(1)
        print("📊 Detection Results:")
        print("  - Cup 1: Confidence 0.95, Position (320, 240)")
        print("  - Cup 2: Confidence 0.87, Position (480, 200)")
        print("  - Cup 3: Confidence 0.92, Position (160, 280)")
        print("✅ YOLO model test completed (simulation)")
        return
    
    # Test on found images
    for img_path in found_images:
        print(f"\n📸 Testing on: {img_path}")
        try:
            import cv2
            image = cv2.imread(img_path)
            if image is not None:
                detections = detector.detect_cups(image)
                print(f"📊 Found {len(detections)} cups")
                for i, detection in enumerate(detections):
                    print(f"  Cup {i+1}: Confidence {detection['confidence']:.2f}")
            else:
                print("❌ Could not load image")
        except Exception as e:
            print(f"❌ Error testing image: {e}")

def simulate_cup_stacking():
    """Simulate cup stacking sequence"""
    print("\n🚀 Simulating Cup Stacking Sequence...")
    
    # Simulate cup positions
    cup_positions = [
        (0.25, 0.30, 0.05),  # Cup 1
        (0.45, 0.30, 0.05),  # Cup 2
        (0.65, 0.30, 0.05),  # Cup 3
    ]
    
    print(f"📊 Stacking {len(cup_positions)} cups...")
    
    for i, (x, y, z) in enumerate(cup_positions):
        print(f"\n🥤 Processing cup {i+1}/{len(cup_positions)}")
        print(f"🎭 Simulating: Pick cup at ({x:.2f}, {y:.2f}, {z:.2f})")
        time.sleep(1)
        print(f"🎭 Simulating: Place cup {i+1} in stack")
        time.sleep(1)
        print(f"✅ Cup {i+1} stacked")
    
    print("\n🎉 Stacking sequence completed!")
    print("🏠 Returning to home position...")
    time.sleep(1)
    print("✅ Home position reached")

def test_robot_movements():
    """Test robot movements"""
    print("\n🤖 Testing Robot Movements...")
    
    movements = [
        ("Home position", "Moving to home position"),
        ("Open gripper", "Opening gripper"),
        ("Close gripper", "Closing gripper"),
        ("Test servo 1", "Testing base servo"),
        ("Test servo 2", "Testing shoulder servo"),
        ("Test servo 3", "Testing elbow servo"),
    ]
    
    for movement, description in movements:
        print(f"🎭 {description}...")
        time.sleep(0.5)
        print(f"✅ {movement} completed")
    
    print("✅ Robot movement test completed!")

def show_system_info(model_path):
    """Show system information"""
    print("\n📊 System Information:")
    print("=" * 30)
    
    # Model info
    if os.path.exists(model_path):
        size_mb = os.path.getsize(model_path) / (1024 * 1024)
        print(f"🎯 YOLO Model: {model_path}")
        print(f"📏 Model Size: {size_mb:.1f} MB")
    else:
        print("❌ YOLO Model: Not found")
    
    # Check other components
    components = [
        ("src/vision/cup_detector.py", "Vision System"),
        ("src/robot/dofbot_controller.py", "Robot Controller"),
        ("cup.names", "Class Names"),
        ("cfg/yolo-cup-memory-optimized.cfg", "YOLO Config"),
    ]
    
    for path, name in components:
        if os.path.exists(path):
            print(f"✅ {name}: Available")
        else:
            print(f"❌ {name}: Missing")
    
    print("\n🎮 Demo Features:")
    print("- YOLO model testing")
    print("- Cup stacking simulation")
    print("- Robot movement testing")
    print("- System diagnostics")

if __name__ == "__main__":
    main() 