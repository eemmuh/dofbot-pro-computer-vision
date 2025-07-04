# DOFBOT Pro Cup Stacking Project

This project implements an automated cup stacking system using the DOFBOT Pro robot arm. The system uses computer vision for cup detection and precise robotic control for stacking cups in a pyramid formation.

---

## 🚀 Project Status (June 2024)

- **Model Training:** Complete (YOLO model trained and validated)
- **Detection:** Real-time detection working with Darknet on Jetson Orin NX
- **Accuracy:** High (100% confidence on clear cup images)
- **Robot Integration:** Next step
- **Stacking Algorithm:** Next step

---

## 🏆 Sample Detection Result

Below is an example of a successful detection from the trained model:

```
[Image: Cup detected with bounding box and label 'cup: 100']
```
- The model detects cups with high confidence (100%) and accurate bounding boxes.
- Real-time detection is fast and reliable using Darknet.

---

## Next Steps

1. **Integrate vision system with DOFBOT robot arm**
   - Use detected cup positions to guide the robot for picking and stacking.
2. **Implement stacking algorithm**
   - Plan and execute stacking sequences (e.g., pyramid, tower).
3. **Test full pipeline**
   - Camera → Detection → Robot movement → Stacking
4. **Document and demo**
   - Record video, update documentation, and prepare for presentation or deployment.

---

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
├── yolo-cup.cfg         # YOLO configuration file (memory optimized)
├── yolo-cup-tiny.cfg    # Ultra-conservative config for low memory
├── cup.names            # Class names for YOLO
├── cup.data             # Training data configuration
├── yolov4.weights       # Pre-trained weights (250MB)
├── train_yolo_optimized.sh  # Optimized training script for Jetson
├── monitor_training.sh      # Memory monitoring script
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
- **Memory Optimization**: Configurations optimized for Jetson Orin NX
- **Label Conversion**: XML to YOLO format conversion script ready
- **Validation Tools**: Scripts to check label quality and statistics
- **Auto-Labeling Options**: Multiple AI-powered labeling solutions available

### 🔄 In Progress
- **Model Training**: Ready to start YOLO training with memory optimization
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

### 4. Start YOLO Training (Jetson Optimized)

#### Memory-Optimized Training (Recommended)
```bash
# Use the optimized training script
./train_yolo_optimized.sh
```

#### Manual Training with Memory Management
```bash
# Install Darknet
git clone https://github.com/AlexeyAB/darknet.git
cd darknet && make

# Clear GPU memory first
sudo fuser -v /dev/nvidia* 2>/dev/null | xargs -I {} kill -9 {} 2>/dev/null || true

# Start training with optimized config
cd darknet
./darknet detector train ../data/cup.data ../cfg/yolo-cup.cfg yolov4.weights
```

#### If Still Running Out of Memory
```bash
# Use ultra-conservative configuration
cd darknet
./darknet detector train ../data/cup.data ../cfg/yolo-cup-tiny.cfg yolov4.weights
```

### 5. Monitor Training
```bash
# Monitor system resources during training
./monitor_training.sh
```

- **Check loss values** (should decrease over time)
- **Weights saved** every 1000 iterations in `backup/` folder
- **Stop when loss plateaus** (usually 2000-4000 iterations)
- **Expected training time**: 4-8 hours (Jetson optimized)

### 6. Test Your Model
```bash
# Test on validation images
cd darknet
./darknet detector test ../data/cup.data ../cfg/yolo-cup.cfg ../backup/yolo-cup_final.weights
```

## Memory Optimization for Jetson Orin NX

### Configuration Changes Made:
- **Batch size**: Reduced from 16 to 4 (or 2 for tiny config)
- **Subdivisions**: Reduced from 8 to 4 (or 2 for tiny config)
- **Image size**: Reduced from 416x416 to 320x320 (or 256x256 for tiny)
- **Memory management**: Added GPU memory clearing
- **Environment variables**: Set for better CUDA memory handling

### Available Configurations:
1. **yolo-cup.cfg**: Standard optimized (batch=4, 320x320)
2. **yolo-cup-tiny.cfg**: Ultra-conservative (batch=2, 256x256)

### Memory Requirements:
- **Standard config**: ~4GB RAM, ~6GB GPU memory
- **Tiny config**: ~2GB RAM, ~4GB GPU memory

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

The project uses a single-class YOLO model optimized for Jetson Orin NX:
- **Classes**: 1 (cup)
- **Input size**: 320x320 (optimized) or 256x256 (tiny)
- **Configuration**: `yolo-cup.cfg` or `yolo-cup-tiny.cfg`
- **Class names**: `cup.names`
- **Pre-trained weights**: `yolov4.weights` (250MB)
- **Memory optimized**: Batch size and image dimensions reduced

## Usage

### Training
```bash
# Use optimized training script (recommended)
./train_yolo_optimized.sh

# Or manual training
cd darknet
./darknet detector train ../data/cup.data ../cfg/yolo-cup.cfg yolov4.weights
```

### Inference
```bash
# Test model on images
cd darknet
./darknet detector test ../data/cup.data ../cfg/yolo-cup.cfg ../backup/yolo-cup_final.weights

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
- **Memory optimization** for Jetson Orin NX
- **Resource monitoring** during training

## Requirements
- Python 3.8+
- OpenCV
- Darknet (for YOLO training)
- DOFBOT Pro robot arm
- USB camera
- Jetson Orin NX (8GB RAM recommended)

## Training Progress
- **Dataset**: ✅ Complete (224/224 images)
- **Preparation**: ✅ Complete (train/valid split)
- **Configuration**: ✅ Complete (YOLO config ready, memory optimized)
- **Training**: 🔄 Ready to start (memory optimized)
- **Testing**: 📋 Pending training completion
- **Integration**: 📋 Pending model testing

## Troubleshooting

### Memory Issues During Training
1. **Use optimized script**: `./train_yolo_optimized.sh`
2. **Try tiny config**: `yolo-cup-tiny.cfg`
3. **Monitor resources**: `./monitor_training.sh`
4. **Clear GPU memory**: Restart system if needed

### Training Killed by System
- Reduce batch size further in config file
- Use smaller image dimensions
- Close other applications
- Monitor memory usage with provided script

## License
MIT License

