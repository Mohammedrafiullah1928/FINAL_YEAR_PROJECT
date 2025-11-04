"""
Local YOLOv8 Training Script
Train pothole detection model on your computer

WARNING: This will be SLOW without GPU (6-12 hours)
"""

from ultralytics import YOLO
import torch

print("="*60)
print("🎓 LOCAL YOLOV8 TRAINING")
print("="*60)

# Check hardware
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"\n💻 Device: {device}")
if device == 'cpu':
    print("⚠️  WARNING: Training on CPU will be VERY SLOW (6-12 hours)")
    print("   Recommended: Use Google Colab for FREE GPU")
    response = input("\n   Continue anyway? (yes/no): ")
    if response.lower() != 'yes':
        print("Exiting. Use Google Colab instead!")
        exit()

print("\n" + "="*60)
print("STEP 1: Download Dataset")
print("="*60)
print("\n1. Go to: https://app.roboflow.com/")
print("2. Sign up (free)")
print("3. Get API key from Settings")

api_key = input("\n4. Paste your Roboflow API key: ")

if not api_key or api_key == "":
    print("❌ API key required!")
    exit()

print("\n📥 Downloading dataset...")
from roboflow import Roboflow

rf = Roboflow(api_key=api_key)
project = rf.workspace("pothole-detection-system").project("pothole-detection-6jllm")
dataset = project.version(1).download("yolov8")

print(f"✅ Dataset downloaded to: {dataset.location}")

print("\n" + "="*60)
print("STEP 2: Train Model")
print("="*60)

# Load pretrained model
print("\n📦 Loading YOLOv8 nano model...")
model = YOLO('yolov8n.pt')

print("\n🚀 Starting training...")
print("="*60)
if device == 'cpu':
    print("⏰ Estimated time: 6-12 hours (CPU)")
    print("💡 Tip: Press Ctrl+C to stop anytime")
else:
    print("⏰ Estimated time: 2-4 hours (GPU)")
print("="*60)

# Reduce epochs for CPU training
epochs = 50 if device == 'cpu' else 100
batch = 8 if device == 'cpu' else 16

print(f"\nTraining with {epochs} epochs, batch size {batch}")
print("Training will start in 5 seconds...")
import time
time.sleep(5)

# Train
results = model.train(
    data=f"{dataset.location}/data.yaml",
    epochs=epochs,
    imgsz=640 if device == 'cuda' else 416,  # Smaller for CPU
    batch=batch,
    device=device,
    name='pothole_detector',
    patience=20,
    save=True,
    plots=True,
    
    # Reduce augmentation for CPU
    hsv_h=0.015 if device == 'cuda' else 0,
    hsv_s=0.7 if device == 'cuda' else 0,
    hsv_v=0.4 if device == 'cuda' else 0,
    degrees=10 if device == 'cuda' else 0,
    translate=0.1 if device == 'cuda' else 0,
    scale=0.5 if device == 'cuda' else 0,
    mosaic=1.0 if device == 'cuda' else 0,
)

print("\n" + "="*60)
print("STEP 3: Evaluate Model")
print("="*60)

# Load best model
best_model = YOLO('runs/detect/pothole_detector/weights/best.pt')

# Validate
metrics = best_model.val()

print("\n" + "="*60)
print("📊 FINAL RESULTS")
print("="*60)
print(f"mAP50:     {metrics.box.map50:.4f}  (Detection accuracy)")
print(f"mAP50-95:  {metrics.box.map:.4f}  (Strict accuracy)")
print(f"Precision: {metrics.box.mp:.4f}  (Correct predictions)")
print(f"Recall:    {metrics.box.mr:.4f}  (Objects found)")
print("="*60)

print("\n✅ Training complete!")
print("\n📂 Model saved to:")
print(f"   runs/detect/pothole_detector/weights/best.pt")
print("\n📊 View training plots:")
print(f"   runs/detect/pothole_detector/results.png")
print(f"   runs/detect/pothole_detector/confusion_matrix.png")

print("\n" + "="*60)
print("NEXT STEPS:")
print("="*60)
print("1. Copy best.pt to your project:")
print("   models/custom_pothole.pt")
print("\n2. Use in demo:")
print("   model = YOLO('models/custom_pothole.pt')")
print("\n3. Test:")
print("   python demo_standalone.py")
print("="*60)
