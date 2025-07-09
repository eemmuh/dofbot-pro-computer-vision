# Jetson DOFBOT Pro Setup Guide

## Understanding Your DOFBOT Pro

The DOFBOT Pro is a **Jetson-based robotic arm** that runs directly on your Jetson board. It does **NOT** use Arduino - the Jetson board directly controls the servos through a servo controller.

## Current Status
- ✅ DOFBOT detected at `/dev/ttyUSB0`
- ✅ Serial connection established
- ✅ Jetson-based controller created
- ❌ Need to determine servo communication protocol

## What You Need to Download

The actual DOFBOT code is in a Google Drive folder:
**Link**: https://drive.google.com/drive/folders/13Rp6BC_t_N1sBiD6OY1-aM88_jkhX6nn?usp=drive_link

### Steps to Get the Code:

1. **Visit the Google Drive link** above
2. **Download the DOFBOT code** (Python files for Jetson)
3. **Extract and copy** the servo control code to your project

## How DOFBOT Pro Works

```
Jetson Board → USB → Servo Controller → 6 Servos
```

- **Jetson Board**: Runs Python code to control the robot
- **USB Connection**: Communicates with servo controller
- **Servo Controller**: Converts commands to servo signals
- **6 Servos**: Move the robotic arm joints

## Testing Your Setup

### 1. Test Basic Connection
```bash
python3 test_jetson_dofbot.py
```

### 2. Test Movement Commands
```bash
python3 src/robot/jetson_dofbot_controller.py
```

### 3. Run Full Demo
```bash
python3 demo_cup_stacking.py
```

## Servo Communication Protocol

The current controller uses a **placeholder protocol**. You need to:

1. **Check the downloaded code** for the actual servo command format
2. **Update the command format** in `jetson_dofbot_controller.py`
3. **Test with your specific servo controller**

### Common Servo Protocols:
- **Maestro**: `#1P1500T1000\n` (servo 1, position 1500, time 1000ms)
- **Pololu**: `#1P1500T1000\n` (similar format)
- **Custom**: May use different command formats

## Files Created for You

- `src/robot/jetson_dofbot_controller.py` - Jetson-based DOFBOT controller
- `test_jetson_dofbot.py` - Test script for Jetson controller
- `demo_cup_stacking.py` - Updated demo with Jetson controller

## Next Steps

### 1. Download the Code
- Get the DOFBOT code from Google Drive
- Look for servo control examples

### 2. Identify Servo Protocol
- Check what servo controller your DOFBOT uses
- Find the command format in the downloaded code

### 3. Update Controller
- Modify `jetson_dofbot_controller.py` with correct protocol
- Test basic servo movements

### 4. Implement Inverse Kinematics
- Add proper IK calculations for 3D positioning
- Calibrate coordinate system

### 5. Test Cup Stacking
- Run the full demo with camera and robot

## Troubleshooting

### If servos don't move:
1. **Check servo controller**: Make sure it's powered and connected
2. **Verify command format**: Use the correct protocol for your controller
3. **Check servo IDs**: Ensure servo numbers match your setup
4. **Test individual servos**: Try moving one servo at a time

### If connection fails:
1. **Check USB connection**: Try different USB ports
2. **Verify permissions**: Run `sudo usermod -a -G dialout $USER`
3. **Check device**: Run `ls /dev/ttyUSB*` to see available ports

## Servo Controller Types

Your DOFBOT Pro likely uses one of these:
- **Maestro Servo Controller**
- **Pololu Servo Controller** 
- **Custom Yahboom Controller**

Check the downloaded code to identify which one you have.

## Coordinate System

The DOFBOT Pro uses:
- **X**: Left/Right movement
- **Y**: Forward/Backward movement  
- **Z**: Up/Down movement

You'll need to calibrate this for your specific setup.

## Support

If you need help:
1. Check the downloaded DOFBOT code examples
2. Look for servo controller documentation
3. Contact Yahboom support with your specific model
4. Check the DOFBOT Pro manual for your servo controller type 