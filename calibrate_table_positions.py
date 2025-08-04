#!/usr/bin/env python3
"""
Table Cup Position Calibration
Help find the correct servo angles for picking up cups from the table
and stacking them in pyramid order
"""

import sys
import os
import time

# Add src directory to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

# Fix smbus import issue
try:
    import smbus2 as smbus
    sys.modules['smbus'] = smbus
    print("✅ smbus compatibility fixed")
except ImportError:
    print("❌ smbus2 not available")
    sys.exit(1)

# Import our modules
try:
    from Arm_Lib import Arm_Device
    print("✅ Arm_Lib imported successfully")
except Exception as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

class TableCupCalibrator:
    def __init__(self):
        self.robot = None
        self.calibrated_positions = []
        
        # Table stacking positions (pyramid order)
        self.pyramid_positions = [
            "Bottom Left",      # Position 1
            "Bottom Center",    # Position 2  
            "Bottom Right",     # Position 3
            "Middle Left",      # Position 4
            "Middle Right",     # Position 5
            "Top Center"        # Position 6
        ]
        
    def initialize_robot(self):
        """Initialize the robot"""
        print("🤖 Initializing robot...")
        try:
            self.robot = Arm_Device()
            time.sleep(0.1)
            print("✅ Robot connected")
            # Move to home position
            print("🏠 Moving to home position...")
            self.robot.Arm_serial_servo_write6(90, 90, 90, 90, 90, 30, 3000)
            time.sleep(3)
            print("✅ Home position reached")
            return True
        except Exception as e:
            print(f"❌ Robot initialization failed: {e}")
            return False
    
    def move_servo(self, servo_id, angle, speed=1000):
        """Move individual servo"""
        print(f"🤖 Moving servo {servo_id} to {angle}°")
        self.robot.Arm_serial_servo_write(servo_id, angle, speed)
        time.sleep(speed/1000 + 0.5)
    
    def move_all_servos(self, angles, speed=2000):
        """Move all servos to specified angles"""
        print(f"🤖 Moving to: {[f'{a}°' for a in angles]}")
        self.robot.Arm_serial_servo_write6(
            angles[0], angles[1], angles[2],
            angles[3], angles[4], angles[5],
            speed
        )
        time.sleep(speed/1000 + 0.5)
    
    def test_gripper(self):
        """Test gripper open/close"""
        print("🤏 Testing gripper...")
        self.robot.Arm_serial_servo_write(6, 180, 1000)  # Open
        time.sleep(1)
        self.robot.Arm_serial_servo_write(6, 30, 1000)   # Close
        time.sleep(1)
        print("✅ Gripper test completed")
    
    def find_table_height(self):
        """Find the correct height to reach the table"""
        print("\n📏 Finding Table Height")
        print("=" * 40)
        print("We need to find the correct servo angles to reach the table.")
        print("The robot should be able to pick up cups from the table surface.")
        
        # Start with a reasonable position for table access
        # Servo 1 (base): 90° (center)
        # Servo 2 (shoulder): 45° (downward)
        # Servo 3 (elbow): 135° (bent to reach down)
        # Servo 4 (wrist rotation): 90° (neutral)
        # Servo 5 (wrist tilt): 90° (neutral)
        # Servo 6 (gripper): 30° (closed)
        
        table_position = [90, 45, 135, 90, 90, 30]
        print(f"🎯 Trying initial table position: {table_position}")
        
        self.move_all_servos(table_position, 2000)
        
        print("\n🔧 Manual adjustment mode:")
        print("Use these commands to fine-tune the position:")
        print("- '2 60' = Move shoulder down more")
        print("- '2 30' = Move shoulder down even more") 
        print("- '3 150' = Bend elbow more")
        print("- '3 120' = Straighten elbow")
        print("- '1 60' = Rotate base left")
        print("- '1 120' = Rotate base right")
        print("- 't' = Test gripper")
        print("- 'save' = Save this position as table height")
        print("- 'done' = Finish adjustment")
        
        while True:
            command = input("\nEnter command: ").strip().lower()
            if command == 'done':
                break
            elif command == 't':
                self.test_gripper()
            elif command == 'save':
                # Read current positions
                current_positions = []
                for i in range(1, 7):
                    pos = self.robot.Arm_serial_servo_read(i)
                    current_positions.append(pos)
                print(f"💾 Saved table height position: {current_positions}")
                self.table_height_position = current_positions
                break
            elif len(command.split()) == 2:
                try:
                    servo_id = int(command.split()[0])
                    angle = int(command.split()[1])
                    if 1 <= servo_id <= 6:
                        self.move_servo(servo_id, angle, 1000)
                    else:
                        print("❌ Servo ID must be 1-6")
                except:
                    print("❌ Invalid servo command")
            else:
                print("❌ Invalid command")
    
    def calibrate_pyramid_positions(self):
        """Calibrate positions for pyramid stacking"""
        print("\n🏗️ Calibrating Pyramid Stacking Positions")
        print("=" * 50)
        print("We need to calibrate 6 positions for pyramid stacking:")
        for i, pos_name in enumerate(self.pyramid_positions):
            print(f"   {i+1}. {pos_name}")
        
        # Start with table height position
        if hasattr(self, 'table_height_position'):
            base_position = self.table_height_position.copy()
        else:
            # Default table position if not calibrated
            base_position = [90, 45, 135, 90, 90, 30]
        
        print(f"\n📍 Using base position: {base_position}")
        
        for i, pos_name in enumerate(self.pyramid_positions):
            print(f"\n🎯 Calibrating {pos_name} (Position {i+1})")
            print(f"Place a cup at the {pos_name} position on the table.")
            input("Press Enter when cup is in position...")
            
            # Start with base position
            self.move_all_servos(base_position, 2000)
            
            print(f"\nNow adjust the position for {pos_name}:")
            print("- '1 60-120' = Adjust base rotation (left/right)")
            print("- '2 30-60' = Adjust shoulder height")
            print("- '3 120-150' = Adjust elbow bend")
            print("- 't' = Test gripper")
            print("- 'save' = Save this position")
            print("- 'skip' = Skip this position")
            
            while True:
                command = input("Enter command: ").strip().lower()
                if command == 'save':
                    # Read current positions
                    current_positions = []
                    for i in range(1, 7):
                        pos = self.robot.Arm_serial_servo_read(i)
                        current_positions.append(pos)
                    print(f"💾 Saved {pos_name} position: {current_positions}")
                    self.calibrated_positions.append(current_positions)
                    break
                elif command == 'skip':
                    print(f"⏭️ Skipping {pos_name}")
                    # Add a placeholder position
                    self.calibrated_positions.append(base_position.copy())
                    break
                elif command == 't':
                    self.test_gripper()
                elif len(command.split()) == 2:
                    try:
                        servo_id = int(command.split()[0])
                        angle = int(command.split()[1])
                        if 1 <= servo_id <= 6:
                            self.move_servo(servo_id, angle, 1000)
                        else:
                            print("❌ Servo ID must be 1-6")
                    except:
                        print("❌ Invalid servo command")
                else:
                    print("❌ Invalid command")
        
        print(f"\n🎉 Calibration complete!")
        print(f"📊 Calibrated {len(self.calibrated_positions)} pyramid positions:")
        for i, pos in enumerate(self.calibrated_positions):
            print(f"   {self.pyramid_positions[i]}: {pos}")
        
        # Save to file
        self.save_calibration()
    
    def save_calibration(self):
        """Save calibrated positions to file"""
        if not self.calibrated_positions:
            print("❌ No positions to save")
            return
        
        filename = "calibrated_pyramid_positions.py"
        with open(filename, 'w') as f:
            f.write("# Calibrated Pyramid Cup Positions\n")
            f.write("# Generated by table calibration script\n\n")
            f.write("# Pyramid stacking positions (bottom to top)\n")
            f.write("PYRAMID_POSITIONS = [\n")
            for i, pos in enumerate(self.calibrated_positions):
                f.write(f"    {pos},  # {self.pyramid_positions[i]}\n")
            f.write("]\n\n")
            f.write("# Table height reference position\n")
            if hasattr(self, 'table_height_position'):
                f.write(f"TABLE_HEIGHT_POSITION = {self.table_height_position}\n")
            else:
                f.write("TABLE_HEIGHT_POSITION = [90, 45, 135, 90, 90, 30]\n")
        print(f"💾 Calibration saved to {filename}")
        print("You can now use these positions in your pyramid stacking script!")
    
    def test_calibrated_positions(self):
        """Test the calibrated positions"""
        if not self.calibrated_positions:
            print("❌ No calibrated positions to test")
            return
        
        print(f"\n🧪 Testing {len(self.calibrated_positions)} calibrated positions...")
        for i, pos in enumerate(self.calibrated_positions):
            print(f"\nTesting {self.pyramid_positions[i]} position: {pos}")
            self.move_all_servos(pos, 2000)
            time.sleep(2)
            # Test gripper
            print("🤏 Testing gripper...")
            self.robot.Arm_serial_servo_write(6, 180, 1000)
            time.sleep(1)
            self.robot.Arm_serial_servo_write(6, 30, 1000)
            time.sleep(1)
        
        # Return to home
        self.move_all_servos([90, 90, 90, 90, 90, 30], 2000)
        print("✅ Position testing completed!")

def main():
    """Main function"""
    print("🏗️ Table Cup Position Calibrator")
    print("=" * 50)
    print("This will help you calibrate positions for pyramid cup stacking on the table.")
    
    calibrator = TableCupCalibrator()
    if not calibrator.initialize_robot():
        print("❌ Failed to initialize robot")
        return
    
    try:
        print("\n🎯 Choose calibration mode:")
        print("1. Find table height (start here)")
        print("2. Calibrate pyramid positions")
        print("3. Test existing calibration")
        choice = input("Enter choice (1-3): ").strip()
        
        if choice == '1':
            calibrator.find_table_height()
        elif choice == '2':
            calibrator.calibrate_pyramid_positions()
        elif choice == '3':
            calibrator.test_calibrated_positions()
        else:
            print("❌ Invalid choice")
            
    except KeyboardInterrupt:
        print("\n⏹️ Interrupted by user")
    
    print("✅ Calibration complete!")

if __name__ == "__main__":
    main() 