# 🥤 Cup Sorting System Guide

## Overview

The Cup Sorting System is an alternative to cup stacking that organizes cups into different zones based on various criteria. It uses the same YOLO detection and robot control infrastructure as the stacking system.

## 🎯 How It Works

### 1. **Detection & Analysis**
- Uses your trained YOLO model to detect cups in real-time
- Analyzes cup properties (position, size, color)
- Determines appropriate sorting zone for each cup

### 2. **Sorting Zones**
The system divides the workspace into 3 zones:
- **Left Zone** (Green): Base angle 60°
- **Center Zone** (Blue): Base angle 90°  
- **Right Zone** (Red): Base angle 120°

### 3. **Sorting Criteria**
You can sort cups by different criteria:

#### **Position-based Sorting** (Default)
- **Left Zone**: Cups in left 1/3 of camera view
- **Center Zone**: Cups in middle 1/3 of camera view
- **Right Zone**: Cups in right 1/3 of camera view

#### **Size-based Sorting**
- **Left Zone**: Small cups (area < 5000 pixels)
- **Center Zone**: Medium cups (area 5000-15000 pixels)
- **Right Zone**: Large cups (area > 15000 pixels)

#### **Color-based Sorting** (Future)
- Sort by cup color (requires color detection implementation)

## 🚀 Getting Started

### 1. **Test the System** (Recommended First Step)
```bash
# Test without robot to verify detection and sorting logic
python test_cup_sorting.py
```

Choose options:
- **Option 1**: Test on a single image
- **Option 2**: Test with live camera feed
- **Option 3**: Test on your dataset images

### 2. **Run Full System** (With Robot)
```bash
# Run the complete cup sorting system with robot
python realtime_cup_sorting.py
```

### 3. **Controls During Operation**
- **'1'**: Switch to position-based sorting
- **'2'**: Switch to size-based sorting  
- **'3'**: Switch to color-based sorting (placeholder)
- **'r'**: Reset sorting counts
- **'q'**: Quit the system

## 📊 System Features

### **Real-time Visualization**
- Live camera feed with detection overlays
- Color-coded sorting zones
- Cup detection boxes with confidence scores
- Zone assignment indicators
- Real-time statistics

### **Smart Detection**
- Stable detection filtering (prevents false triggers)
- Confidence threshold filtering
- Size-based filtering
- Multi-threaded processing

### **Robot Integration**
- Automatic cup pickup from detected positions
- Precise placement in sorting zones
- Zone counting and statistics
- Safe movement with approach positions

## 🔧 Configuration

### **Detection Settings**
```python
self.confidence_threshold = 0.5    # Minimum confidence for detection
self.min_cup_size = 50            # Minimum cup size in pixels
self.stable_detection_threshold = 3  # Frames needed for stable detection
```

### **Robot Settings**
```python
self.pickup_speed = 2000          # Speed for pickup movements
self.placement_speed = 1500       # Speed for placement movements
self.approach_speed = 1000        # Speed for approach movements
```

### **Sorting Zone Positions**
```python
self.sorting_zones = {
    'left': {'position': [60, 90, 90, 90, 90, 30]},   # Left side
    'center': {'position': [90, 90, 90, 90, 90, 30]}, # Center
    'right': {'position': [120, 90, 90, 90, 90, 30]}  # Right side
}
```

## 🎯 Use Cases

### **Educational Demonstrations**
- Show how computer vision can classify objects
- Demonstrate robotic sorting capabilities
- Teach automation and robotics concepts

### **Manufacturing Simulation**
- Simulate production line sorting
- Test quality control systems
- Demonstrate pick-and-place operations

### **Research & Development**
- Test different sorting algorithms
- Validate detection accuracy
- Develop new sorting criteria

## 🔄 Customization

### **Add New Sorting Criteria**
1. Modify `determine_sorting_zone()` method
2. Add new logic for your criteria
3. Update sorting mode options

### **Change Zone Layout**
1. Modify `sorting_zones` dictionary
2. Adjust robot positions for each zone
3. Update zone visualization colors

### **Add More Zones**
1. Add new zones to `sorting_zones`
2. Update zone boundary calculations
3. Modify sorting logic for new zones

## 🛠️ Troubleshooting

### **Detection Issues**
- Check camera connection and settings
- Verify YOLO model weights exist
- Adjust confidence threshold if needed
- Check lighting conditions

### **Robot Movement Issues**
- Verify robot connection
- Check servo angle limits
- Calibrate zone positions if needed
- Ensure safe movement speeds

### **Sorting Accuracy**
- Adjust zone boundaries
- Fine-tune sorting criteria thresholds
- Improve camera positioning
- Calibrate coordinate conversion

## 📈 Performance Tips

1. **Good Lighting**: Ensure consistent, bright lighting
2. **Camera Position**: Position camera for clear view of cups
3. **Cup Arrangement**: Space cups apart for better detection
4. **Zone Spacing**: Ensure adequate space between sorting zones
5. **Speed Settings**: Adjust robot speeds for your setup

## 🔮 Future Enhancements

- **Color Detection**: Implement actual color-based sorting
- **Multi-criteria Sorting**: Combine position, size, and color
- **Dynamic Zones**: Adjust zones based on cup distribution
- **Learning System**: Improve sorting based on historical data
- **Remote Control**: Web interface for system control

---

## 🎉 Success Metrics

- **Detection Accuracy**: Cups correctly identified
- **Sorting Accuracy**: Cups placed in correct zones
- **Speed**: Cups sorted per minute
- **Reliability**: System uptime and error rate
- **User Experience**: Ease of operation and monitoring

The cup sorting system provides a practical alternative to stacking, demonstrating the versatility of your YOLO detection and robot control infrastructure! 