#!/usr/bin/env python3
"""
Real-time Cup Stacking Launcher
Choose between basic and calibrated real-time stacking
"""

import os
import sys
import subprocess

def check_requirements():
    """Check if required files exist"""
    required_files = [
        'src/vision/cup_detector.py',
        'src/robot/dofbot_controller.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    return True

def show_menu():
    """Show the main menu"""
    print("🥤 Real-time Cup Stacking Launcher")
    print("=" * 50)
    print()
    print("Choose your real-time stacking mode:")
    print()
    print("1. 🎯 Basic Real-time Stacking")
    print("   - Uses camera detection to find cups")
    print("   - Converts pixel coordinates to robot angles")
    print("   - Good for testing and demonstration")
    print()
    print("2. 🎯 Calibrated Real-time Stacking")
    print("   - Uses your calibrated cup positions")
    print("   - More accurate and reliable")
    print("   - Includes manual fine-tuning mode")
    print()
    print("3. 🔧 Calibrate Cup Positions")
    print("   - Run the calibration script first")
    print("   - Set up precise cup positions")
    print()
    print("4. 📋 System Status")
    print("   - Check if all components are ready")
    print()
    print("5. ❌ Exit")
    print()

def check_system_status():
    """Check system status"""
    print("🔍 Checking System Status...")
    print("=" * 40)
    
    # Check Python environment
    print("🐍 Python Environment:")
    print(f"   Python version: {sys.version}")
    print(f"   Virtual environment: {'venv' in sys.prefix}")
    
    # Check required files
    print("\n📁 Required Files:")
    files_to_check = [
        ('src/vision/cup_detector.py', 'Cup Detector'),
        ('src/robot/dofbot_controller.py', 'Robot Controller'),
        ('cup.names', 'YOLO Class Names'),
        ('data/cup.data', 'YOLO Data Config'),
        ('cfg/yolo-cup.cfg', 'YOLO Config'),
        ('backup/yolo-cup-memory-optimized_final.weights', 'YOLO Weights')
    ]
    
    all_good = True
    for file_path, description in files_to_check:
        if os.path.exists(file_path):
            print(f"   ✅ {description}: {file_path}")
        else:
            print(f"   ❌ {description}: {file_path} (MISSING)")
            all_good = False
    
    # Check calibrated positions
    print("\n🎯 Calibrated Positions:")
    if os.path.exists('calibrated_cup_positions.py'):
        print("   ✅ Calibrated positions file found")
        try:
            from calibrated_cup_positions import CUP_POSITIONS, STACK_POSITION
            print(f"   📊 {len(CUP_POSITIONS)} cup positions defined")
            print(f"   🏗️ Stack position: {STACK_POSITION}")
        except ImportError as e:
            print(f"   ❌ Error loading calibrated positions: {e}")
    else:
        print("   ⚠️ No calibrated positions file found")
        print("   💡 Run calibration first for best results")
    
    # Check camera
    print("\n📷 Camera:")
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("   ✅ Camera is available")
            cap.release()
        else:
            print("   ❌ Camera not available")
            all_good = False
    except Exception as e:
        print(f"   ❌ Camera error: {e}")
        all_good = False
    
    # Check robot
    print("\n🤖 Robot:")
    try:
        import smbus2 as smbus
        sys.modules['smbus'] = smbus
        from Arm_Lib import Arm_Device
        print("   ✅ Arm_Lib available")
    except Exception as e:
        print(f"   ❌ Robot library error: {e}")
        all_good = False
    
    print("\n" + "=" * 40)
    if all_good:
        print("✅ System is ready for real-time stacking!")
    else:
        print("⚠️ Some components need attention")
        print("💡 Fix missing components before running")
    
    return all_good

def run_script(script_name):
    """Run a Python script"""
    if not os.path.exists(script_name):
        print(f"❌ Script not found: {script_name}")
        return False
    
    print(f"🚀 Running {script_name}...")
    print("=" * 50)
    
    try:
        # Run the script
        result = subprocess.run([sys.executable, script_name], 
                              cwd=os.getcwd())
        
        if result.returncode == 0:
            print("✅ Script completed successfully")
        else:
            print(f"❌ Script exited with code {result.returncode}")
        
        return result.returncode == 0
        
    except KeyboardInterrupt:
        print("\n⏹️ Script interrupted by user")
        return False
    except Exception as e:
        print(f"❌ Error running script: {e}")
        return False

def main():
    """Main function"""
    while True:
        show_menu()
        
        try:
            choice = input("Enter your choice (1-5): ").strip()
            
            if choice == '1':
                print("\n🎯 Starting Basic Real-time Stacking...")
                if check_requirements():
                    run_script('realtime_cup_stacking.py')
                else:
                    print("❌ Requirements not met. Please check system status.")
                
            elif choice == '2':
                print("\n🎯 Starting Calibrated Real-time Stacking...")
                if check_requirements():
                    run_script('realtime_cup_stacking_calibrated.py')
                else:
                    print("❌ Requirements not met. Please check system status.")
                
            elif choice == '3':
                print("\n🔧 Starting Cup Position Calibration...")
                if os.path.exists('calibrate_cup_positions.py'):
                    run_script('calibrate_cup_positions.py')
                else:
                    print("❌ Calibration script not found")
                    print("💡 Please ensure calibrate_cup_positions.py exists")
                
            elif choice == '4':
                print()
                check_system_status()
                
            elif choice == '5':
                print("👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid choice. Please enter 1-5.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
        
        if choice in ['1', '2', '3']:
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    main() 