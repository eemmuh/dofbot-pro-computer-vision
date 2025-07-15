#!/usr/bin/env python3
"""
DOFBOT Pro Direct Serial Controller
Direct USB serial communication with DOFBOT Pro hardware
"""

import serial
import time
import threading
from typing import Tuple, List, Optional
import numpy as np

class DOFBOTProDirectSerial:
    def __init__(self, port='/dev/ttyUSB0', baudrate=115200):
        """
        Initialize DOFBOT Pro direct serial controller.
        
        Args:
            port: Serial port (default: /dev/ttyUSB0)
            baudrate: Baud rate (default: 115200)
        """
        self.port = port
        self.baudrate = baudrate
        self.serial_conn = None
        self.connected = False
        
        # Current joint positions (in degrees)
        self.current_positions = [90.0, 90.0, 90.0, 90.0, 90.0, 30.0]  # DOFBOT Pro default
        
        # Joint limits (in degrees) - DOFBOT Pro specific
        self.joint_limits = [
            (0, 180),    # Base rotation
            (0, 180),    # Shoulder
            (0, 180),    # Elbow
            (0, 180),    # Wrist rotation
            (0, 180),    # Wrist pitch
            (30, 180),   # Gripper (30-180 for DOFBOT Pro)
        ]
        
    def connect(self) -> bool:
        """Connect to DOFBOT Pro via serial."""
        try:
            print(f"🔌 Connecting to DOFBOT Pro on {self.port}...")
            
            # Open serial connection
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            
            if self.serial_conn.is_open:
                self.connected = True
                print("✅ Connected to DOFBOT Pro via serial")
                
                # Initialize to home position
                self.home_position()
                return True
            else:
                print("❌ Failed to open serial connection")
                return False
                
        except Exception as e:
            print(f"❌ Failed to connect to DOFBOT Pro: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from DOFBOT Pro."""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            self.connected = False
            print("🔌 Disconnected from DOFBOT Pro")
    
    def send_command(self, command: str) -> Optional[str]:
        """Send command to DOFBOT Pro and get response."""
        if not self.connected or not self.serial_conn:
            print("❌ Not connected to DOFBOT Pro")
            return None
            
        try:
            # Clear input buffer
            self.serial_conn.reset_input_buffer()
            
            # Send command
            command_bytes = command.encode('utf-8')
            self.serial_conn.write(command_bytes)
            self.serial_conn.flush()
            
            # Wait for response
            time.sleep(0.1)
            
            # Read response
            if self.serial_conn.in_waiting > 0:
                response = self.serial_conn.readline().decode('utf-8').strip()
                return response
            
            return None
            
        except Exception as e:
            print(f"❌ Error sending command: {e}")
            return None
    
    def move_servo(self, servo_id: int, angle_degrees: float, time_ms: int = 1000) -> bool:
        """
        Move a specific servo to an angle.
        
        Args:
            servo_id: Servo ID (1-6)
            angle_degrees: Target angle in degrees
            time_ms: Movement time in milliseconds
        """
        if not self.connected:
            print("❌ Not connected to DOFBOT Pro")
            return False
            
        if servo_id < 1 or servo_id > 6:
            print("❌ Servo ID must be between 1 and 6")
            return False
        
        # Clamp angle to joint limits
        min_angle, max_angle = self.joint_limits[servo_id - 1]
        angle_degrees = max(min_angle, min(max_angle, angle_degrees))
        
        print(f"🤖 Moving servo {servo_id} to {angle_degrees:.1f}°")
        
        try:
            # Try different command formats for DOFBOT Pro
            commands_to_try = [
                f"#{servo_id:03d}P{int(angle_degrees):03d}T{time_ms:04d}\r\n",
                f"#{servo_id}P{int(angle_degrees)}T{time_ms}\r\n",
                f"#{servo_id:03d}P{int(angle_degrees):03d}\r\n",
                f"#{servo_id}P{int(angle_degrees)}\r\n"
            ]
            
            for command in commands_to_try:
                response = self.send_command(command)
                if response:
                    print(f"✅ Command sent: {command.strip()}")
                    # Update current position
                    self.current_positions[servo_id - 1] = angle_degrees
                    print(f"✅ Servo {servo_id} moved successfully")
                    return True
            
            print(f"❌ Failed to move servo {servo_id} with any command format")
            return False
                
        except Exception as e:
            print(f"❌ Failed to move servo {servo_id}: {e}")
            return False
    
    def move_all_servos(self, angles_degrees: List[float], time_ms: int = 2000) -> bool:
        """
        Move all servos to specified angles.
        
        Args:
            angles_degrees: List of 6 angles in degrees
            time_ms: Movement time in milliseconds
        """
        if len(angles_degrees) != 6:
            print("❌ Must provide exactly 6 angles")
            return False
            
        if not self.connected:
            print("❌ Not connected to DOFBOT Pro")
            return False
        
        print(f"🤖 Moving all servos to angles: {angles_degrees}")
        
        try:
            # Clamp angles to joint limits
            clamped_angles = []
            for i, angle in enumerate(angles_degrees):
                min_angle, max_angle = self.joint_limits[i]
                clamped_angles.append(max(min_angle, min(max_angle, angle)))
            
            # Try different command formats for all servos
            commands_to_try = [
                f"#000P{int(clamped_angles[0]):03d}P{int(clamped_angles[1]):03d}P{int(clamped_angles[2]):03d}P{int(clamped_angles[3]):03d}P{int(clamped_angles[4]):03d}P{int(clamped_angles[5]):03d}T{time_ms:04d}\r\n",
                f"#000P{int(clamped_angles[0])}P{int(clamped_angles[1])}P{int(clamped_angles[2])}P{int(clamped_angles[3])}P{int(clamped_angles[4])}P{int(clamped_angles[5])}T{time_ms}\r\n",
                f"#000P{int(clamped_angles[0]):03d}P{int(clamped_angles[1]):03d}P{int(clamped_angles[2]):03d}P{int(clamped_angles[3]):03d}P{int(clamped_angles[4]):03d}P{int(clamped_angles[5]):03d}\r\n"
            ]
            
            for command in commands_to_try:
                response = self.send_command(command)
                if response:
                    print(f"✅ Command sent: {command.strip()}")
                    # Update current positions
                    self.current_positions = clamped_angles.copy()
                    print("✅ All servos moved successfully")
                    return True
            
            print("❌ Failed to move servos with any command format")
            return False
                
        except Exception as e:
            print(f"❌ Failed to move servos: {e}")
            return False
    
    def home_position(self) -> bool:
        """Move to home position."""
        print("🏠 Moving to home position...")
        home_angles = [90.0, 90.0, 90.0, 90.0, 90.0, 30.0]  # DOFBOT Pro home
        return self.move_all_servos(home_angles, 3000)
    
    def open_gripper(self) -> bool:
        """Open the gripper (servo 6)."""
        print("🤏 Opening gripper...")
        return self.move_servo(6, 180.0, 1000)  # Open position
    
    def close_gripper(self) -> bool:
        """Close the gripper (servo 6)."""
        print("🤏 Closing gripper...")
        return self.move_servo(6, 30.0, 1000)  # Closed position
    
    def read_servo_position(self, servo_id: int) -> Optional[float]:
        """Read current position of a servo."""
        if not self.connected:
            return None
            
        try:
            # Try different read command formats
            commands_to_try = [
                f"#{servo_id:03d}PRAD\r\n",
                f"#{servo_id}PRAD\r\n",
                f"#{servo_id:03d}READ\r\n",
                f"#{servo_id}READ\r\n"
            ]
            
            for command in commands_to_try:
                response = self.send_command(command)
                if response and ('P' in response or 'READ' in response):
                    # Try to parse response
                    try:
                        if 'P' in response:
                            parts = response.split('P')
                            if len(parts) >= 2:
                                angle_str = parts[1][:3]  # Get first 3 digits
                                angle = float(angle_str)
                                self.current_positions[servo_id - 1] = angle
                                return angle
                        elif 'READ' in response:
                            # Try to extract angle from READ response
                            import re
                            numbers = re.findall(r'\d+', response)
                            if numbers:
                                angle = float(numbers[0])
                                self.current_positions[servo_id - 1] = angle
                                return angle
                    except:
                        continue
            
            return None
            
        except Exception as e:
            print(f"❌ Failed to read servo {servo_id}: {e}")
            return None
    
    def read_all_positions(self) -> Optional[List[float]]:
        """Read current positions of all servos."""
        if not self.connected:
            return None
            
        try:
            # Try different read all command formats
            commands_to_try = [
                "#000PRAD\r\n",
                "#000READ\r\n",
                "#000PREAD\r\n"
            ]
            
            for command in commands_to_try:
                response = self.send_command(command)
                if response:
                    try:
                        # Try to parse response
                        if 'P' in response:
                            parts = response.split('P')
                            if len(parts) >= 7:
                                positions = []
                                for i in range(1, 7):  # Skip first part (command)
                                    angle_str = parts[i][:3]  # Get first 3 digits
                                    positions.append(float(angle_str))
                                
                                self.current_positions = positions
                                return positions
                        elif 'READ' in response:
                            # Try to extract angles from READ response
                            import re
                            numbers = re.findall(r'\d+', response)
                            if len(numbers) >= 6:
                                positions = [float(num) for num in numbers[:6]]
                                self.current_positions = positions
                                return positions
                    except:
                        continue
            
            return None
            
        except Exception as e:
            print(f"❌ Failed to read positions: {e}")
            return None
    
    def get_current_positions(self) -> List[float]:
        """Get current joint positions in degrees."""
        return self.current_positions.copy()
    
    def test_connection(self) -> bool:
        """Test the connection by reading servo positions."""
        if not self.connected:
            return False
            
        print("🧪 Testing connection...")
        
        # Try to read positions
        positions = self.read_all_positions()
        if positions:
            print(f"✅ Current positions: {positions}")
            return True
        
        # Try reading individual servos
        for i in range(1, 7):
            pos = self.read_servo_position(i)
            if pos is not None:
                print(f"✅ Servo {i} position: {pos}°")
                return True
        
        print("❌ Failed to read any positions")
        return False
    
    def test_movement(self) -> bool:
        """Test basic movements."""
        if not self.connected:
            return False
            
        print("🧪 Testing movements...")
        
        # Test home position
        if self.home_position():
            time.sleep(3)
            
            # Test gripper
            if self.open_gripper():
                time.sleep(2)
                if self.close_gripper():
                    time.sleep(2)
                    
                    # Test individual servo
                    if self.move_servo(1, 120.0):
                        time.sleep(2)
                        if self.move_servo(1, 90.0):
                            print("✅ All movement tests passed!")
                            return True
        
        print("❌ Movement tests failed")
        return False

if __name__ == "__main__":
    print("🤖 Testing DOFBOT Pro Direct Serial Controller...")
    robot = DOFBOTProDirectSerial()
        
    if robot.connect():
        print("✅ Connection test successful!")
        
        # Test reading positions
        robot.test_connection()
        
        # Test movements
        robot.test_movement()
        
        robot.disconnect()
    else:
        print("❌ Connection test failed.") 