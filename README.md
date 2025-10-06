# DOFBOT Pro Cup Stacking & Sorting Robot

A complete robot control system for the DOFBOT Pro arm featuring cup stacking, sorting, and manual control capabilities.

## Features

- **Cup Stacking**: Pyramid and tower formation with YOLO detection
- **Cup Sorting**: 5 intelligent sorting strategies across 3 zones
- **Manual Control**: Precise coordinate control with gripper optimization
- **Real-time Processing**: Live camera feed with multi-threading
- **Optimized**: Clean project structure with essential dependencies only

## Quick Start

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Or with UV (faster)
uv pip install -r requirements.txt
```

### Run Systems
```bash
# Manual robot control
python3 manual_coordinate_control.py

# Cup sorting system
python3 realtime_cup_sorting_improved.py

# Cup stacking algorithm
python3 src/robot/fixed_cup_stacking_algorithm.py

# Interactive notebook
jupyter notebook cup_stacking_algorithm.ipynb
```

## Cup Sorting Controls

**Sorting Strategies:**
- `1` - Position-based (left/center/right)
- `2` - Distance-based (closest to center first)
- `3` - Pattern-based (alternating zones)
- `4` - Random sorting
- `5` - Capacity-based (balance zones)
- `r` - Reset counts
- `q` - Quit

## System Requirements

- **Hardware**: DOFBOT Pro robot arm, USB camera, Jetson Orin NX
- **Software**: Python 3.8+, OpenCV, YOLO, Arm_Lib
- **Dependencies**: 7 essential packages (optimized from 30)

## Troubleshooting

```bash
# Check camera
ls -la /dev/video*

# Check robot connection
lsusb | grep DOFBOT

# Verify YOLO model
ls -la backup/yolo-cup-*.weights
```

## Documentation

- `CUP_SORTING_GUIDE.md` - Complete sorting guide
- `COORDINATE_REFERENCE.md` - Robot coordinates
- `cup_stacking_algorithm.ipynb` - Interactive notebook






