#!/usr/bin/env python3
"""
Pyramid Cup Stacking Robot
Picks up cups from a stack and arranges them in pyramid order on the table
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

# Try to import calibrated pyramid positions
try:
    from calibrated_pyramid_positions import PYRAMID_POSITIONS, TABLE_HEIGHT_POSITION
    print("✅ Loaded calibrated pyramid positions")
    CALIBRATED_POSITIONS_AVAILABLE = True
except ImportError:
    print("⚠️ No calibrated pyramid positions found - using default positions")
    CALIBRATED_POSITIONS_AVAILABLE = False
    # Default positions (you should calibrate these)
    PYRAMID_POSITIONS = [
        [90, 15, 70, 90, 90, 30],  # Bottom Left
        [90, 15, 70, 90, 90, 30],  # Bottom Center
        [90, 15, 70, 90, 90, 30],  # Bottom Right
        [90, 15, 70, 90, 90, 30],  # Middle Left
        [90, 15, 70, 90, 90, 30],  # Middle Right
        [90, 15, 70, 90, 90, 30],  # Top Center
    ]
    TABLE_HEIGHT_POSITION = [90, 15, 70, 90, 90, 30]

class PyramidCupStackingRobot:
    def __init__(self):
        self.robot = None
        
        # Pyramid positions
        self.pyramid_positions = PYRAMID_POSITIONS.copy()
        self.table_height_position = TABLE_HEIGHT_POSITION.copy()
        
        # Movement parameters
        self.pickup_speed = 2000
        self.placement_speed = 1500
        self.approach_speed = 1000
        
        # Stacking state
        self.cups_placed = 0
        self.total_cups = len(self.pyramid_positions)
        
        # Cup stack position (where cups are initially stacked)
        self.cup_stack_position = [90, 15, 70, 90, 90, 30]  # Same as table height
        
        # Pyramid layout
        self.pyramid_layout = [
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
    
    def move_to_position(self, angles, speed=2000, description=""):
        """Move robot to specified servo angles"""
        print(f"🤖 Moving to {description}...")
        print(f"   Servo angles: {[f'{a}°' for a in angles]}")
        self.robot.Arm_serial_servo_write6(
            angles[0], angles[1], angles[2],
            angles[3], angles[4], angles[5],
            speed
        )
        time.sleep(speed/1000 + 0.5)
    
    def approach_position(self, target_position):
        """Move to approach position above target"""
        approach_position = target_position.copy()
        approach_position[2] += 10  # Move elbow up a bit
        self.move_to_position(approach_position, self.approach_speed, "approach position")
    
    def pickup_cup_from_stack(self, stack_height=0):
        """Pick up a cup from the initial stack"""
        print(f"🥤 Picking up cup {self.cups_placed + 1} from stack...")
        
        try:
            # Calculate stack position with height adjustment
            stack_position = self.cup_stack_position.copy()
            stack_position[2] -= int(stack_height * 100)  # Adjust for stack height
            
            # Step 1: Move to approach position above stack
            self.approach_position(stack_position)
            
            # Step 2: Open gripper
            print("   🤏 Opening gripper...")
            self.robot.Arm_serial_servo_write(6, 180, 1000)
            time.sleep(1)
            
            # Step 3: Move to stack position
            self.move_to_position(stack_position, self.pickup_speed, "stack pickup position")
            
            # Step 4: Close gripper
            print("   🤏 Closing gripper to grab cup...")
            self.robot.Arm_serial_servo_write(6, 30, 1000)
            time.sleep(1)
            
            # Step 5: Move back to approach position
            self.approach_position(stack_position)
            
            print("   ✅ Cup picked successfully!")
            return True
            
        except Exception as e:
            print(f"   ❌ Pickup failed: {e}")
            return False
    
    def place_cup_in_pyramid(self, pyramid_position_index):
        """Place cup in the specified pyramid position"""
        if pyramid_position_index >= len(self.pyramid_positions):
            print("❌ Invalid pyramid position")
            return False
        
        position_name = self.pyramid_layout[pyramid_position_index]
        position = self.pyramid_positions[pyramid_position_index]
        
        print(f"🏗️ Placing cup in {position_name}...")
        
        try:
            # Step 1: Move to approach position above target
            self.approach_position(position)
            
            # Step 2: Move to placement position
            self.move_to_position(position, self.placement_speed, f"{position_name} position")
            
            # Step 3: Open gripper
            print("   🤏 Releasing cup...")
            self.robot.Arm_serial_servo_write(6, 180, 1000)
            time.sleep(1)
            
            # Step 4: Move back to approach position
            self.approach_position(position)
            
            print(f"   ✅ Cup placed in {position_name}!")
            return True
            
        except Exception as e:
            print(f"   ❌ Placement failed: {e}")
            return False
    
    def build_pyramid(self):
        """Build the pyramid by placing cups in the correct order"""
        print("🏗️ Starting Pyramid Construction")
        print("=" * 50)
        print("Pyramid layout:")
        print("     6")
        print("   4   5")
        print("  1  2  3")
        print()
        
        # Show positions
        print("📊 Using pyramid positions:")
        for i, pos in enumerate(self.pyramid_positions):
            print(f"   {i+1}. {self.pyramid_layout[i]}: {pos}")
        
        # Ask for confirmation
        response = input(f"\nReady to build pyramid with {self.total_cups} cups? (y/n): ").strip().lower()
        if response != 'y':
            print("Pyramid construction cancelled")
            return
        
        try:
            for i in range(self.total_cups):
                cup_number = i + 1
                position_name = self.pyramid_layout[i]
                
                print(f"\n{'='*50}")
                print(f"🥤 Processing cup {cup_number}/{self.total_cups}")
                print(f"📍 Target: {position_name}")
                print(f"{'='*50}")
                
                # Pick up cup from stack
                if self.pickup_cup_from_stack():
                    # Place in pyramid position
                    if self.place_cup_in_pyramid(i):
                        self.cups_placed += 1
                        print(f"🎉 Successfully placed cup {cup_number} in {position_name}!")
                    else:
                        print("❌ Failed to place cup in pyramid")
                        break
                else:
                    print("❌ Failed to pick up cup from stack")
                    break
                
                # Small pause between cups
                time.sleep(1)
            
            print(f"\n🎉 Pyramid construction completed!")
            print(f"📊 Total cups placed: {self.cups_placed}/{self.total_cups}")
            
            # Return to home position
            print("\n🏠 Returning to home position...")
            self.robot.Arm_serial_servo_write6(90, 90, 90, 90, 90, 30, 3000)
            time.sleep(3)
            print("✅ Home position reached")
            
        except KeyboardInterrupt:
            print("\n⏹️ Pyramid construction interrupted by user")
            # Return to home position
            self.robot.Arm_serial_servo_write6(90, 90, 90, 90, 90, 30, 3000)
            time.sleep(3)
    
    def test_positions(self):
        """Test all pyramid positions"""
        print(f"🧪 Testing {len(self.pyramid_positions)} pyramid positions...")
        
        for i, pos in enumerate(self.pyramid_positions):
            position_name = self.pyramid_layout[i]
            print(f"\nTesting {position_name} position: {pos}")
            self.move_to_position(pos, 2000, position_name)
            time.sleep(2)
            
            # Test gripper
            print("🤏 Testing gripper...")
            self.robot.Arm_serial_servo_write(6, 180, 1000)
            time.sleep(1)
            self.robot.Arm_serial_servo_write(6, 30, 1000)
            time.sleep(1)
        
        # Test cup stack position
        print(f"\nTesting cup stack position: {self.cup_stack_position}")
        self.move_to_position(self.cup_stack_position, 2000, "cup stack")
        time.sleep(2)
        
        # Return to home
        self.move_to_position([90, 90, 90, 90, 90, 30], 2000, "home position")
        print("✅ Position testing completed!")
    
    def manual_control(self):
        """Manual control mode"""
        print("🎮 Manual Control Mode")
        print("Controls:")
        print("- '1-6' to move to pyramid positions")
        print("- 's' to move to cup stack position")
        print("- 'h' to home position")
        print("- '1-6' + number: Move servo (e.g., '1 60')")
        print("- 'all' + angles: Move all servos")
        print("- 'g' + number: Move gripper")
        print("- 't' to test gripper")
        print("- 'q' to quit")
        
        while True:
            command = input("\nEnter command: ").strip().lower()
            if command == 'q':
                break
            elif command == 'h':
                self.move_to_position([90, 90, 90, 90, 90, 30], 2000, "home position")
            elif command == 's':
                self.move_to_position(self.cup_stack_position, 2000, "cup stack position")
            elif command == 't':
                print("🤏 Testing gripper...")
                self.robot.Arm_serial_servo_write(6, 180, 1000)
                time.sleep(1)
                self.robot.Arm_serial_servo_write(6, 30, 1000)
                time.sleep(1)
            elif command in ['1', '2', '3', '4', '5', '6']:
                pos_index = int(command) - 1
                if pos_index < len(self.pyramid_positions):
                    position_name = self.pyramid_layout[pos_index]
                    self.move_to_position(self.pyramid_positions[pos_index], 2000, position_name)
                else:
                    print("❌ Invalid position")
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
                        self.move_to_position(angles, 2000, "manual position")
                    else:
                        print("❌ Need 6 angles for 'all' command")
                except:
                    print("❌ Invalid 'all' command")
            elif len(command.split()) == 2:
                try:
                    servo_id = int(command.split()[0])
                    angle = int(command.split()[1])
                    if 1 <= servo_id <= 6:
                        print(f"🤖 Moving servo {servo_id} to {angle}°")
                        self.robot.Arm_serial_servo_write(servo_id, angle, 1000)
                        time.sleep(1)
                    else:
                        print("❌ Servo ID must be 1-6")
                except:
                    print("❌ Invalid servo command")
            else:
                print("❌ Invalid command")

def main():
    """Main function"""
    print("🏗️ Pyramid Cup Stacking Robot")
    print("=" * 50)
    
    robot = PyramidCupStackingRobot()
    if not robot.initialize_robot():
        print("❌ Failed to initialize robot")
        return
    
    try:
        print("\n🎯 Choose mode:")
        print("1. Build pyramid (automatic)")
        print("2. Test positions")
        print("3. Manual control")
        choice = input("Enter choice (1-3): ").strip()
        
        if choice == '1':
            robot.build_pyramid()
        elif choice == '2':
            robot.test_positions()
        elif choice == '3':
            robot.manual_control()
        else:
            print("❌ Invalid choice")
            
    except KeyboardInterrupt:
        print("\n⏹️ Interrupted by user")
    
    print("✅ Program complete!")

if __name__ == "__main__":
    main() 