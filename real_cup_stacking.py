#!/usr/bin/env python3
"""
Real Cup Stacking Robot
Actually moves to different positions to pick up cups one by one
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

class RealCupStackingRobot:
    def __init__(self):
        self.robot = None
        
        # Cup pickup positions (servo angles for different cup locations)
        # Format: [base, shoulder, elbow, wrist, wrist_rotate, gripper]
        self.cup_positions = [
            [60, 90, 90, 90, 90, 30],   # Cup 1 - Left position
            [90, 90, 90, 90, 90, 30],   # Cup 2 - Center position
            [120, 90, 90, 90, 90, 30],  # Cup 3 - Right position
            [75, 90, 90, 90, 90, 30],   # Cup 4 - Left-center
            [105, 90, 90, 90, 90, 30],  # Cup 5 - Right-center
        ]
        
        # Stack position (where to place cups)
        self.stack_position = [90, 90, 90, 90, 90, 30]  # Center stack
        
        # Movement parameters
        self.pickup_speed = 2000
        self.placement_speed = 1500
        self.approach_speed = 1000
        
        # Stack tracking
        self.cups_stacked = 0
        self.stack_height = 0
        self.cup_height = 0.12  # meters
        
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
    
    def move_to_position(self, angles, speed=2000, description=""):
        """Move robot to specific servo angles"""
        print(f"🤖 Moving to {description}...")
        print(f"   Servo angles: {[f'{a}°' for a in angles]}")
        
        self.robot.Arm_serial_servo_write6(
            angles[0], angles[1], angles[2], 
            angles[3], angles[4], angles[5], 
            speed
        )
        time.sleep(speed/1000 + 0.5)  # Wait for movement to complete
    
    def approach_cup(self, cup_angles):
        """Move to approach position above a cup"""
        # Approach position is slightly higher than pickup position
        approach_angles = cup_angles.copy()
        approach_angles[2] += 10  # Move elbow up a bit
        
        self.move_to_position(approach_angles, self.approach_speed, "approach position")
    
    def pickup_cup(self, cup_number, cup_angles):
        """Pick up a cup at the specified position"""
        print(f"\n🥤 Picking up cup {cup_number}...")
        
        # Step 1: Move to approach position above the cup
        self.approach_cup(cup_angles)
        
        # Step 2: Open gripper
        print("   🤏 Opening gripper...")
        self.robot.Arm_serial_servo_write(6, 180, 1000)
        time.sleep(1)
        
        # Step 3: Move down to cup position
        self.move_to_position(cup_angles, self.pickup_speed, "cup pickup position")
        
        # Step 4: Close gripper to grab cup
        print("   🤏 Closing gripper to grab cup...")
        self.robot.Arm_serial_servo_write(6, 30, 1000)
        time.sleep(1)
        
        # Step 5: Move back to approach position
        self.approach_cup(cup_angles)
        
        print(f"   ✅ Cup {cup_number} picked successfully!")
    
    def place_cup_in_stack(self, cup_number):
        """Place cup in the stacking position"""
        print(f"🏗️ Placing cup {cup_number} in stack...")
        
        # Calculate stack height (each cup adds to the height)
        stack_angles = self.stack_position.copy()
        stack_angles[2] -= int(self.stack_height * 100)  # Adjust elbow for stack height
        
        # Step 1: Move to approach position above stack
        approach_stack = stack_angles.copy()
        approach_stack[2] += 10  # Slightly higher
        self.move_to_position(approach_stack, self.placement_speed, "stack approach")
        
        # Step 2: Move to stack position
        self.move_to_position(stack_angles, self.placement_speed, "stack position")
        
        # Step 3: Open gripper to release cup
        print("   🤏 Releasing cup in stack...")
        self.robot.Arm_serial_servo_write(6, 180, 1000)
        time.sleep(1)
        
        # Step 4: Move back to approach position
        self.move_to_position(approach_stack, self.placement_speed, "stack approach")
        
        # Update stack tracking
        self.stack_height += self.cup_height
        self.cups_stacked += 1
        
        print(f"   ✅ Cup {cup_number} placed in stack! (Stack height: {self.stack_height:.3f}m)")
    
    def stack_cups_sequentially(self, num_cups=3):
        """Stack cups one by one in sequence"""
        print(f"🎯 Starting sequential cup stacking...")
        print(f"📊 Will stack {num_cups} cups")
        
        # Ask for confirmation
        response = input(f"\nReady to stack {num_cups} cups? (y/n): ").strip().lower()
        if response != 'y':
            print("Stacking cancelled")
            return
        
        try:
            for i in range(num_cups):
                if i >= len(self.cup_positions):
                    print(f"⚠️ Only {len(self.cup_positions)} cup positions defined")
                    break
                
                cup_number = i + 1
                cup_angles = self.cup_positions[i]
                
                print(f"\n{'='*50}")
                print(f"🥤 Processing cup {cup_number}/{num_cups}")
                print(f"{'='*50}")
                
                # Pick up the cup
                self.pickup_cup(cup_number, cup_angles)
                
                # Place it in the stack
                self.place_cup_in_stack(cup_number)
                
                # Small pause between cups
                time.sleep(1)
            
            print(f"\n🎉 Sequential stacking completed!")
            print(f"📊 Total cups stacked: {self.cups_stacked}")
            print(f"🏗️ Final stack height: {self.stack_height:.3f}m")
            
            # Return to home position
            print("\n🏠 Returning to home position...")
            self.robot.Arm_serial_servo_write6(90, 90, 90, 90, 90, 30, 3000)
            time.sleep(3)
            print("✅ Home position reached")
            
        except KeyboardInterrupt:
            print("\n⏹️ Stacking interrupted by user")
            # Return to home position
            self.robot.Arm_serial_servo_write6(90, 90, 90, 90, 90, 30, 3000)
            time.sleep(3)
    
    def test_cup_positions(self):
        """Test moving to each cup position"""
        print("🧪 Testing cup positions...")
        
        for i, angles in enumerate(self.cup_positions):
            print(f"\nTesting position {i+1}: {angles}")
            self.move_to_position(angles, 2000, f"cup position {i+1}")
            time.sleep(2)
        
        # Return to home
        self.move_to_position([90, 90, 90, 90, 90, 30], 2000, "home position")
        print("✅ Position testing completed!")
    
    def run_interactive_mode(self):
        """Run interactive mode for manual testing"""
        print("🎮 Interactive Mode")
        print("Controls:")
        print("- Press '1-5' to move to cup positions")
        print("- Press 's' to move to stack position")
        print("- Press 'h' to home position")
        print("- Press 'o' to open gripper")
        print("- Press 'c' to close gripper")
        print("- Press 't' to test all positions")
        print("- Press 'q' to quit")
        
        while True:
            command = input("\nEnter command: ").strip().lower()
            
            if command == 'q':
                break
            elif command in ['1', '2', '3', '4', '5']:
                cup_index = int(command) - 1
                if cup_index < len(self.cup_positions):
                    self.move_to_position(self.cup_positions[cup_index], 2000, f"cup position {command}")
                else:
                    print("❌ Invalid cup position")
            elif command == 's':
                self.move_to_position(self.stack_position, 2000, "stack position")
            elif command == 'h':
                self.move_to_position([90, 90, 90, 90, 90, 30], 2000, "home position")
            elif command == 'o':
                print("🤏 Opening gripper...")
                self.robot.Arm_serial_servo_write(6, 180, 1000)
            elif command == 'c':
                print("🤏 Closing gripper...")
                self.robot.Arm_serial_servo_write(6, 30, 1000)
            elif command == 't':
                self.test_cup_positions()
            else:
                print("❌ Invalid command")

def main():
    """Main function"""
    print("🥤 Real Cup Stacking Robot")
    print("=" * 50)
    
    robot = RealCupStackingRobot()
    
    if not robot.initialize_robot():
        print("❌ Failed to initialize robot")
        return
    
    try:
        print("\n🎯 Choose mode:")
        print("1. Sequential cup stacking")
        print("2. Interactive mode")
        print("3. Test cup positions")
        
        choice = input("Enter choice (1-3): ").strip()
        
        if choice == '1':
            num_cups = input("How many cups to stack? (1-5): ").strip()
            try:
                num_cups = int(num_cups)
                robot.stack_cups_sequentially(num_cups)
            except ValueError:
                print("❌ Invalid number")
        elif choice == '2':
            robot.run_interactive_mode()
        elif choice == '3':
            robot.test_cup_positions()
        else:
            print("❌ Invalid choice")
    
    except KeyboardInterrupt:
        print("\n⏹️ Interrupted by user")
    
    print("✅ Program complete!")

if __name__ == "__main__":
    main() 