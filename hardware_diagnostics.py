#!/usr/bin/env python3
"""
DOFBOT Pro Hardware Diagnostics
Comprehensive hardware testing for power, I2C, and servo controller
"""

import os
import time
import subprocess
import smbus

def run_command(cmd):
    """Run a command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "", "Command timed out", -1

def check_system_info():
    """Check system information"""
    print("🔍 SYSTEM INFORMATION")
    print("=" * 50)
    
    # Check OS and hardware
    stdout, stderr, code = run_command("uname -a")
    if code == 0:
        print(f"✅ OS: {stdout}")
    
    # Check CPU info
    stdout, stderr, code = run_command("cat /proc/cpuinfo | grep 'Model name' | head -1")
    if code == 0 and ':' in stdout:
        print(f"✅ CPU: {stdout.split(':')[1].strip()}")
    elif code == 0:
        print(f"✅ CPU: {stdout}")
    
    # Check memory
    stdout, stderr, code = run_command("free -h | grep 'Mem:'")
    if code == 0:
        print(f"✅ Memory: {stdout}")

def check_i2c_buses():
    """Check available I2C buses"""
    print("\n🔍 I2C BUS DETECTION")
    print("=" * 50)
    
    # Check if i2c-tools is installed
    stdout, stderr, code = run_command("which i2cdetect")
    if code != 0:
        print("❌ i2c-tools not installed. Installing...")
        run_command("sudo apt update && sudo apt install -y i2c-tools")
    
    # Find all I2C buses
    stdout, stderr, code = run_command("ls /dev/i2c-* 2>/dev/null")
    if code == 0:
        buses = stdout.split('\n')
        print(f"✅ Found I2C buses: {buses}")
        
        # Scan each bus
        for bus in buses:
            if bus.strip():
                bus_num = bus.split('-')[1]
                print(f"\n📡 Scanning I2C bus {bus_num}:")
                stdout, stderr, code = run_command(f"i2cdetect -y {bus_num}")
                if code == 0:
                    print(stdout)
                else:
                    print(f"❌ Failed to scan bus {bus_num}: {stderr}")
    else:
        print("❌ No I2C buses found")

def check_i2c_communication():
    """Test I2C communication with found devices"""
    print("\n🔍 I2C COMMUNICATION TEST")
    print("=" * 50)
    
    # Test communication with devices on bus 0
    devices = [0x30, 0x50, 0x57]
    
    try:
        bus = smbus.SMBus(0)
        print("✅ Successfully opened I2C bus 0")
        
        for addr in devices:
            print(f"\n📡 Testing device at address 0x{addr:02x}:")
            
            # Try to read a byte
            try:
                data = bus.read_byte_data(addr, 0x00)
                print(f"  ✅ Read successful: 0x{data:02x}")
            except Exception as e:
                print(f"  ❌ Read failed: {e}")
            
            # Try to write a byte
            try:
                bus.write_byte_data(addr, 0x00, 0x00)
                print(f"  ✅ Write successful")
            except Exception as e:
                print(f"  ❌ Write failed: {e}")
        
        bus.close()
        
    except Exception as e:
        print(f"❌ Failed to open I2C bus 0: {e}")

def check_servo_power():
    """Check servo power supply"""
    print("\n🔍 SERVO POWER CHECK")
    print("=" * 50)
    
    # Check USB power
    stdout, stderr, code = run_command("lsusb")
    if code == 0:
        print("✅ USB devices:")
        for line in stdout.split('\n'):
            if line.strip():
                print(f"  {line}")
    
    # Check if DOFBOT is connected via USB
    stdout, stderr, code = run_command("lsusb | grep -i yahboom")
    if code == 0:
        print(f"✅ DOFBOT detected via USB: {stdout}")
    else:
        print("⚠️  No Yahboom device found in USB list")
    
    # Check GPIO power (if applicable)
    stdout, stderr, code = run_command("ls /sys/class/gpio/ 2>/dev/null")
    if code == 0:
        print("✅ GPIO available")
    else:
        print("❌ GPIO not available")

def check_servo_controller():
    """Test servo controller specifically"""
    print("\n🔍 SERVO CONTROLLER TEST")
    print("=" * 50)
    
    # Test different I2C addresses with servo commands
    addresses = [0x50, 0x57, 0x30]
    
    try:
        bus = smbus.SMBus(0)
        
        for addr in addresses:
            print(f"\n🤖 Testing servo controller at 0x{addr:02x}:")
            
            # Test servo 1 position command
            test_commands = [
                # Format 1: [servo_id, pos_H, pos_L, time_H, time_L]
                [1, 0x08, 0x00, 0x03, 0xE8],  # Servo 1 to 90 degrees, 1000ms
                # Format 2: [0x10 + servo_id, pos_H, pos_L, time_H, time_L]
                [0x11, 0x08, 0x00, 0x03, 0xE8],
                # Format 3: [0x19, servo_id, pos_H, pos_L, time_H, time_L]
                [0x19, 1, 0x08, 0x00, 0x03, 0xE8],
            ]
            
            for i, cmd in enumerate(test_commands):
                try:
                    print(f"  Testing command format {i+1}...")
                    if i == 2:  # Format 3 has different structure
                        bus.write_i2c_block_data(addr, cmd[0], cmd[1:])
                    else:
                        bus.write_i2c_block_data(addr, cmd[0], cmd[1:])
                    
                    print(f"    ✅ Command sent successfully")
                    time.sleep(0.1)
                    
                    # Ask user if they saw movement
                    response = input(f"    Did servo 1 move? (y/n): ")
                    if response.lower() == 'y':
                        print(f"    🎉 SUCCESS! Servo controller at 0x{addr:02x} works!")
                        bus.close()
                        return True
                    
                except Exception as e:
                    print(f"    ❌ Command failed: {e}")
                    continue
        
        bus.close()
        print("❌ No servo movement detected from any address")
        return False
        
    except Exception as e:
        print(f"❌ Failed to test servo controller: {e}")
        return False

def check_arm_lib_connection():
    """Test Arm_Lib connection"""
    print("\n🔍 ARM_LIB CONNECTION TEST")
    print("=" * 50)
    
    try:
        import sys
        sys.path.append('/home/jetson/software/Arm_Lib')
        from Arm_Lib import Arm_Device
        
        # Test different buses
        for bus in [0, 1, 7]:
            try:
                print(f"Testing Arm_Lib on bus {bus}...")
                arm = Arm_Device(bus)
                
                # Try to read servo position
                pos = arm.Arm_serial_servo_read(1)
                if pos is not None:
                    print(f"  ✅ Arm_Lib connected on bus {bus}, servo 1 position: {pos}°")
                    
                    # Try to move servo
                    arm.Arm_serial_servo_write(1, 90, 1000)
                    print(f"  ✅ Command sent to servo 1")
                    
                    response = input(f"  Did servo 1 move? (y/n): ")
                    if response.lower() == 'y':
                        print(f"  🎉 SUCCESS! Arm_Lib works on bus {bus}!")
                        return True
                else:
                    print(f"  ❌ Arm_Lib connected but can't read servo position")
                    
            except Exception as e:
                print(f"  ❌ Arm_Lib failed on bus {bus}: {e}")
                continue
        
        print("❌ Arm_Lib not working on any bus")
        return False
        
    except ImportError:
        print("❌ Arm_Lib not found")
        return False

def check_yahboom_arm_app():
    """Check YahboomArm app status"""
    print("\n🔍 YAHBOOM ARM APP STATUS")
    print("=" * 50)
    
    # Check if app is running
    stdout, stderr, code = run_command("ps aux | grep YahboomArm")
    if code == 0:
        print("✅ YahboomArm app is running:")
        for line in stdout.split('\n'):
            if 'YahboomArm' in line and 'grep' not in line:
                print(f"  {line}")
    else:
        print("❌ YahboomArm app not running")
    
    # Check web interface
    stdout, stderr, code = run_command("curl -s -o /dev/null -w '%{http_code}' http://localhost:6500")
    if code == 0 and stdout == "200":
        print("✅ Web interface accessible")
    else:
        print("❌ Web interface not accessible")
    
    # Check TCP server
    stdout, stderr, code = run_command("netstat -tlnp | grep 6000")
    if code == 0:
        print("✅ TCP server running on port 6000")
    else:
        print("❌ TCP server not running")

def main():
    """Run all hardware diagnostics"""
    print("🔧 DOFBOT Pro Hardware Diagnostics")
    print("=" * 60)
    print("This will test power, I2C connections, and servo controller")
    print()
    
    # Run all diagnostic tests
    check_system_info()
    check_i2c_buses()
    check_i2c_communication()
    check_servo_power()
    check_servo_controller()
    check_arm_lib_connection()
    check_yahboom_arm_app()
    
    print("\n🎯 DIAGNOSTIC SUMMARY")
    print("=" * 60)
    print("Based on the tests above, here are the likely issues:")
    print()
    print("1. If I2C devices are found but servo controller fails:")
    print("   → Hardware power issue or wrong command protocol")
    print()
    print("2. If no I2C devices are found:")
    print("   → Hardware connection issue or wrong bus")
    print()
    print("3. If Arm_Lib connects but servos don't move:")
    print("   → Wrong I2C address or servo power issue")
    print()
    print("4. If YahboomArm app works but Python doesn't:")
    print("   → Protocol mismatch or permission issue")
    print()
    
    response = input("Would you like to try a specific fix based on the results? (y/n): ")
    if response.lower() == 'y':
        print("\nPlease tell me what issues were found and I'll help fix them!")

if __name__ == "__main__":
    main() 