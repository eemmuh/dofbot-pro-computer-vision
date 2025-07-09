# DOFBOT Pro Setup Guide

## Current Status
- ✅ DOFBOT detected at `/dev/ttyUSB0`
- ✅ Serial connection established
- ✅ Arduino IDE installed
- ❌ Firmware not loaded (robot not responding to commands)

## Step 1: Download DOFBOT Library

1. **Search for DOFBOT library:**
   - Visit: https://github.com/YahboomTechnology/DOFBOT
   - Or search: "DOFBOT Pro library GitHub"
   - Download the library ZIP file

2. **Install in Arduino IDE:**
   - Open Arduino IDE: `arduino`
   - Go to `Sketch` → `Include Library` → `Add .ZIP Library`
   - Select the downloaded DOFBOT library ZIP file

## Step 2: Upload Firmware

1. **Open DOFBOT example:**
   - In Arduino IDE, go to `File` → `Examples` → `DOFBOT` → `DOFBOT_Control`
   - Or find the main DOFBOT control sketch

2. **Select board and port:**
   - Board: Arduino Leonardo or Arduino Micro
   - Port: `/dev/ttyUSB0`

3. **Upload firmware:**
   - Click the upload button (→)
   - Wait for upload to complete

## Step 3: Test Connection

After uploading firmware, test the connection:

```bash
python3 test_dofbot_connection.py
```

## Step 4: Test Movement

Once connected, test basic movements:

```bash
python3 test_dofbot_movement.py
```

## Step 5: Run Full Demo

Run the complete cup stacking demo:

```bash
python3 demo_cup_stacking.py
```

## Troubleshooting

### If robot still doesn't respond:
1. **Check power**: Make sure DOFBOT is powered on
2. **Check mode**: Ensure robot is in operation mode (not programming mode)
3. **Check USB**: Try different USB ports
4. **Check firmware**: Re-upload the firmware

### Common Issues:
- **Permission denied**: Run `sudo usermod -a -G dialout $USER` and reboot
- **Port not found**: Check USB connection and power
- **Upload fails**: Try different USB cable or port

## Alternative: Manual Testing

If you want to test commands manually:

```bash
python3 test_dofbot_commands.py
```

Then type commands like:
- `HOME`
- `MOVE 150 150 150`
- `GRIPPER_OPEN`
- `GRIPPER_CLOSE`

## Next Steps After Setup

1. **Calibrate robot**: Set up proper coordinate system
2. **Test cup detection**: Run with camera to detect cups
3. **Adjust positions**: Modify stacking positions for your setup
4. **Fine-tune movements**: Adjust speeds and positions

## Files Created

- `test_dofbot_connection.py` - Test basic connection
- `test_dofbot_movement.py` - Test robot movements
- `test_dofbot_commands.py` - Test various commands
- `demo_cup_stacking.py` - Full cup stacking demo
- `setup_dofbot_firmware.py` - Setup helper script

## Support

If you continue having issues:
1. Check the DOFBOT official documentation
2. Look for LED indicators on the robot
3. Try different command protocols
4. Contact DOFBOT support with your specific model 