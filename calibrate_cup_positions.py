#!/usr/bin/env python3
"""
Cup Position Calibration
Help find the correct servo angles for your actual cup positions
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

class CupPositionCalibrator:
    def __init__(self):
        self.robot = None
        self.calibrated_positions = []
        
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
    
    def manual_positioning(self):
        """Manual positioning mode"""
        print("\n🎮 Manual Positioning Mode")
        print("Controls:")
        print("- '1-6' + number: Move servo (e.g., '1 60' moves servo 1 to 60°)")
        print("- 'all' + angles: Move all servos (e.g., 'all 90 90 90 90 90 30')")
        print("- 'g' + number: Move gripper (e.g., 'g 180' opens gripper)")
        print("- 'h': Home position")
        print("- 't': Test gripper")
        print("- 's': Save current position")
        print("- 'q': Quit")
        
        while True:
            command = input("\nEnter command: ").strip().lower()
            
            if command == 'q':
                break
            elif command == 'h':
                self.move_all_servos([90, 90, 90, 90, 90, 30], 2000)
            elif command == 't':
                self.test_gripper()
            elif command == 's':
                # Read current servo positions
                current_positions = []
                for i in range(1, 7):
                    pos = self.robot.Arm_serial_servo_read(i)
                    current_positions.append(pos)
                print(f"💾 Saved position: {current_positions}")
                self.calibrated_positions.append(current_positions)
            elif command.startswith('g '):
                try:
                    angle = int(command.split()[1])
                    self.robot.Arm_serial_servo_write(6, angle, 1000)
                    print(f"🤏 Gripper moved to {angle}°")
                except:
                    print("❌ Invalid gripper command")
            elif command.startswith('all '):
                try:
                    angles = [int(x) for x in command.split()[1:]]
                    if len(angles) == 6:
                        self.move_all_servos(angles, 2000)
                    else:
                        print("❌ Need 6 angles for 'all' command")
                except:
                    print("❌ Invalid 'all' command")
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
    
    def guided_calibration(self):
        """Guided calibration process"""
        print("\n🎯 Guided Cup Position Calibration")
        print("=" * 50)
        print("This will help you find the right positions for your cups.")
        print("Place your cups on the table and we'll calibrate each position.")
        
        num_cups = int(input("How many cups do you want to calibrate? (1-5): "))
        
        for cup_num in range(1, num_cups + 1):
            print(f"\n🥤 Calibrating cup {cup_num}")
            print(f"Place cup {cup_num} on the table where you want the robot to pick it up.")
            input("Press Enter when cup is in position...")
            
            print(f"\nNow let's find the right position for cup {cup_num}:")
            print("1. Start with home position")
            self.move_all_servos([90, 90, 90, 90, 90, 30], 2000)
            
            print("2. Let's adjust the base rotation (servo 1)")
            print("   - Use '1 60' to move left")
            print("   - Use '1 120' to move right")
            print("   - Use '1 90' for center")
            
            while True:
                command = input("Adjust base rotation (or 'done'): ").strip()
                if command == 'done':
                    break
                elif len(command.split()) == 2:
                    try:
                        servo_id = int(command.split()[0])
                        angle = int(command.split()[1])
                        if servo_id == 1:
                            self.move_servo(1, angle, 1000)
                    except:
                        print("❌ Invalid command")
            
            print("3. Now adjust the shoulder (servo 2) for height")
            print("   - Use '2 60' to move down")
            print("   - Use '2 120' to move up")
            print("   - Use '2 90' for middle")
            
            while True:
                command = input("Adjust shoulder height (or 'done'): ").strip()
                if command == 'done':
                    break
                elif len(command.split()) == 2:
                    try:
                        servo_id = int(command.split()[0])
                        angle = int(command.split()[1])
                        if servo_id == 2:
                            self.move_servo(2, angle, 1000)
                    except:
                        print("❌ Invalid command")
            
            print("4. Test the gripper at this position")
            self.test_gripper()
            
            # Save the position
            current_positions = []
            for i in range(1, 7):
                pos = self.robot.Arm_serial_servo_read(i)
                current_positions.append(pos)
            
            print(f"💾 Saved position for cup {cup_num}: {current_positions}")
            self.calibrated_positions.append(current_positions)
            
            # Move back to home
            self.move_all_servos([90, 90, 90, 90, 90, 30], 2000)
        
        print(f"\n🎉 Calibration complete!")
        print(f"📊 Calibrated {len(self.calibrated_positions)} cup positions:")
        for i, pos in enumerate(self.calibrated_positions):
            print(f"   Cup {i+1}: {pos}")
        
        # Save to file
        self.save_calibration()
    
    def save_calibration(self):
        """Save calibrated positions to file"""
        if not self.calibrated_positions:
            print("❌ No positions to save")
            return
        
        filename = "calibrated_cup_positions.py"
        with open(filename, 'w') as f:
            f.write("# Calibrated Cup Positions\n")
            f.write("# Generated by calibration script\n\n")
            f.write("CUP_POSITIONS = [\n")
            for i, pos in enumerate(self.calibrated_positions):
                f.write(f"    {pos},  # Cup {i+1}\n")
            f.write("]\n\n")
            f.write("# Stack position (center)\n")
            f.write("STACK_POSITION = [90, 90, 90, 90, 90, 30]\n")
        
        print(f"💾 Calibration saved to {filename}")
        print("You can now use these positions in your stacking script!")
    
    def test_calibrated_positions(self):
        """Test the calibrated positions"""
        if not self.calibrated_positions:
            print("❌ No calibrated positions to test")
            return
        
        print(f"\n🧪 Testing {len(self.calibrated_positions)} calibrated positions...")
        
        for i, pos in enumerate(self.calibrated_positions):
            print(f"\nTesting cup {i+1} position: {pos}")
            self.move_all_servos(pos, 2000)
            time.sleep(2)
            self.test_gripper()
            time.sleep(1)
        
        # Return to home
        self.move_all_servos([90, 90, 90, 90, 90, 30], 2000)
        print("✅ Position testing completed!")

def main():
    """Main function"""
    print("🎯 Cup Position Calibrator")
    print("=" * 50)
    
    calibrator = CupPositionCalibrator()
    
    if not calibrator.initialize_robot():
        print("❌ Failed to initialize robot")
        return
    
    try:
        print("\n🎯 Choose calibration mode:")
        print("1. Guided calibration (step-by-step)")
        print("2. Manual positioning (free-form)")
        print("3. Test existing calibration")
        
        choice = input("Enter choice (1-3): ").strip()
        
        if choice == '1':
            calibrator.guided_calibration()
        elif choice == '2':
            calibrator.manual_positioning()
        elif choice == '3':
            calibrator.test_calibrated_positions()
        else:
            print("❌ Invalid choice")
    
    except KeyboardInterrupt:
        print("\n⏹️ Interrupted by user")
    
    print("✅ Calibration complete!")

if __name__ == "__main__":
    main() 