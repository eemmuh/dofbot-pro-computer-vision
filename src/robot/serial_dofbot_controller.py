#!/usr/bin/env python3
"""
Serial DOFBOT Pro Controller
Direct serial communication with DOFBOT Pro via USB
"""

import time
import serial
from typing import Tuple, List, Optional

class SerialDOFBOTController:
    def __init__(self, port='/dev/ttyUSB0', baudrate=1000000):
        """
        Initialize the serial DOFBOT controller.
        Communicates directly with DOFBOT via USB serial.
        """
        self.connected = False
        self.ser = None
        self.port = port
        self.baudrate = baudrate
        
        # Current servo positions (in degrees)
        self.current_positions = [90.0, 90.0, 90.0, 90.0, 90.0, 90.0]
        
        # Servo limits (in degrees)
        self.servo_limits = [
            (0.0, 180.0),    # Base rotation
            (0.0, 180.0),    # Shoulder
            (0.0, 180.0),    # Elbow
            (0.0, 180.0),    # Wrist rotation
            (0.0, 180.0),    # Wrist pitch
            (0.0, 180.0),    # Gripper
        ]
        
    def connect(self) -> bool:
        """Initialize serial connection to DOFBOT."""
        try:
            print(f"🔌 Connecting to DOFBOT via {self.port} at {self.baudrate} baud...")
            
            # Open serial connection
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            
            # Clear buffers
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
            time.sleep(1)
            
            # Test connection
            if self.test_connection():
                self.connected = True
                print("✅ Connected to DOFBOT via serial")
                
                # Initialize to home position
                self.initialize_servos()
                return True
            else:
                print("❌ Failed to communicate with DOFBOT")
                return False
                
        except Exception as e:
            print(f"❌ Failed to connect to DOFBOT: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from DOFBOT."""
        if self.connected and self.ser:
            try:
                self.ser.close()
                self.connected = False
                print("✅ Disconnected from DOFBOT")
            except Exception as e:
                print(f"❌ Error disconnecting: {e}")
    
    def test_connection(self) -> bool:
        """Test if DOFBOT is responding."""
        try:
            # Try to read servo positions
            for servo_id in range(1, 7):
                pos = self.read_servo_position(servo_id)
                if pos is not None:
                    print(f"✅ Servo {servo_id} responding: {pos}°")
                else:
                    print(f"❌ Servo {servo_id} not responding")
                    return False
            return True
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return False
    
    def send_command(self, command: str) -> bool:
        """Send a command to DOFBOT and wait for response."""
        if not self.connected or not self.ser:
            return False
            
        try:
            # Send command
            self.ser.write((command + '\n').encode())
            self.ser.flush()
            
            # Wait for response
            time.sleep(0.1)
            
            # Check for response
            if self.ser.in_waiting > 0:
                response = self.ser.read(self.ser.in_waiting).decode().strip()
                print(f"Response: {response}")
                return True
            else:
                return True  # No response expected for some commands
                
        except Exception as e:
            print(f"❌ Failed to send command: {e}")
            return False
    
    def read_servo_position(self, servo_id: int) -> Optional[float]:
        """Read servo position via serial."""
        if not self.connected or not self.ser:
            return None
            
        try:
            # Try different command formats
            commands = [
                f"#P{servo_id}",
                f"#{servo_id}P",
                f"READ{servo_id}",
                f"GET{servo_id}",
                f"STATUS{servo_id}"
            ]
            
            for cmd in commands:
                if self.send_command(cmd):
                    time.sleep(0.1)
                    if self.ser.in_waiting > 0:
                        response = self.ser.read(self.ser.in_waiting).decode().strip()
                        # Try to parse position from response
                        try:
                            # Look for numbers in response
                            import re
                            numbers = re.findall(r'\d+', response)
                            if numbers:
                                pos = float(numbers[0])
                                if 0 <= pos <= 180:
                                    return pos
                        except:
                            continue
            
            return None
            
        except Exception as e:
            print(f"❌ Failed to read servo {servo_id}: {e}")
            return None
    
    def move_servo(self, servo_id: int, angle_degrees: float, speed: int = 500):
        """
        Move a specific servo to an angle.
        
        Args:
            servo_id: Servo ID (1-6)
            angle_degrees: Target angle in degrees
            speed: Movement speed in milliseconds
        """
        if not self.connected:
            print("❌ Not connected to DOFBOT")
            return False
            
        if servo_id < 1 or servo_id > 6:
            print("❌ Servo ID must be between 1 and 6")
            return False
        
        # Clamp angle to servo limits
        min_angle, max_angle = self.servo_limits[servo_id - 1]
        angle_degrees = max(min_angle, min(max_angle, angle_degrees))
        
        print(f"🤖 Moving servo {servo_id} to {angle_degrees:.1f}° (speed: {speed}ms)")
        
        try:
            # Try different command formats for servo control
            commands = [
                f"#{servo_id}P{int(angle_degrees)}T{speed}",
                f"#P{servo_id}{int(angle_degrees)}T{speed}",
                f"SERVO{servo_id}{int(angle_degrees)}",
                f"MOVE{servo_id}{int(angle_degrees)}",
                f"#{servo_id}P{int(angle_degrees)}"
            ]
            
            success = False
            for cmd in commands:
                if self.send_command(cmd):
                    success = True
                    break
            
            if success:
                # Update current position
                self.current_positions[servo_id - 1] = angle_degrees
                print(f"✅ Servo {servo_id} command sent successfully")
                return True
            else:
                print(f"❌ Failed to send command to servo {servo_id}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to move servo {servo_id}: {e}")
            return False
    
    def move_all_servos(self, angles_degrees: List[float], speed: int = 500):
        """
        Move all servos to specified angles.
        
        Args:
            angles_degrees: List of 6 angles in degrees
            speed: Movement speed in milliseconds
        """
        if len(angles_degrees) != 6:
            print("❌ Must provide exactly 6 angles")
            return False
            
        if not self.connected:
            print("❌ Not connected to DOFBOT")
            return False
        
        print(f"🤖 Moving all servos to angles: {angles_degrees}")
        
        try:
            # Clamp angles to servo limits
            clamped_angles = []
            for i, angle in enumerate(angles_degrees):
                min_angle, max_angle = self.servo_limits[i]
                clamped_angles.append(max(min_angle, min(max_angle, angle)))
            
            # Try different command formats for all servos
            angle_str = ''.join([f"{int(angle):03d}" for angle in clamped_angles])
            commands = [
                f"#0P{angle_str}T{speed}",
                f"#P{angle_str}T{speed}",
                f"ALL{angle_str}",
                f"MOVE{angle_str}"
            ]
            
            success = False
            for cmd in commands:
                if self.send_command(cmd):
                    success = True
                    break
            
            if success:
                # Update current positions
                self.current_positions = clamped_angles.copy()
                print("✅ All servos command sent successfully")
                return True
            else:
                print("❌ Failed to send command to all servos")
                return False
                
        except Exception as e:
            print(f"❌ Failed to move servos: {e}")
            return False
    
    def initialize_servos(self):
        """Initialize all servos to default positions."""
        if not self.connected:
            return
            
        print("🔧 Initializing servos to default positions...")
        home_angles = [90.0, 90.0, 90.0, 90.0, 90.0, 90.0]  # Home position
        self.move_all_servos(home_angles)
        time.sleep(2)
        print("✅ Servos initialized")
    
    def home_position(self):
        """Move to home position."""
        home_angles = [90.0, 90.0, 90.0, 90.0, 90.0, 90.0]
        print("🏠 Moving to home position...")
        return self.move_all_servos(home_angles)
    
    def open_gripper(self):
        """Open the gripper (servo 6)."""
        print("🤏 Opening gripper...")
        return self.move_servo(6, 180.0)  # Open position
    
    def close_gripper(self):
        """Close the gripper (servo 6)."""
        print("🤏 Closing gripper...")
        return self.move_servo(6, 0.0)  # Closed position
    
    def get_current_positions(self) -> List[float]:
        """Get current servo positions in degrees."""
        return self.current_positions.copy()

if __name__ == "__main__":
    print("🤖 Testing Serial DOFBOT Controller...")
    robot = SerialDOFBOTController()
    
    if robot.connect():
        print("✅ Connection test successful!")
        
        # Test basic movements
        print("\n🧪 Testing basic movements...")
        robot.home_position()
        time.sleep(2)
        
        robot.open_gripper()
        time.sleep(1)
        
        robot.close_gripper()
        time.sleep(1)
        
        # Test individual servo movements
        print("\n🧪 Testing individual servo movements...")
        for servo_id in range(1, 7):
            print(f"Testing servo {servo_id}...")
            robot.move_servo(servo_id, 45.0)
            time.sleep(1)
            robot.move_servo(servo_id, 135.0)
            time.sleep(1)
            robot.move_servo(servo_id, 90.0)
            time.sleep(1)
        
        robot.disconnect()
    else:
        print("❌ Connection test failed.") 