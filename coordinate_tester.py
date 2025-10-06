
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

class SimpleCoordinateTester:
    def __init__(self):
        self.robot = None
        self.current_position = [90, 20, 50, 90, 90, 30]  # Home position
        
        # Simple test positions - optimized for cup pickup sequence
        self.positions = {
            'home': [90, 20, 50, 90, 90, 30],      # Good cup pickup height
            'pickup': [90, 20, 50, 90, 90, 30],     # Approach cup position
            'grip': [90, 20, 50, 90, 90, 0],        # At cup level, gripper closed
            'lift': [90, 35, 65, 90, 90, 0],        # Lifted cup (higher shoulder + elbow)
            'stack': [90, 20, 50, 90, 90, 0],       # At stack level (same height as pickup)
            'open': [90, 20, 50, 90, 90, 30],       # Open gripper at stack
            'left': [60, 20, 50, 90, 90, 30],       # Left side pickup
            'right': [120, 20, 50, 90, 90, 30],     # Right side pickup
            'high': [90, 45, 70, 90, 90, 30],        # Higher safe position
            'low': [90, 15, 45, 90, 90, 30],        # Lower position
            'approach': [90, 25, 55, 90, 90, 30],   # Approach from above
            'retract': [90, 30, 60, 90, 90, 30],    # Retract after placing
        }
        
    def initialize_robot(self):
        """Initialize robot connection"""
        print("🔧 Initializing robot...")
        try:
            self.robot = Arm_Device()
            time.sleep(0.1)
            print("✅ Robot connected")
            return True
        except Exception as e:
            print(f"❌ Robot failed: {e}")
            return False
    
    def move_to(self, angles, description=""):
        """Move robot to coordinates"""
        if description:
            print(f"🤖 {description}")
        print(f"   Moving to: {angles}")
        
        try:
            for i, angle in enumerate(angles):
                self.robot.Arm_serial_servo_write(i+1, int(angle), 2000)
                time.sleep(0.1)
            time.sleep(1)
            self.current_position = angles.copy()
            print("✅ Done")
            return True
        except Exception as e:
            print(f"❌ Failed: {e}")
            return False
    
    def test_position(self, name):
        """Test a predefined position"""
        if name not in self.positions:
            print(f"❌ Position '{name}' not found")
            print(f"Available: {', '.join(self.positions.keys())}")
            return False
        
        angles = self.positions[name]
        return self.move_to(angles, f"Testing {name}")
    
    def custom_position(self):
        """Set custom coordinates"""
        print("\n🎯 Custom Position")
        print("Enter 6 angles (0-180 each):")
        
        try:
            angles = []
            joint_names = ["Base", "Shoulder", "Elbow", "Wrist Rot", "Wrist Tilt", "Gripper"]
            
            for i, name in enumerate(joint_names):
                angle = int(input(f"Joint {i+1} ({name}): "))
                if 0 <= angle <= 180:
                    angles.append(angle)
                else:
                    print("❌ Must be 0-180")
                    return False
            
            print(f"Position: {angles}")
            if input("Move? (y/n): ").lower() == 'y':
                return self.move_to(angles, "Custom position")
            return False
                
        except (ValueError, KeyboardInterrupt):
            print("❌ Cancelled")
            return False
    
    def show_positions(self):
        """Show all positions"""
        print("\n📋 Available Positions:")
        for name, angles in self.positions.items():
            print(f"  {name:8}: {angles}")
    
    def run(self):
        """Main interactive loop"""
        print("\n🎯 Simple Coordinate Tester")
        print("Commands:")
        print("  h - Home")
        print("  c - Custom position")
        print("  <name> - Test position (pickup, grip, lift, etc.)")
        print("  list - Show positions")
        print("  p - Show current position")
        print("  q - Quit")
        
        while True:
            try:
                cmd = input(f"\nCommand: ").strip().lower()
                
                if cmd == 'q':
                    break
                elif cmd == 'h':
                    self.move_to(self.positions['home'], "Home")
                elif cmd == 'c':
                    self.custom_position()
                elif cmd == 'list':
                    self.show_positions()
                elif cmd == 'p':
                    print(f"Current: {self.current_position}")
                elif cmd in self.positions:
                    self.test_position(cmd)
                else:
                    print("❌ Unknown command")
                    
            except KeyboardInterrupt:
                print("\n👋 Exiting...")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

def main():
    """Main function"""
    print("🧪 Simple Coordinate Tester")
    print("Easy robot position testing")
    
    tester = SimpleCoordinateTester()
    
    if not tester.initialize_robot():
        return
    
    try:
        tester.move_to(tester.positions['home'], "Starting at home")
        tester.run()
    finally:
        tester.move_to(tester.positions['home'], "Returning to home")
        print("👋 Done")

if __name__ == "__main__":
    main()