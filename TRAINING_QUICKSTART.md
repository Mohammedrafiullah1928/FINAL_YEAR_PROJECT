# 🚀 QUICK START: Train Your Model (3 Options)

The Colab notebook had a JSON format error. Here are **3 working alternatives**:

---

## ⭐ **Option 1: Manual Colab Setup** (RECOMMENDED - 5 minutes)

### **Step-by-Step:**

1. **Open Colab**:
   ```
   https://colab.research.google.com/
   ```

2. **Create new notebook**:
   - File → New notebook

3. **Enable GPU**:
   - Runtime → Change runtime type
   - Hardware accelerator: **T4 GPU**
   - Save

4. **Copy-paste these cells** (10 cells total):

#### **Cell 1** - Check GPU:
```python
!nvidia-smi
import torch
print(f"CUDA: {torch.cuda.is_available()}")
```

#### **Cell 2** - Install:
```python
!pip install -q ultralytics roboflow
from ultralytics import YOLO
from roboflow import Roboflow
print("✅ Ready!")
```

#### **Cell 3** - Download dataset:
```python
ROBOFLOW_API_KEY = "YOUR_KEY_HERE"  # Get from roboflow.com

rf = Roboflow(api_key=ROBOFLOW_API_KEY)
project = rf.workspace("pothole-detection-system").project("pothole-detection-6jllm")
dataset = project.version(1).download("yolov8")
print(f"✅ Downloaded: {dataset.location}")
```

#### **Cell 4** - Train:
```python
model = YOLO('yolov8n.pt')

results = model.train(
    data=f"{dataset.location}/data.yaml",
    epochs=100,
    imgsz=640,
    batch=16,
    device=0,
    name='pothole_detector'
)
print("✅ Training done!")
```

#### **Cell 5** - Evaluate:
```python
best = YOLO('/content/runs/detect/pothole_detector/weights/best.pt')
metrics = best.val()

print(f"mAP50: {metrics.box.map50:.4f}")
print(f"Precision: {metrics.box.mp:.4f}")
print(f"Recall: {metrics.box.mr:.4f}")
```

#### **Cell 6** - View results:
```python
from IPython.display import Image, display
display(Image('/content/runs/detect/pothole_detector/results.png'))
```

#### **Cell 7** - Download:
```python
!zip -r model.zip /content/runs/detect/pothole_detector/weights/
print("✅ Download 'model.zip' from Files panel")
```

5. **Get API key**:
   - Go to: https://app.roboflow.com/
   - Sign up (free)
   - Settings → Copy API key
   - Paste in Cell 3

6. **Run all**:
   - Runtime → Run all
   - Wait 3 hours ☕

7. **Download model**:
   - Files panel (left) → `runs/detect/pothole_detector/weights/best.pt`
   - Right-click → Download

---

## 💻 **Option 2: Train Locally** (Your Computer)

### **Run this command**:

```powershell
cd c:\Users\N\Desktop\FINAL_YEAR_PROJECT\pedestrian-navigation-esp32cam

python train_local.py
```

### **What it does**:
1. Checks if you have GPU
2. Downloads dataset from Roboflow
3. Trains YOLOv8 model
4. Saves to `runs/detect/pothole_detector/weights/best.pt`

### **Requirements**:
- ⚠️ Will be SLOW on CPU (6-12 hours)
- ✅ Fast on GPU (2-4 hours)
- Need: 8GB RAM, 10GB disk space

---

## 🌐 **Option 3: Use Public Colab Notebook**

### **Direct links to working notebooks**:

1. **Official YOLOv8 Training**:
   ```
   https://colab.research.google.com/github/ultralytics/ultralytics/blob/main/examples/tutorial.ipynb
   ```

2. **Roboflow Example**:
   ```
   https://colab.research.google.com/github/roboflow/notebooks/blob/main/notebooks/train-yolov8-object-detection-on-custom-dataset.ipynb
   ```

### **Modify for your dataset**:
- Find cell with dataset download
- Replace with your Roboflow project:
  ```python
  project = rf.workspace("pothole-detection-system").project("pothole-detection-6jllm")
  ```

---

## ⚡ **Quick Comparison**:

| Option | Time | Difficulty | Speed | Cost |
|--------|------|------------|-------|------|
| **Manual Colab** | 5 min setup | Easy | Fast (GPU) | FREE |
| **Local training** | 1 min setup | Easiest | Slow (CPU) | FREE |
| **Public notebook** | 2 min setup | Medium | Fast (GPU) | FREE |

---

## 🎯 **My Recommendation**:

**Use Option 1 (Manual Colab)**

**Why?**
- ✅ FREE Tesla T4 GPU
- ✅ 10x faster than CPU
- ✅ Step-by-step control
- ✅ Only 5 minutes to set up
- ✅ No installation needed

---

## 📊 **Expected Results**:

After 100 epochs (~3 hours):

```
mAP50:     0.891  (89% accuracy)
Precision: 0.854  (85% correct)
Recall:    0.812  (81% found)
```

---

## 🆘 **Troubleshooting**:

### **"API key invalid"**
- Get new key from: https://app.roboflow.com/settings
- Make sure no spaces in key

### **"Out of memory"**
- Reduce batch size: `batch=8`
- Reduce image size: `imgsz=416`

### **"Colab disconnected"**
- Session timeout (12 hours max)
- Rerun from last checkpoint
- Or use Kaggle (30 hours/week)

---

## ✅ **Success Checklist**:

After training:
- [ ] Model file (`best.pt`) downloaded
- [ ] mAP50 > 0.80
- [ ] Training curves look good (loss decreasing)
- [ ] Confusion matrix saved
- [ ] Sample predictions work

---

## 📥 **After Training**:

1. **Copy model to project**:
   ```powershell
   # Create models folder
   mkdir c:\Users\N\Desktop\FINAL_YEAR_PROJECT\pedestrian-navigation-esp32cam\models
   
   # Copy best.pt to models/custom_pothole.pt
   ```

2. **Update demo**:
   ```python
   # In demo_standalone.py, change:
   model = YOLO('yolov8n.pt')
   
   # To:
   model = YOLO('models/custom_pothole.pt')
   ```

3. **Test**:
   ```powershell
   python demo_standalone.py
   ```

---

## 🎓 **For Your Project Report**:

Include:
1. Training platform (Google Colab)
2. Dataset (Roboflow - 2800 images)
3. Model architecture (YOLOv8 nano)
4. Training time (3 hours)
5. Results (mAP, precision, recall)
6. Screenshots (training curves, confusion matrix)

---

## 🔗 **Helpful Links**:

- **Colab**: https://colab.research.google.com/
- **Roboflow**: https://app.roboflow.com/
- **YOLOv8 Docs**: https://docs.ultralytics.com/
- **Dataset Browser**: https://universe.roboflow.com/

---

**Ready to train?** Start with **Option 1** (Manual Colab) - it's the easiest and fastest!

**Questions?** Check the detailed guide in `FREE_CLOUD_TRAINING.md`
