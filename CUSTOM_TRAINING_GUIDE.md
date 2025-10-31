# 🎓 Custom Training Guide: Potholes & Obstacles Detection

This guide explains how to train YOLOv8 to detect **potholes, cracks, obstacles, and urban hazards** for your pedestrian navigation system.

---

## 📋 Table of Contents

1. [Quick Overview](#quick-overview)
2. [Option 1: Use Pre-trained Models](#option-1-use-pre-trained-models)
3. [Option 2: Fine-tune with Custom Data](#option-2-fine-tune-with-custom-data)
4. [Option 3: Combine Models](#option-3-combine-models)
5. [Dataset Sources](#dataset-sources)
6. [Training Steps](#training-steps)
7. [Integration](#integration)

---

## 🎯 Quick Overview

### What You Need to Detect:
- ✅ **Potholes** - Road damage
- ✅ **Cracks** - Pavement cracks
- ✅ **Uneven surfaces** - Steps, curbs
- ✅ **Obstacles** - Barriers, construction
- ✅ **Debris** - Objects on ground
- ✅ **People & vehicles** - Moving hazards

### Current Limitations:
- ❌ YOLOv8 (COCO dataset) detects 80 classes, but NOT potholes/cracks
- ❌ Generic objects only: person, car, chair, etc.

### Solution:
- ✅ Train custom YOLOv8 model on road hazards dataset
- ✅ OR use pre-trained pothole detection models
- ✅ OR combine multiple models

---

## 🚀 Option 1: Use Pre-trained Models (Easiest)

### A. Pothole Detection Model from Roboflow

**Step 1: Download Pre-trained Model**

Visit Roboflow Universe and download a ready-to-use model:
- [Pothole Detection Dataset](https://universe.roboflow.com/pothole-detection-system/pothole-detection-6jllm)
- [Road Damage Detection](https://universe.roboflow.com/potholes-detection-d6jf5/potholes-detection)

**Step 2: Export for YOLOv8**

1. Go to dataset page → "Export Dataset"
2. Select **YOLOv8** format
3. Download the `.zip` file
4. Extract to `models/pothole_detection/`

**Step 3: Use in Your Project**

Create `demo_pothole.py`:

```python
"""
Pedestrian Navigation with Pothole Detection
"""
import cv2
from ultralytics import YOLO
import pyttsx3

# Load pothole detection model
pothole_model = YOLO('models/pothole_detection/best.pt')

# Load generic object detection
object_model = YOLO('yolov8n.pt')

# Audio
engine = pyttsx3.init()

cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    # Detect potholes
    pothole_results = pothole_model(frame, conf=0.4)
    
    # Detect general objects
    object_results = object_model(frame, conf=0.45)
    
    # Process pothole detections
    for box in pothole_results[0].boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        confidence = box.conf[0]
        class_id = int(box.cls[0])
        class_name = pothole_results[0].names[class_id]
        
        # Draw red box for potholes
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
        cv2.putText(frame, f"HAZARD: {class_name}", (x1, y1-10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Audio warning
        engine.say(f"Warning! {class_name} ahead!")
        engine.runAndWait()
    
    # Process object detections
    for box in object_results[0].boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        class_name = object_results[0].names[int(box.cls[0])]
        
        # Draw blue box for objects
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
        cv2.putText(frame, class_name, (x1, y1-10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
    
    cv2.imshow('Pothole Detection', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

---

## 🎓 Option 2: Fine-tune with Custom Data (Best Accuracy)

### Step 1: Collect Dataset

#### **A. Download Existing Datasets**

**Recommended Datasets:**

1. **RDD2022 - Road Damage Dataset**
   - 47,000 images
   - 4 countries (India, Japan, Czech, USA)
   - Classes: D00 (longitudinal crack), D10 (transverse crack), D20 (alligator crack), D40 (pothole)
   - Download: [IEEE DataPort](https://ieee-dataport.org/competitions/road-damage-detection-challenge-2022)

2. **Pothole Dataset - Kaggle**
   - 2,800+ annotated images
   - Download: [Kaggle Pothole Dataset](https://www.kaggle.com/datasets/atulyakumar98/pothole-detection-dataset)

3. **Roboflow Public Datasets**
   - Search: "pothole", "road damage", "cracks"
   - [Roboflow Universe](https://universe.roboflow.com/)

#### **B. Create Your Own Dataset** (Recommended for local conditions)

**Tools:**
- **LabelImg** - Desktop annotation tool ([GitHub](https://github.com/heartexlabs/labelImg))
- **Roboflow** - Web-based annotation ([roboflow.com](https://roboflow.com/))
- **CVAT** - Advanced annotation ([cvat.org](https://cvat.org/))

**Collection Tips:**
- Take 500-1000 photos around your campus/city
- Vary lighting conditions (day, night, shadows)
- Multiple angles (straight, angled, close, far)
- Include negative samples (normal road)

**Classes to Annotate:**
```yaml
- pothole
- crack
- uneven_surface
- curb
- barrier
- debris
- construction_zone
```

### Step 2: Prepare Dataset

**Directory Structure:**

```
custom_dataset/
├── train/
│   ├── images/
│   │   ├── img001.jpg
│   │   ├── img002.jpg
│   │   └── ...
│   └── labels/
│       ├── img001.txt
│       ├── img002.txt
│       └── ...
├── valid/
│   ├── images/
│   └── labels/
├── test/
│   ├── images/
│   └── labels/
└── data.yaml
```

**data.yaml:**

```yaml
# Dataset configuration
path: ./custom_dataset  # dataset root directory
train: train/images     # train images (relative to 'path')
val: valid/images       # validation images
test: test/images       # test images (optional)

# Classes
nc: 7  # number of classes
names: ['pothole', 'crack', 'uneven_surface', 'curb', 'barrier', 'debris', 'construction']
```

**Label Format (YOLO format - .txt files):**

```
# img001.txt
0 0.716797 0.395833 0.216406 0.147222    # class x_center y_center width height (normalized 0-1)
1 0.234375 0.509259 0.145313 0.088889
```

### Step 3: Train Custom Model

Create `train_hazard_detector.py`:

```python
"""
Train Custom YOLOv8 Model for Hazard Detection
"""
from ultralytics import YOLO
import torch

# Check GPU availability
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"Using device: {device}")

# Load pretrained YOLOv8 model (transfer learning)
model = YOLO('yolov8n.pt')  # Start with nano model
# OR use larger models for better accuracy:
# model = YOLO('yolov8s.pt')  # Small
# model = YOLO('yolov8m.pt')  # Medium

# Train on custom dataset
results = model.train(
    data='custom_dataset/data.yaml',
    epochs=100,              # Number of training epochs
    imgsz=640,               # Image size (640, 800, 1024)
    batch=16,                # Batch size (adjust based on GPU memory)
    name='hazard_detector',  # Experiment name
    patience=20,             # Early stopping patience
    device=device,           # GPU or CPU
    
    # Augmentation (improve generalization)
    hsv_h=0.015,            # HSV-Hue augmentation
    hsv_s=0.7,              # HSV-Saturation
    hsv_v=0.4,              # HSV-Value
    degrees=10,             # Rotation
    translate=0.1,          # Translation
    scale=0.5,              # Scale
    flipud=0.0,             # Flip up-down
    fliplr=0.5,             # Flip left-right
    mosaic=1.0,             # Mosaic augmentation
    
    # Optimizer
    optimizer='Adam',       # SGD, Adam, AdamW
    lr0=0.01,               # Initial learning rate
    lrf=0.01,               # Final learning rate fraction
    momentum=0.937,         # SGD momentum
    weight_decay=0.0005,    # Weight decay
    
    # Loss
    box=7.5,                # Box loss gain
    cls=0.5,                # Classification loss gain
    dfl=1.5,                # DFL loss gain
    
    # Validation
    val=True,               # Validate during training
    plots=True,             # Save plots
    save=True,              # Save checkpoints
)

# Evaluate on test set
metrics = model.val()

print(f"\n{'='*60}")
print(f"Training Complete!")
print(f"{'='*60}")
print(f"Best model saved to: runs/detect/hazard_detector/weights/best.pt")
print(f"\nMetrics:")
print(f"  mAP50: {metrics.box.map50:.4f}")
print(f"  mAP50-95: {metrics.box.map:.4f}")
print(f"  Precision: {metrics.box.mp:.4f}")
print(f"  Recall: {metrics.box.mr:.4f}")
```

**Run Training:**

```powershell
# Install dependencies
pip install ultralytics torch torchvision

# Start training
python train_hazard_detector.py
```

**Training Time:**
- CPU: 6-12 hours (100 epochs)
- GPU (NVIDIA): 1-3 hours
- Google Colab (free GPU): 2-4 hours

**Monitor Training:**

```powershell
# View training plots
# Check: runs/detect/hazard_detector/
# - results.png (loss curves)
# - confusion_matrix.png
# - PR_curve.png
```

### Step 4: Evaluate Model

Create `evaluate_model.py`:

```python
"""
Evaluate Custom Hazard Detection Model
"""
from ultralytics import YOLO
import cv2
import os

# Load trained model
model = YOLO('runs/detect/hazard_detector/weights/best.pt')

# Test on validation images
results = model.val()

print(f"\nValidation Results:")
print(f"  mAP50: {results.box.map50:.4f}")
print(f"  mAP50-95: {results.box.map:.4f}")
print(f"  Precision: {results.box.mp:.4f}")
print(f"  Recall: {results.box.mr:.4f}")

# Test on sample images
test_images = [
    'test_pothole1.jpg',
    'test_crack1.jpg',
    'test_normal_road.jpg'
]

for img_path in test_images:
    if not os.path.exists(img_path):
        continue
    
    frame = cv2.imread(img_path)
    results = model(frame, conf=0.35)
    
    # Draw detections
    for box in results[0].boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        confidence = float(box.conf[0])
        class_id = int(box.cls[0])
        class_name = results[0].names[class_id]
        
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
        cv2.putText(frame, f"{class_name} {confidence:.2f}", 
                    (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 
                    0.6, (0, 0, 255), 2)
    
    # Show result
    cv2.imshow(f'Detection: {img_path}', frame)
    cv2.waitKey(0)

cv2.destroyAllWindows()
```

---

## 🔗 Option 3: Combine Multiple Models (Recommended)

Use **two models** for comprehensive detection:
1. **YOLOv8n (COCO)** - People, vehicles, objects
2. **Custom Model** - Potholes, cracks, hazards

Create `demo_combined.py`:

```python
"""
Combined Detection: Objects + Road Hazards
"""
import cv2
from ultralytics import YOLO
import pyttsx3
import time

# Load models
print("Loading models...")
object_model = YOLO('yolov8n.pt')  # Generic objects
hazard_model = YOLO('runs/detect/hazard_detector/weights/best.pt')  # Custom hazards
print("✅ Models loaded")

# Audio
engine = pyttsx3.init()
engine.setProperty('rate', 180)

# Camera
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

last_warning = {}
COOLDOWN = 3.0

print("\n" + "="*60)
print("🦯 COMBINED HAZARD DETECTION")
print("="*60)
print("Detecting: Objects + Potholes + Cracks + Obstacles")
print("Press 'Q' to quit")
print("="*60 + "\n")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    # Detect objects (people, vehicles, etc.)
    object_results = object_model(frame, conf=0.45, verbose=False)
    
    # Detect road hazards (potholes, cracks)
    hazard_results = hazard_model(frame, conf=0.35, verbose=False)
    
    warnings = []
    
    # Process road hazards (HIGH PRIORITY)
    for box in hazard_results[0].boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        confidence = float(box.conf[0])
        class_id = int(box.cls[0])
        class_name = hazard_results[0].names[class_id]
        
        # Draw RED box for road hazards
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
        cv2.putText(frame, f"HAZARD: {class_name} {confidence:.2f}", 
                    (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 
                    0.7, (0, 0, 255), 2)
        
        # Estimate distance
        box_height = y2 - y1
        distance = "IMMEDIATE" if box_height > 100 else "CLOSE"
        
        warnings.append((f"{distance}! {class_name} ahead", 'high'))
    
    # Process objects (people, vehicles)
    for box in object_results[0].boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        confidence = float(box.conf[0])
        class_id = int(box.cls[0])
        class_name = object_results[0].names[class_id]
        
        # Draw BLUE box for objects
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
        cv2.putText(frame, f"{class_name} {confidence:.2f}", 
                    (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 
                    0.6, (255, 0, 0), 2)
        
        # Warn for people and vehicles
        if class_name in ['person', 'bicycle', 'car', 'motorcycle', 'bus', 'truck']:
            box_height = y2 - y1
            distance = "CLOSE" if box_height > 150 else "NEAR"
            warnings.append((f"{distance}! {class_name} ahead", 'medium'))
    
    # Announce warnings (priority: high first)
    warnings.sort(key=lambda x: 0 if x[1] == 'high' else 1)
    
    current_time = time.time()
    for message, priority in warnings[:2]:  # Max 2 warnings
        key = message.split('!')[1].strip().split()[0]  # Extract object name
        
        if key not in last_warning or (current_time - last_warning[key]) > COOLDOWN:
            print(f"🔊 {message}")
            engine.say(message)
            engine.runAndWait()
            last_warning[key] = current_time
            break  # Only announce one warning per frame
    
    # Display
    cv2.imshow('Combined Hazard Detection', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

---

## 📊 Dataset Sources

### 1. **Roboflow Universe** (Easiest)
- [Pothole Detection](https://universe.roboflow.com/pothole-detection-system/pothole-detection-6jllm)
- [Road Damage](https://universe.roboflow.com/potholes-detection-d6jf5/potholes-detection)
- [Cracks Detection](https://universe.roboflow.com/crack-detection-xvyrt/crack-detection-hjrpd)

### 2. **Kaggle**
- [Pothole Dataset](https://www.kaggle.com/datasets/atulyakumar98/pothole-detection-dataset)
- [Road Damage Detection](https://www.kaggle.com/datasets/chitholian/annotated-potholes-dataset)

### 3. **IEEE DataPort**
- [RDD2022 - Road Damage Dataset](https://ieee-dataport.org/competitions/road-damage-detection-challenge-2022)

### 4. **GitHub**
- Search "pothole dataset", "road damage dataset"

---

## 🎯 Recommended Approach

### For Your Final Year Project:

**Phase 1: Quick Demo (1 week)**
✅ Use existing YOLOv8n for objects  
✅ Download pre-trained pothole model from Roboflow  
✅ Combine both models (Option 3)  

**Phase 2: Custom Training (2-4 weeks)**
✅ Collect 500+ images around campus  
✅ Annotate using Roboflow/LabelImg  
✅ Fine-tune YOLOv8 on your dataset  
✅ Achieve 85%+ accuracy  

**Phase 3: Optimization (1-2 weeks)**
✅ Test in real conditions  
✅ Adjust confidence thresholds  
✅ Optimize for FPS  

---

## 🚀 Quick Start Script

Create `setup_custom_detection.py`:

```python
"""
Quick Setup for Custom Hazard Detection
"""
import os
import subprocess

print("="*60)
print("🔧 SETTING UP CUSTOM HAZARD DETECTION")
print("="*60)

# Step 1: Install dependencies
print("\n1. Installing dependencies...")
subprocess.run(["pip", "install", "ultralytics", "roboflow"])

# Step 2: Download pre-trained pothole model from Roboflow
print("\n2. Downloading pre-trained pothole detection model...")
print("   Visit: https://universe.roboflow.com/pothole-detection-system/pothole-detection-6jllm")
print("   1. Click 'Export Dataset'")
print("   2. Select 'YOLOv8' format")
print("   3. Download and extract to 'models/pothole_detection/'")

# Step 3: Create directory structure
print("\n3. Creating directory structure...")
os.makedirs('models/pothole_detection', exist_ok=True)
os.makedirs('custom_dataset/train/images', exist_ok=True)
os.makedirs('custom_dataset/train/labels', exist_ok=True)
os.makedirs('custom_dataset/valid/images', exist_ok=True)
os.makedirs('custom_dataset/valid/labels', exist_ok=True)

print("\n✅ Setup complete!")
print("\nNext steps:")
print("  1. Download pothole model from Roboflow")
print("  2. Run: python demo_combined.py")
```

---

## 📈 Expected Results

### After Custom Training:

| Metric | Target |
|--------|--------|
| **mAP50** | >85% |
| **Precision** | >80% |
| **Recall** | >75% |
| **FPS** | 20-25 (YOLOv8n) |
| **False Positives** | <10% |

### Detection Examples:

```
Frame 001: pothole (0.89), person (0.92)
   🔊 "IMMEDIATE! pothole ahead"
   
Frame 025: crack (0.76), car (0.88)
   🔊 "CLOSE! crack ahead"
   
Frame 050: curb (0.82), bicycle (0.79)
   🔊 "WARNING! curb ahead"
```

---

## 🐛 Troubleshooting

### Low Accuracy?
- Collect more training data (500+)
- Increase epochs (150-200)
- Use larger model (yolov8s.pt or yolov8m.pt)
- Check label quality

### Slow Training?
- Reduce batch size
- Use Google Colab free GPU
- Use YOLOv8n (nano) instead of larger models

### Model Not Detecting?
- Lower confidence threshold (0.25-0.35)
- Check if model loaded correctly
- Verify test images similar to training data

---

## 📚 Additional Resources

- **YOLOv8 Docs**: https://docs.ultralytics.com/
- **Roboflow Tutorials**: https://blog.roboflow.com/
- **Computer Vision Tutorials**: https://www.pyimagesearch.com/
- **Dataset Annotation**: https://github.com/heartexlabs/labelImg

---

## 🎓 For Your Project Report

Include:
1. **Dataset Description** - Size, classes, sources
2. **Training Process** - Epochs, augmentation, hyperparameters
3. **Results** - Accuracy metrics, confusion matrix
4. **Comparison** - Before/after custom training
5. **Challenges** - Data collection, annotation time
6. **Future Work** - More classes, real-time optimization

---

**Ready to train?** Start with Option 1 (pre-trained model), then move to Option 2 for custom training!

For questions, check the documentation or create an issue on GitHub.
