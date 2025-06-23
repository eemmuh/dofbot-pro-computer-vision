# DOFBOT Pro Cup Stacking Project

This project implements an automated cup stacking system using the DOFBOT Pro robot arm. The system uses computer vision for cup detection and precise robotic control for stacking cups in a pyramid formation.

## Project Structure
```
cup-stacking-project/
├── dataset/
│   ├── images/          # Cup images for training (224 images)
│   ├── labels/          # YOLO format labels
│   └── backup/          # Backup files
├── src/
│   ├── vision/
│   │   └── cup_detector.py
│   ├── robot/
│   │   └── dofbot_controller.py
│   └── main.py
├── yolo-cup.cfg         # YOLO configuration file
├── cup.names            # Class names for YOLO
├── requirements.txt
├── xml_to_yolo.py       # Convert XML to YOLO format
├── labelme_to_yolo.py   # Convert LabelMe JSON to YOLO
├── validate_labels.py   # Validate and analyze labels
├── auto_labeling.py     # AI-powered auto-labeling options
├── check_box_quality.py # Analyze bounding box quality
└── README.md
```

## Current Status

### ✅ Completed
- **Dataset Preparation**: 224 cup images renamed sequentially (`cup_001.jpg` to `cup_224.jpg`)
- **Labeling Setup**: Tools configured for YOLO format labeling
- **YOLO Configuration**: Single-class cup detection model configured
- **Label Conversion**: XML to YOLO format conversion script ready
- **Validation Tools**: Scripts to check label quality and statistics
- **Auto-Labeling Options**: Multiple AI-powered labeling solutions available

### 🔄 In Progress
- **Image Labeling**: 147/224 images labeled (66% complete)
- **Total Bounding Boxes**: 551 cups detected
- **Average Cups per Image**: 3.7 cups
- **Model Training**: Pending completion of dataset labeling

### 📋 To Do
- Complete labeling of remaining 77 images
- Train YOLO model on labeled dataset
- Integrate vision system with robot control
- Implement cup stacking algorithm

## Setup Instructions

### 1. Environment Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Dataset Preparation
The project includes 224 cup images that have been renamed sequentially:
- `cup_001.jpg` to `cup_224.jpg`
- Images are ready for labeling

### 3. Labeling Images

#### Option A: LabelImg (GUI Tool)
```bash
labelImg dataset/images dataset/classes.txt dataset/labels
```
- Press `W` to create bounding box
- Type "cup" when prompted
- Press `D` for next image
- **Note**: Ensure format is set to YOLO (not XML/JSON)

#### Option B: LabelMe (Alternative GUI Tool)
```bash
labelme dataset/images --output dataset/labels --labels dataset/classes.txt
```

#### Option C: AI-Powered Auto-Labeling
For faster labeling, consider AI-powered options:
```bash
python auto_labeling.py
```
- **Roboflow**: Upload images for automatic cup detection
- **LabelMe AI**: AI-assisted labeling with suggestions
- **Template Matching**: Use existing labels as templates

#### Option D: Convert Existing Labels
If you have XML or JSON labels, convert them to YOLO format:
```bash
# Convert XML to YOLO
python xml_to_yolo.py

# Convert LabelMe JSON to YOLO
python labelme_to_yolo.py
```

### 4. Validate Labels
Check your labeling progress and quality:
```bash
python validate_labels.py
```

### 5. Check Bounding Box Quality
Analyze the tightness and quality of your bounding boxes:
```bash
python check_box_quality.py
```

## Labeling Guidelines

### Single Cups
- Draw tight bounding boxes around each cup
- Include the entire cup in the box
- Be consistent with labeling style

### Stacked Cups
- **Recommended**: Label each cup individually
- Draw separate boxes for bottom, middle, and top cups
- Useful for precise robot positioning

### Bounding Box Quality
- **Include entire cup** (top to bottom, side to side)
- **Minimize background** around the cup
- **Don't cut off** any part of the cup
- **Aim for 5-15%** of image area per cup

### YOLO Format
Each label file (`.txt`) contains:
```
0 0.543184 0.453606 0.604575 0.453431
```
Where:
- `0` = class ID (cup)
- `0.543184 0.453606` = center coordinates (normalized 0-1)
- `0.604575 0.453431` = width and height (normalized 0-1)

## YOLO Configuration

The project uses a single-class YOLO model:
- **Classes**: 1 (cup)
- **Input size**: 416x416
- **Configuration**: `yolo-cup.cfg`
- **Class names**: `cup.names`

## Usage

### Training (After labeling is complete)
```bash
# Train YOLO model (requires Darknet)
./darknet detector train data/cup.data yolo-cup.cfg darknet53.conv.74
```

### Inference
```bash
python src/main.py
```

## Features
- **Real-time cup detection** using YOLO
- **Precise robotic arm control** for cup manipulation
- **Automated pyramid stacking** sequence
- **Dataset management** tools
- **Label validation** and quality checking
- **AI-powered auto-labeling** options
- **Bounding box quality analysis**

## Requirements
- Python 3.8+
- OpenCV
- PyTorch (for training)
- DOFBOT Pro robot arm
- USB camera
- LabelImg or LabelMe (for labeling)

## Contributing
1. Label images following the guidelines
2. Use the validation tools to check quality
3. Convert any non-YOLO format labels
4. Update progress in this README

## License
MIT License