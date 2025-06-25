# DOFBOT Pro Cup Stacking Project

This project implements an automated cup stacking system using the DOFBOT Pro robot arm. The system uses computer vision for cup detection and precise robotic control for stacking cups in a pyramid formation.

## Project Structure
```
cup-stacking-project/
├── dataset/
│   ├── images/          # Cup images for training (224 images)
│   ├── labels/          # YOLO format labels (COMPLETE)
│   ├── train/           # Training split (179 images)
│   ├── valid/           # Validation split (45 images)
│   └── backup/          # Backup files
├── src/
│   ├── vision/
│   │   └── cup_detector.py
│   ├── robot/
│   │   └── dofbot_controller.py
│   └── main.py
├── yolo-cup.cfg         # YOLO configuration file
├── cup.names            # Class names for YOLO
├── cup.data             # Training data configuration
├── yolov4.weights       # Pre-trained weights (250MB)
├── requirements.txt
├── xml_to_yolo.py       # Convert XML to YOLO format
├── labelme_to_yolo.py   # Convert LabelMe JSON to YOLO
├── validate_labels.py   # Validate and analyze labels
├── auto_labeling.py     # AI-powered auto-labeling options
├── check_box_quality.py # Analyze bounding box quality
├── prepare_training.py  # Prepare dataset for training
└── README.md
```

## Current Status

### ✅ Completed
- **Dataset Preparation**: 224 cup images renamed sequentially (`cup_001.jpg` to `cup_224.jpg`)
- **Image Labeling**: 224/224 images labeled (100% complete!)
- **Total Bounding Boxes**: 1,025 cups detected
- **Average Cups per Image**: 4.6 cups
- **Dataset Split**: 179 training, 45 validation images
- **Training Preparation**: Dataset ready for YOLO training
- **YOLO Configuration**: Single-class cup detection model configured
- **Label Conversion**: XML to YOLO format conversion script ready
- **Validation Tools**: Scripts to check label quality and statistics
- **Auto-Labeling Options**: Multiple AI-powered labeling solutions available

### 🔄 In Progress
- **Model Training**: Ready to start YOLO training
- **Robot Integration**: Pending model completion

### 📋 To Do
- Train YOLO model on labeled dataset
- Test model performance on validation set
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

### 2. Dataset Status
The dataset is **COMPLETE** and ready for training:
- **224 images** with YOLO format labels
- **1,025 total cups** detected across all images
- **4.6 cups per image** average (excellent variety)
- **Train/Validation split**: 179/45 images

### 3. Training Setup

#### Option A: Use Prepared Dataset (Recommended)
```bash
# Dataset is already prepared and ready
python validate_labels.py  # Check final statistics
```

#### Option B: Manual Training Setup
```bash
# Prepare dataset for training
python prepare_training.py
```

### 4. Start YOLO Training
```bash
# Install Darknet
git clone https://github.com/AlexeyAB/darknet.git
cd darknet && make

# Start training (from project root)
./darknet detector train cup.data yolo-cup.cfg yolov4.weights
```

### 5. Monitor Training
- **Check loss values** (should decrease over time)
- **Weights saved** every 1000 iterations in `backup/` folder
- **Stop when loss plateaus** (usually 2000-4000 iterations)
- **Expected training time**: 2-6 hours

### 6. Test Your Model
```bash
# Test on validation images
./darknet detector test cup.data yolo-cup.cfg backup/yolo-cup_final.weights
```

## Dataset Statistics

### **Final Dataset Quality:**
- **Total Images**: 224
- **Labeled Images**: 224 (100%)
- **Total Cups Detected**: 1,025
- **Average Cups per Image**: 4.6
- **Training Split**: 179 images (80%)
- **Validation Split**: 45 images (20%)

### **Labeling Quality:**
- **Consistent YOLO format** throughout
- **High-resolution images**: 4284x5712
- **Varied cup arrangements**: single, stacked, scattered
- **Professional labeling standards**

## YOLO Configuration

The project uses a single-class YOLO model:
- **Classes**: 1 (cup)
- **Input size**: 416x416
- **Configuration**: `yolo-cup.cfg`
- **Class names**: `cup.names`
- **Pre-trained weights**: `yolov4.weights` (250MB)

## Usage

### Training
```bash
# Start training with transfer learning
./darknet detector train cup.data yolo-cup.cfg yolov4.weights
```

### Inference
```bash
# Test model on images
./darknet detector test cup.data yolo-cup.cfg backup/yolo-cup_final.weights

# Run robot vision system
python src/main.py
```

## Features
- **Complete dataset** with 1,025 labeled cups
- **Real-time cup detection** using YOLO
- **Precise robotic arm control** for cup manipulation
- **Automated pyramid stacking** sequence
- **Dataset management** tools
- **Label validation** and quality checking
- **AI-powered auto-labeling** options
- **Bounding box quality analysis**
- **Training preparation** pipeline

## Requirements
- Python 3.8+
- OpenCV
- Darknet (for YOLO training)
- DOFBOT Pro robot arm
- USB camera

## Training Progress
- **Dataset**: ✅ Complete (224/224 images)
- **Preparation**: ✅ Complete (train/valid split)
- **Configuration**: ✅ Complete (YOLO config ready)
- **Training**: 🔄 Ready to start
- **Testing**: 📋 Pending training completion
- **Integration**: 📋 Pending model testing

## License
MIT License

