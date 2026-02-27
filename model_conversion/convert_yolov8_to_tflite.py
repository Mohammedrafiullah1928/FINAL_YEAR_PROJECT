"""
YOLOv8 to TensorFlow Lite Conversion Script
Converts YOLOv8 model to TFLite format for Android deployment
"""

from ultralytics import YOLO
import os

def convert_yolov8_to_tflite():
    """
    Convert YOLOv8n model to TensorFlow Lite format
    """
    
    print("=" * 60)
    print("YOLOv8 to TensorFlow Lite Conversion")
    print("=" * 60)
    
    # Load YOLOv8 model
    print("\n[1/4] Loading YOLOv8n model...")
    model_path = '../yolov8n.pt'
    
    if not os.path.exists(model_path):
        print(f"   Model not found at {model_path}")
        print("   Downloading pretrained YOLOv8n...")
        model = YOLO('yolov8n.pt')  # Auto-downloads
    else:
        model = YOLO(model_path)
    
    print("   ✅ Model loaded successfully")
    
    # Export to TensorFlow Lite (Float32)
    print("\n[2/4] Exporting to TFLite (Float32)...")
    print("   This may take 2-3 minutes...")
    
    model.export(
        format='tflite',
        imgsz=320,  # 320x320 input for mobile
        int8=False,  # Float32 precision
        data='coco128.yaml'  # COCO dataset config
    )
    
    print("   ✅ Float32 model exported")
    
    # Export to TensorFlow Lite (Float16 - RECOMMENDED)
    print("\n[3/4] Exporting to TFLite (Float16 - Recommended)...")
    print("   Smaller size, faster inference, minimal accuracy loss")
    
    model.export(
        format='tflite',
        imgsz=320,
        half=True,  # Float16 quantization
        data='coco128.yaml'
    )
    
    print("   ✅ Float16 model exported")
    
    # Export to TensorFlow Lite (Int8 - Most optimized)
    print("\n[4/4] Exporting to TFLite (Int8 - Most optimized)...")
    print("   Smallest size, fastest inference, slight accuracy loss")
    
    try:
        model.export(
            format='tflite',
            imgsz=320,
            int8=True,  # 8-bit quantization
            data='coco128.yaml'
        )
        print("   ✅ Int8 model exported")
    except Exception as e:
        print(f"   ⚠️  Int8 export failed (needs calibration data): {e}")
        print("   This is optional - Float16 is recommended for your project")
    
    # Summary
    print("\n" + "=" * 60)
    print("CONVERSION COMPLETE! 🎉")
    print("=" * 60)
    
    print("\nGenerated files:")
    print("  📁 yolov8n_saved_model/")
    print("     ├── yolov8n_float32.tflite  (~6MB)  - Most accurate")
    print("     └── yolov8n_float16.tflite  (~3MB)  - ⭐ RECOMMENDED")
    
    print("\n📱 For Android app:")
    print("   1. Copy yolov8n_float16.tflite to:")
    print("      android_app/app/src/main/assets/")
    print("   2. Also copy labels.txt (COCO class names)")
    print("   3. Use in DetectorManager.java")
    
    print("\n⚡ Performance expectations (Float16 on Android):")
    print("   • Model size: ~3MB")
    print("   • Inference time: 40-100ms per frame")
    print("   • FPS: 15-25 (with GPU), 5-10 (CPU only)")
    print("   • Accuracy: >95% of Float32 performance")
    
    print("\n" + "=" * 60)


def create_labels_file():
    """
    Create labels.txt file with COCO class names
    """
    
    print("\n[BONUS] Creating labels.txt...")
    
    coco_classes = [
        "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", 
        "truck", "boat", "traffic light", "fire hydrant", "stop sign", 
        "parking meter", "bench", "bird", "cat", "dog", "horse", "sheep", "cow", 
        "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella", "handbag", 
        "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite", 
        "baseball bat", "baseball glove", "skateboard", "surfboard", "tennis racket", 
        "bottle", "wine glass", "cup", "fork", "knife", "spoon", "bowl", "banana", 
        "apple", "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza", 
        "donut", "cake", "chair", "couch", "potted plant", "bed", "dining table", 
        "toilet", "tv", "laptop", "mouse", "remote", "keyboard", "cell phone", 
        "microwave", "oven", "toaster", "sink", "refrigerator", "book", "clock", 
        "vase", "scissors", "teddy bear", "hair drier", "toothbrush"
    ]
    
    with open('labels.txt', 'w') as f:
        for label in coco_classes:
            f.write(label + '\n')
    
    print("   ✅ labels.txt created (80 COCO classes)")
    print("   📋 Copy this file to android_app/app/src/main/assets/")


def test_tflite_model():
    """
    Test the converted TFLite model
    """
    
    print("\n" + "=" * 60)
    print("TESTING TFLITE MODEL")
    print("=" * 60)
    
    try:
        import tensorflow as tf
        import numpy as np
        
        print("\n[1/3] Loading TFLite model...")
        
        # Load the model
        interpreter = tf.lite.Interpreter(
            model_path='yolov8n_saved_model/yolov8n_float16.tflite'
        )
        interpreter.allocate_tensors()
        
        # Get input/output details
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        
        print("   ✅ Model loaded successfully")
        print(f"\n   Input shape: {input_details[0]['shape']}")
        print(f"   Input type: {input_details[0]['dtype']}")
        print(f"   Output tensors: {len(output_details)}")
        
        print("\n[2/3] Running test inference...")
        
        # Create dummy input (320x320x3)
        dummy_input = np.random.rand(1, 320, 320, 3).astype(np.float32)
        
        interpreter.set_tensor(input_details[0]['index'], dummy_input)
        interpreter.invoke()
        
        print("   ✅ Inference successful!")
        
        print("\n[3/3] Model info:")
        print(f"   • Input size: 320×320×3 (RGB image)")
        print(f"   • Output tensors: {len(output_details)}")
        for i, output in enumerate(output_details):
            print(f"   • Output {i}: shape={output['shape']}, type={output['dtype']}")
        
        print("\n✅ TFLite model is ready for Android deployment!")
        
    except ImportError:
        print("   ⚠️  TensorFlow not installed")
        print("   Install with: pip install tensorflow")
        print("   (Not required for conversion, only for testing)")
    except FileNotFoundError:
        print("   ⚠️  TFLite model not found")
        print("   Run conversion first")
    except Exception as e:
        print(f"   ❌ Error: {e}")


if __name__ == "__main__":
    # Convert model
    convert_yolov8_to_tflite()
    
    # Create labels file
    create_labels_file()
    
    # Test the model (optional)
    print("\nWould you like to test the TFLite model? (requires TensorFlow)")
    response = input("Test? (y/n): ").lower().strip()
    if response == 'y':
        test_tflite_model()
    
    print("\n" + "=" * 60)
    print("NEXT STEPS:")
    print("=" * 60)
    print("\n1. Copy these files to Android project:")
    print("   • yolov8n_saved_model/yolov8n_float16.tflite")
    print("   • labels.txt")
    print("\n2. Follow ANDROID_IMPLEMENTATION_GUIDE.md")
    print("\n3. Build and test Android app!")
    print("\n" + "=" * 60)
