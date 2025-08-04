#!/usr/bin/env python3
"""
Pyramid Cup Stacking Robot - Horizontal Arrangement
Picks up cups from horizontal positions and arranges them in pyramid order
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

class HorizontalPyramidCupStackingRobot:
    def __init__(self):
        self.robot = None
        
        # Pyramid positions (where to place cups)
        self.pyramid_positions = PYRAMID_POSITIONS.copy()
        self.table_height_position = TABLE_HEIGHT_POSITION.copy()
        
        # Horizontal cup pickup positions (where cups are initially placed)
        self.horizontal_cup_positions = [
            [60, 15, 70, 90, 90, 30],   # Cup 1 - Leftmost
            [75, 15, 70, 90, 90, 30],   # Cup 2 - Left center
            [90, 15, 70, 90, 90, 30],   # Cup 3 - Center
            [105, 15, 70, 90, 90, 30],  # Cup 4 - Right center
            [120, 15, 70, 90, 90, 30],  # Cup 5 - Right
            [135, 15, 70, 90, 90, 30],  # Cup 6 - Far right
        ]
        
        # Movement parameters
        self.pickup_speed = 2000
        self.placement_speed = 1500
        self.approach_speed = 1000
        
        # Stacking state
        self.cups_placed = 0
        self.total_cups = len(self.pyramid_positions)
        
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
    
    def pickup_cup_from_horizontal_position(self, cup_index):
        """Pick up a cup from the specified horizontal position"""
        if cup_index >= len(self.horizontal_cup_positions):
            print(f"❌ Invalid cup index: {cup_index}")
            return False
        
        cup_position = self.horizontal_cup_positions[cup_index]
        print(f"🥤 Picking up cup {cup_index + 1} from horizontal position {cup_index + 1}...")
        
        try:
            # Step 1: Move to approach position above cup
            self.approach_position(cup_position)
            
            # Step 2: Open gripper
            print("   🤏 Opening gripper...")
            self.robot.Arm_serial_servo_write(6, 180, 1000)
            time.sleep(1)
            
            # Step 3: Move to pickup position
            self.move_to_position(cup_position, self.pickup_speed, "cup pickup position")
            
            # Step 4: Close gripper
            print("   🤏 Closing gripper to grab cup...")
            self.robot.Arm_serial_servo_write(6, 30, 1000)
            time.sleep(1)
            
            # Step 5: Move back to approach position
            self.approach_position(cup_position)
            
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
    
    def build_pyramid_from_horizontal(self):
        """Build the pyramid by picking up cups from horizontal positions"""
        print("🏗️ Starting Pyramid Construction from Horizontal Arrangement")
        print("=" * 70)
        print("Horizontal cup arrangement:")
        print("🥤 🥤 🥤 🥤 🥤 🥤")
        print()
        print("Pyramid layout:")
        print("     6")
        print("   4   5")
        print("  1  2  3")
        print()
        
        # Show horizontal positions
        print("📊 Horizontal cup positions:")
        for i, pos in enumerate(self.horizontal_cup_positions):
            print(f"   Cup {i+1}: Base rotation {pos[0]}°")
        
        # Show pyramid positions
        print("\n📊 Pyramid placement positions:")
        for i, pos in enumerate(self.pyramid_positions):
            print(f"   {self.pyramid_layout[i]}: Base rotation {pos[0]}°")
        
        # Ask for confirmation
        response = input(f"\nReady to build pyramid with {self.total_cups} cups? (y/n): ").strip().lower()
        if response != 'y':
            print("Pyramid construction cancelled")
            return
        
        try:
            for i in range(self.total_cups):
                cup_number = i + 1
                pyramid_position_name = self.pyramid_layout[i]
                
                print(f"\n{'='*70}")
                print(f"🥤 Processing cup {cup_number}/{self.total_cups}")
                print(f"📍 Pickup: Horizontal position {cup_number}")
                print(f"🎯 Target: {pyramid_position_name}")
                print(f"{'='*70}")
                
                # Pick up cup from horizontal position
                if self.pickup_cup_from_horizontal_position(i):
                    # Place in pyramid position
                    if self.place_cup_in_pyramid(i):
                        self.cups_placed += 1
                        print(f"🎉 Successfully placed cup {cup_number} in {pyramid_position_name}!")
                    else:
                        print("❌ Failed to place cup in pyramid")
                        break
                else:
                    print("❌ Failed to pick up cup from horizontal position")
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
    
    def test_horizontal_positions(self):
        """Test all horizontal cup positions"""
        print(f"🧪 Testing {len(self.horizontal_cup_positions)} horizontal cup positions...")
        
        for i, pos in enumerate(self.horizontal_cup_positions):
            print(f"\nTesting horizontal position {i+1}: {pos}")
            self.move_to_position(pos, 2000, f"horizontal position {i+1}")
            time.sleep(2)
            
            # Test gripper
            print("🤏 Testing gripper...")
            self.robot.Arm_serial_servo_write(6, 180, 1000)
            time.sleep(1)
            self.robot.Arm_serial_servo_write(6, 30, 1000)
            time.sleep(1)
        
        # Test pyramid positions
        print(f"\nTesting {len(self.pyramid_positions)} pyramid positions...")
        for i, pos in enumerate(self.pyramid_positions):
            position_name = self.pyramid_layout[i]
            print(f"\nTesting {position_name}: {pos}")
            self.move_to_position(pos, 2000, position_name)
            time.sleep(2)
        
        # Return to home
        self.move_to_position([90, 90, 90, 90, 90, 30], 2000, "home position")
        print("✅ Position testing completed!")
    
    def manual_control(self):
        """Manual control mode"""
        print("🎮 Manual Control Mode")
        print("Controls:")
        print("- 'h1-6' to move to horizontal cup positions")
        print("- 'p1-6' to move to pyramid positions")
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
            elif command == 't':
                print("🤏 Testing gripper...")
                self.robot.Arm_serial_servo_write(6, 180, 1000)
                time.sleep(1)
                self.robot.Arm_serial_servo_write(6, 30, 1000)
                time.sleep(1)
            elif command.startswith('h') and len(command) == 2:
                try:
                    pos_index = int(command[1]) - 1
                    if 0 <= pos_index < len(self.horizontal_cup_positions):
                        position = self.horizontal_cup_positions[pos_index]
                        self.move_to_position(position, 2000, f"horizontal position {pos_index + 1}")
                    else:
                        print("❌ Invalid horizontal position")
                except:
                    print("❌ Invalid command")
            elif command.startswith('p') and len(command) == 2:
                try:
                    pos_index = int(command[1]) - 1
                    if 0 <= pos_index < len(self.pyramid_positions):
                        position_name = self.pyramid_layout[pos_index]
                        position = self.pyramid_positions[pos_index]
                        self.move_to_position(position, 2000, position_name)
                    else:
                        print("❌ Invalid pyramid position")
                except:
                    print("❌ Invalid command")
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
    print("🏗️ Horizontal Pyramid Cup Stacking Robot")
    print("=" * 60)
    
    robot = HorizontalPyramidCupStackingRobot()
    if not robot.initialize_robot():
        print("❌ Failed to initialize robot")
        return
    
    try:
        print("\n🎯 Choose mode:")
        print("1. Build pyramid from horizontal arrangement")
        print("2. Test horizontal and pyramid positions")
        print("3. Manual control")
        choice = input("Enter choice (1-3): ").strip()
        
        if choice == '1':
            robot.build_pyramid_from_horizontal()
        elif choice == '2':
            robot.test_horizontal_positions()
        elif choice == '3':
            robot.manual_control()
        else:
            print("❌ Invalid choice")
            
    except KeyboardInterrupt:
        print("\n⏹️ Interrupted by user")
    
    print("✅ Program complete!")

if __name__ == "__main__":
    main() 