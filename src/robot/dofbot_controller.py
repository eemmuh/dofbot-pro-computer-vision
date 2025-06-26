import serial
import time
from typing import Tuple, List, Optional
import numpy as np
import glob

class DOFBOTController:
    def __init__(self, port: Optional[str] = None, baudrate: int = 115200):
        """
        Initialize the DOFBOT controller.
        
        Args:
            port: Serial port for DOFBOT communication (auto-detect if None)
            baudrate: Baud rate for serial communication
        """
        self.port = port
        self.baudrate = baudrate
        self.serial: Optional[serial.Serial] = None
        self.connected = False
        
        # Auto-detect DOFBOT port if not specified
        if self.port is None:
            self.port = self._find_dofbot_port()
        
    def _find_dofbot_port(self) -> str:
        """Find the DOFBOT serial port automatically."""
        # Common DOFBOT ports in order of preference
        dofbot_ports = [
            '/dev/ttyUSB0',    # Most common for USB DOFBOTs
            '/dev/ttyACM0',    # Arduino-based DOFBOTs
            '/dev/ttyUSB1',    # Alternative USB port
            '/dev/ttyACM1',    # Alternative ACM port
        ]
        
        # Check which ports exist
        available_ports = []
        for port in dofbot_ports:
            if glob.glob(port):
                available_ports.append(port)
        
        if available_ports:
            print(f"Found potential DOFBOT ports: {available_ports}")
            return available_ports[0]
        else:
            print("⚠️  No common DOFBOT ports found. Using default /dev/ttyUSB0")
            return '/dev/ttyUSB0'
        
    def connect(self) -> bool:
        """Connect to the DOFBOT."""
        try:
            print(f"Attempting to connect to DOFBOT on {self.port}...")
            self.serial = serial.Serial(self.port, self.baudrate, timeout=1)
            self.connected = True
            print(f"✅ Connected to DOFBOT on {self.port}")
            
            # Test if it's actually a DOFBOT by sending a test command
            if self._test_dofbot_connection():
                print("✅ DOFBOT is responding to commands")
                return True
            else:
                print("⚠️  Connected to serial port but DOFBOT not responding")
                print("   This might not be a DOFBOT or it's not powered on")
                self.disconnect()
                return False
                
        except Exception as e:
            print(f"❌ Failed to connect to DOFBOT: {e}")
            return False
    
    def _test_dofbot_connection(self) -> bool:
        """Test if the connected device is actually a DOFBOT."""
        try:
            if not self.serial:
                return False
                
            # Send a simple status command
            self.send_command("STATUS")
            time.sleep(0.5)
            
            # Try to read response
            if self.serial.in_waiting > 0:
                response = self.read_response()
                print(f"DOFBOT response: {response}")
                return True
            else:
                # Try a different command
                self.send_command("HOME")
                time.sleep(0.5)
                if self.serial.in_waiting > 0:
                    response = self.read_response()
                    print(f"DOFBOT response: {response}")
                    return True
                else:
                    return False
        except Exception as e:
            print(f"Error testing DOFBOT connection: {e}")
            return False
            
    def disconnect(self):
        """Disconnect from the DOFBOT."""
        if self.serial and self.serial.is_open:
            self.serial.close()
            self.connected = False
            print("Disconnected from DOFBOT")
            
    def send_command(self, command: str) -> bool:
        """Send a command to the DOFBOT."""
        if not self.connected or not self.serial:
            print("Not connected to DOFBOT")
            return False
            
        try:
            # Add newline to command
            full_command = command + '\n'
            self.serial.write(full_command.encode())
            self.serial.flush()
            return True
        except Exception as e:
            print(f"Failed to send command: {e}")
            return False
    
    def read_response(self, timeout: float = 1.0) -> str:
        """Read response from DOFBOT."""
        if not self.connected or not self.serial:
            return ""
            
        try:
            self.serial.timeout = timeout
            response = self.serial.readline().decode().strip()
            return response
        except Exception as e:
            print(f"Failed to read response: {e}")
            return ""
        
    def move_to_position(self, x: float, y: float, z: float):
        """
        Move the end effector to the specified position.
        
        Args:
            x: X coordinate
            y: Y coordinate
            z: Z coordinate
        """
        if not self.connected:
            print("Not connected to DOFBOT")
            return False
            
        # DOFBOT position command format: MOVE x y z
        command = f"MOVE {x:.2f} {y:.2f} {z:.2f}"
        print(f"Sending position command: {command}")
        
        success = self.send_command(command)
        if success:
            # Wait for movement to complete
            time.sleep(2)
            response = self.read_response()
            if response:
                print(f"DOFBOT response: {response}")
        
        return success
        
    def open_gripper(self):
        """Open the gripper."""
        if not self.connected:
            print("Not connected to DOFBOT")
            return False
            
        print("Opening gripper...")
        command = "GRIPPER_OPEN"
        success = self.send_command(command)
        
        if success:
            time.sleep(1)
            response = self.read_response()
            if response:
                print(f"Gripper response: {response}")
        
        return success
        
    def close_gripper(self):
        """Close the gripper."""
        if not self.connected:
            print("Not connected to DOFBOT")
            return False
            
        print("Closing gripper...")
        command = "GRIPPER_CLOSE"
        success = self.send_command(command)
        
        if success:
            time.sleep(1)
            response = self.read_response()
            if response:
                print(f"Gripper response: {response}")
        
        return success
    
    def move_joint(self, joint_id: int, angle: float):
        """
        Move a specific joint to an angle.
        
        Args:
            joint_id: Joint number (1-6)
            angle: Target angle in degrees
        """
        if not self.connected:
            print("Not connected to DOFBOT")
            return False
            
        if joint_id < 1 or joint_id > 6:
            print("Joint ID must be between 1 and 6")
            return False
            
        print(f"Moving joint {joint_id} to {angle} degrees...")
        command = f"JOINT {joint_id} {angle:.2f}"
        success = self.send_command(command)
        
        if success:
            time.sleep(1)
            response = self.read_response()
            if response:
                print(f"Joint response: {response}")
        
        return success
    
    def home_position(self):
        """Move to home position."""
        if not self.connected:
            print("Not connected to DOFBOT")
            return False
            
        print("Moving to home position...")
        command = "HOME"
        success = self.send_command(command)
        
        if success:
            time.sleep(3)
            response = self.read_response()
            if response:
                print(f"Home response: {response}")
        
        return success
        
    def execute_stack_sequence(self, cup_positions: List[Tuple[float, float, float]]):
        """
        Execute the cup stacking sequence.
        
        Args:
            cup_positions: List of cup positions to stack
        """
        if not self.connected:
            print("Not connected to DOFBOT")
            return False
            
        print(f"Executing stacking sequence for {len(cup_positions)} cups...")
        
        # Move to home position first
        self.home_position()
        
        for i, (x, y, z) in enumerate(cup_positions):
            print(f"Stacking cup {i+1}/{len(cup_positions)} at position ({x}, {y}, {z})")
            
            # Move to cup position
            self.move_to_position(x, y, z + 10)  # Approach from above
            time.sleep(1)
            
            # Open gripper
            self.open_gripper()
            time.sleep(0.5)
            
            # Move down to cup
            self.move_to_position(x, y, z)
            time.sleep(1)
            
            # Close gripper to grab cup
            self.close_gripper()
            time.sleep(1)
            
            # Lift cup
            self.move_to_position(x, y, z + 50)
            time.sleep(1)
            
            # Move to stack position (you'll need to define this)
            stack_x, stack_y, stack_z = 150, 150, 50  # Example stack position
            self.move_to_position(stack_x, stack_y, stack_z + 50)
            time.sleep(1)
            
            # Lower to stack
            self.move_to_position(stack_x, stack_y, stack_z)
            time.sleep(1)
            
            # Release cup
            self.open_gripper()
            time.sleep(0.5)
            
            # Move up
            self.move_to_position(stack_x, stack_y, stack_z + 50)
            time.sleep(1)
        
        # Return to home position
        self.home_position()
        print("Stacking sequence completed!")
        
        return True 