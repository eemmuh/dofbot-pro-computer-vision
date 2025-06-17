# DOFBOT Pro Cup Stacking Project

This project implements an automated cup stacking system using the DOFBOT Pro robot arm. The system uses computer vision for cup detection and precise robotic control for stacking cups in a pyramid formation.

## Project Structure
```
cup-stacking-project/
├── requirements.txt
├── src/
│   ├── vision/
│   │   ├── __init__.py
│   │   ├── cup_detector.py
│   │   └── camera_interface.py
│   ├── robot/
│   │   ├── __init__.py
│   │   ├── dofbot_controller.py
│   │   └── gripper_control.py
│   └── main.py
└── README.md
```

## Setup Instructions

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Clone the Darknet repository for YOLO:
```bash
git clone https://github.com/hank-ai/darknet.git
cd darknet
make
```

3. Configure the DOFBOT Pro:
- Connect the robot arm to your computer via USB
- Ensure the correct port is set in the configuration
- Calibrate the robot arm before first use

## Usage

1. Run the main script:
```bash
python src/main.py
```

## Features
- Real-time cup detection using YOLO/Darknet
- Precise robotic arm control for cup manipulation
- Automated pyramid stacking sequence
- Return to initial stack configuration

## Requirements
- Python 3.7+
- OpenCV
- PyTorch
- DOFBOT Pro robot arm
- USB camera 