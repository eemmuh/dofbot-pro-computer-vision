#!/usr/bin/env python3
"""
Manual Coordinate Control for DOFBot Pro
Direct control of robot positions using joint angles
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
except ImportError:
    print("❌ smbus2 not available")
    sys.exit(1)

# Import robot control
try:
    from Arm_Lib import Arm_Device
except Exception as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

class ManualCoordinateControl:
    def __init__(self):
        self.robot = None
        
        # Predefined positions for cup stacking - CORRECT GRIPPER ANGLES & HEIGHTS
        self.positions = {
            'home': [90, 30, 40, 90, 90, 30],           # Safe home position
            'pickup_approach': [90, 35, 45, 90, 90, 30], # Above cup to pick up
            'pickup_grip': [90, 30, 35, 90, 90, 40],     # HIGHER to cup level, gripper closed (40°)
            'pickup_lift': [90, 40, 50, 90, 90, 40],     # Lifted cup
            'stack_approach': [90, 40, 50, 90, 90, 40],  # Above stack position
            'stack_place': [90, 30, 35, 90, 90, 40],     # HIGHER to stack level
            'stack_release': [90, 30, 35, 90, 90, 30],   # Open gripper (30°)
            'stack_lift': [90, 45, 55, 90, 90, 30],      # Lift away from stack
        }
        
        # Current position tracking
        self.current_position = self.positions['home'].copy()
        self.stack_height = 0
        
    def initialize_robot(self):
        """Initialize robot only"""
        print("🔧 Initializing robot...")
        try:
            self.robot = Arm_Device()
            time.sleep(0.1)
            print("✅ Robot connected")
            return True
        except Exception as e:
            print(f"❌ Robot initialization failed: {e}")
            return False
    
    def move_to_position(self, angles, speed=2000, description=""):
        """Move robot to specified joint angles"""
        if description:
            print(f"🤖 {description}")
        print(f"   Moving to: {angles}")
        
        for i, angle in enumerate(angles):
            self.robot.Arm_serial_servo_write(i+1, int(angle), speed)
            time.sleep(0.1)
        time.sleep(speed/1000 + 0.5)
        self.current_position = angles.copy()
        print("✅ Movement completed")
    
    def explain_coordinates(self):
        """Explain what the coordinates represent"""
        print("\n🎯 DOFBot Pro Joint Coordinates Explained")
        print("=" * 50)
        print("The robot has 6 joints, each with an angle from 0-180 degrees:")
        print("")
        print("Joint 1 (Base):     [0-180°] - Rotates the entire arm left/right")
        print("Joint 2 (Shoulder): [0-180°] - Lifts/lowers the arm up/down")
        print("Joint 3 (Elbow):    [0-180°] - Bends the forearm up/down")
        print("Joint 4 (Wrist):    [0-180°] - Rotates the wrist left/right")
        print("Joint 5 (Wrist):    [0-180°] - Tilts the wrist up/down")
        print("Joint 6 (Gripper):  [0-180°] - Opens/closes the gripper")
        print("")
        print("Example: [90, 30, 40, 90, 90, 30]")
        print("  - Base: 90° (straight ahead)")
        print("  - Shoulder: 30° (arm lowered)")
        print("  - Elbow: 40° (forearm bent)")
        print("  - Wrist rotation: 90° (neutral)")
        print("  - Wrist tilt: 90° (neutral)")
        print("  - Gripper: 30° (open)")
        print("")
        print("💡 Tips:")
        print("  - Lower shoulder (20-40°) = arm down")
        print("  - Higher shoulder (50-80°) = arm up")
        print("  - Lower elbow (20-40°) = arm extended")
        print("  - Higher elbow (60-100°) = arm retracted")
        print("  - Gripper 0° = closed, 30° = open")
    
    def show_predefined_positions(self):
        """Show all predefined positions"""
        print("\n📋 Predefined Positions")
        print("=" * 30)
        for name, angles in self.positions.items():
            print(f"{name:15}: {angles}")
        print("")
    
    def set_custom_position(self):
        """Allow user to set custom position"""
        print("\n🎯 Set Custom Position")
        print("=" * 25)
        print("Enter joint angles (0-180 for each joint):")
        
        try:
            angles = []
            joint_names = ["Base", "Shoulder", "Elbow", "Wrist Rot", "Wrist Tilt", "Gripper"]
            
            for i, name in enumerate(joint_names):
                while True:
                    try:
                        angle = int(input(f"Joint {i+1} ({name}): "))
                        if 0 <= angle <= 180:
                            angles.append(angle)
                            break
                        else:
                            print("❌ Angle must be between 0-180")
                    except ValueError:
                        print("❌ Please enter a valid number")
            
            print(f"\nCustom position: {angles}")
            confirm = input("Move to this position? (y/n): ").lower()
            if confirm == 'y':
                self.move_to_position(angles, description="Moving to custom position")
            else:
                print("❌ Movement cancelled")
                
        except KeyboardInterrupt:
            print("\n❌ Cancelled")
    
    def test_gripper(self):
        """Test gripper open/close functionality"""
        print("\n🤖 Testing Gripper Functionality")
        print("=" * 35)
        
        # Move to safe position first
        self.move_to_position([90, 40, 50, 90, 90, 30], description="Moving to safe position")
        time.sleep(1)
        
        # Test gripper open
        print("🔓 Testing gripper OPEN...")
        self.move_to_position([90, 40, 50, 90, 90, 30], description="Gripper OPEN (30°)")
        time.sleep(2)
        
        # Test gripper close
        print("🔒 Testing gripper CLOSE...")
        self.move_to_position([90, 40, 50, 90, 90, 0], description="Gripper CLOSE (0°)")
        time.sleep(2)
        
        # Test gripper open again
        print("🔓 Testing gripper OPEN again...")
        self.move_to_position([90, 40, 50, 90, 90, 30], description="Gripper OPEN (30°)")
        time.sleep(2)
        
        print("✅ Gripper test completed")
        print("💡 Check if gripper actually opens and closes!")
        print("   - 30° = Open")
        print("   - 0° = Closed")

    def run_cup_stacking_sequence(self):
        """Run the complete cup stacking sequence"""
        print("\n🎯 Running Cup Stacking Sequence")
        print("=" * 35)
        
        try:
            # 1. Start at home
            self.move_to_position(self.positions['home'], description="1. Moving to home position")
            time.sleep(1)
            
            # 2. Move to pickup approach
            self.move_to_position(self.positions['pickup_approach'], description="2. Moving above cup")
            time.sleep(1)
            
            # 3. Move to pickup grip
            self.move_to_position(self.positions['pickup_grip'], description="3. Gripping cup")
            time.sleep(1)
            
            # 4. Lift cup
            self.move_to_position(self.positions['pickup_lift'], description="4. Lifting cup")
            time.sleep(1)
            
            # 5. Move to stack approach
            self.move_to_position(self.positions['stack_approach'], description="5. Moving above stack")
            time.sleep(1)
            
            # 6. Place on stack
            self.move_to_position(self.positions['stack_place'], description="6. Placing cup on stack")
            time.sleep(1)
            
            # 7. Release gripper
            self.move_to_position(self.positions['stack_release'], description="7. Releasing cup")
            time.sleep(1)
            
            # 8. Lift away
            self.move_to_position(self.positions['stack_lift'], description="8. Lifting away from stack")
            time.sleep(1)
            
            # 9. Return to home
            self.move_to_position(self.positions['home'], description="9. Returning to home")
            
            self.stack_height += 1
            print(f"✅ Cup stacking sequence completed! Stack height: {self.stack_height}")
            
        except KeyboardInterrupt:
            print("\n❌ Sequence interrupted")
            self.move_to_position(self.positions['home'], description="Emergency return to home")
    
    def interactive_mode(self):
        """Interactive mode for manual control"""
        print("\n🎯 Interactive Robot Control")
        print("=" * 35)
        print("Commands:")
        print("  h - Home position")
        print("  p - Pickup sequence")
        print("  s - Stack sequence")
        print("  f - Full stacking sequence")
        print("  g - Test gripper (open/close)")
        print("  c - Custom position")
        print("  e - Explain coordinates")
        print("  l - List predefined positions")
        print("  q - Quit")
        
        while True:
            try:
                command = input(f"\nEnter command (stack height: {self.stack_height}): ").lower().strip()
                
                if command == 'q':
                    break
                elif command == 'h':
                    self.move_to_position(self.positions['home'], description="Moving to home")
                elif command == 'p':
                    print("🤖 Pickup sequence...")
                    self.move_to_position(self.positions['pickup_approach'], description="Above cup")
                    time.sleep(1)
                    self.move_to_position(self.positions['pickup_grip'], description="Gripping")
                    time.sleep(1)
                    self.move_to_position(self.positions['pickup_lift'], description="Lifting")
                elif command == 's':
                    print("🤖 Stack sequence...")
                    self.move_to_position(self.positions['stack_approach'], description="Above stack")
                    time.sleep(1)
                    self.move_to_position(self.positions['stack_place'], description="Placing")
                    time.sleep(1)
                    self.move_to_position(self.positions['stack_release'], description="Releasing")
                    time.sleep(1)
                    self.move_to_position(self.positions['stack_lift'], description="Lifting away")
                    self.stack_height += 1
                elif command == 'f':
                    self.run_cup_stacking_sequence()
                elif command == 'g':
                    self.test_gripper()
                elif command == 'c':
                    self.set_custom_position()
                elif command == 'e':
                    self.explain_coordinates()
                elif command == 'l':
                    self.show_predefined_positions()
                else:
                    print("❌ Unknown command. Use: h, p, s, f, g, c, e, l, q")
                    
            except KeyboardInterrupt:
                print("\n👋 Exiting...")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

def main():
    """Main function"""
    print("🤖 Manual Coordinate Control for DOFBot Pro")
    print("=" * 50)
    print("Direct control of robot using joint angles")
    
    controller = ManualCoordinateControl()
    
    if not controller.initialize_robot():
        print("❌ Failed to initialize robot")
        return
    
    try:
        # Show explanation first
        controller.explain_coordinates()
        controller.show_predefined_positions()
        
        # Run interactive mode
        controller.interactive_mode()
    finally:
        print("👋 Robot control completed")

if __name__ == "__main__":
    main()