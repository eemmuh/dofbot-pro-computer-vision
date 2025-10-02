# DOFBot Pro Coordinate Reference

## Joint Angles Explained

The DOFBot Pro has 6 joints, each controlled by an angle from 0-180 degrees:

```
[Base, Shoulder, Elbow, Wrist_Rot, Wrist_Tilt, Gripper]
```

### Joint 1 - Base (0-180°)
- **0°** = Arm pointing left
- **90°** = Arm pointing straight ahead  
- **180°** = Arm pointing right

### Joint 2 - Shoulder (0-180°)
- **0-30°** = Arm very low (dangerous - avoid)
- **30-50°** = Arm at table level
- **50-80°** = Arm raised up
- **80-180°** = Arm very high

### Joint 3 - Elbow (0-180°)
- **0-30°** = Arm extended forward
- **30-60°** = Arm bent at 90°
- **60-120°** = Arm retracted
- **120-180°** = Arm very bent

### Joint 4 - Wrist Rotation (0-180°)
- **90°** = Neutral (recommended)
- **0°** = Wrist rotated left
- **180°** = Wrist rotated right

### Joint 5 - Wrist Tilt (0-180°)
- **90°** = Neutral (recommended)
- **0°** = Wrist tilted down
- **180°** = Wrist tilted up

### Joint 6 - Gripper (0-180°)
- **0°** = Gripper closed
- **30°** = Gripper open
- **60°** = Gripper very open

## Predefined Positions

### Safe Positions
```python
home = [90, 30, 40, 90, 90, 30]           # Safe home position
pickup_approach = [90, 35, 45, 90, 90, 30] # Above cup to pick up
pickup_grip = [90, 30, 35, 90, 90, 0]      # At cup level, gripper closed
pickup_lift = [90, 40, 50, 90, 90, 0]      # Lifted cup
stack_approach = [90, 40, 50, 90, 90, 0]   # Above stack position
stack_place = [90, 35, 40, 90, 90, 0]      # At stack level
stack_release = [90, 35, 40, 90, 90, 30]   # Open gripper
stack_lift = [90, 45, 55, 90, 90, 30]      # Lift away from stack
```

## Manual Control Commands

### Quick Commands
- `h` - Home position
- `p` - Pickup sequence (approach → grip → lift)
- `s` - Stack sequence (approach → place → release → lift)
- `f` - Full stacking sequence
- `c` - Set custom position
- `e` - Explain coordinates
- `l` - List predefined positions

### Custom Position Example
```
Joint 1 (Base): 90      # Straight ahead
Joint 2 (Shoulder): 35  # Slightly raised
Joint 3 (Elbow): 45    # Slightly bent
Joint 4 (Wrist Rot): 90 # Neutral
Joint 5 (Wrist Tilt): 90 # Neutral
Joint 6 (Gripper): 30   # Open
```

## Safety Guidelines

### ✅ Safe Ranges
- **Base**: 30-150° (avoid extreme rotations)
- **Shoulder**: 25-80° (avoid too low/high)
- **Elbow**: 30-120° (avoid overextension)
- **Wrist**: 90° (keep neutral)
- **Gripper**: 0-60° (open/close range)

### ❌ Avoid These
- Shoulder < 25° (too low - will hit table)
- Shoulder > 80° (too high - may hit ceiling)
- Elbow < 30° (overextended)
- Elbow > 120° (overbent)
- Base < 30° or > 150° (extreme rotations)

## Cup Stacking Workflow

1. **Home** → `[90, 30, 40, 90, 90, 30]`
2. **Pickup Approach** → `[90, 35, 45, 90, 90, 30]`
3. **Pickup Grip** → `[90, 30, 35, 90, 90, 0]`
4. **Pickup Lift** → `[90, 40, 50, 90, 90, 0]`
5. **Stack Approach** → `[90, 40, 50, 90, 90, 0]`
6. **Stack Place** → `[90, 35, 40, 90, 90, 0]`
7. **Stack Release** → `[90, 35, 40, 90, 90, 30]`
8. **Stack Lift** → `[90, 45, 55, 90, 90, 30]`
9. **Return Home** → `[90, 30, 40, 90, 90, 30]`

## Tips for Manual Control

1. **Start High**: Always approach from above
2. **Move Slowly**: Use slower speeds for precision
3. **Check Angles**: Ensure all angles are in safe ranges
4. **Test Positions**: Try positions step by step
5. **Emergency Home**: Always have a safe home position
6. **Gripper Control**: 0° = closed, 30° = open
7. **Height Control**: Shoulder angle controls height
8. **Reach Control**: Elbow angle controls reach