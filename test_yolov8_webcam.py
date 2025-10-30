"""
Minimal YOLOv8 Object Detection Demo with Webcam
Tests laptop camera with real-time object detection
"""

import cv2
import numpy as np
from ultralytics import YOLO
import time

def main():
    print("="*60)
    print("🎥 YOLOV8 WEBCAM DETECTION TEST")
    print("="*60)
    print()
    
    # Initialize YOLOv8
    print("1. Loading YOLOv8 model...")
    print("   (First run will download the model)")
    try:
        model = YOLO('yolov8n.pt')  # Nano model - fastest
        print("   ✅ Model loaded successfully")
    except Exception as e:
        print(f"   ❌ Failed to load model: {e}")
        return
    
    # Open webcam
    print("\n2. Opening webcam...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("   ❌ Cannot open camera")
        return
    
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"   ✅ Camera opened: {width}x{height}")
    
    print("\n3. Starting detection...")
    print("   Controls:")
    print("      Q - Quit")
    print("      S - Save snapshot")
    print("   ")
    print("   Place objects in view to test detection!")
    print()
    
    frame_count = 0
    start_time = time.time()
    
    try:
        while True:
            ret, frame = cap.read()
            
            if not ret:
                print("   ⚠️  Failed to read frame")
                break
            
            frame_count += 1
            
            # Run YOLOv8 detection
            results = model(frame, conf=0.45, verbose=False)
            
            # Get annotated frame with bounding boxes
            annotated_frame = results[0].plot()
            
            # Calculate FPS
            elapsed = time.time() - start_time
            fps = frame_count / elapsed if elapsed > 0 else 0
            
            # Add FPS text
            cv2.putText(
                annotated_frame,
                f"FPS: {fps:.1f}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )
            
            # Add detection count
            detections = len(results[0].boxes)
            cv2.putText(
                annotated_frame,
                f"Detections: {detections}",
                (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )
            
            # Add controls text
            cv2.putText(
                annotated_frame,
                "Press Q to quit | S to save",
                (10, height - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )
            
            # Display frame
            cv2.imshow('YOLOv8 Webcam Detection', annotated_frame)
            
            # Print detected objects (every 30 frames)
            if frame_count % 30 == 0 and detections > 0:
                detected_classes = []
                for box in results[0].boxes:
                    class_id = int(box.cls[0])
                    class_name = model.names[class_id]
                    confidence = float(box.conf[0])
                    detected_classes.append(f"{class_name} ({confidence:.2f})")
                
                print(f"   Frame {frame_count}: {', '.join(detected_classes)}")
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q') or key == ord('Q'):
                print("\n   ✅ Exiting (Q pressed)")
                break
            elif key == ord('s') or key == ord('S'):
                filename = f"detection_snapshot_{frame_count}.jpg"
                cv2.imwrite(filename, annotated_frame)
                print(f"   📸 Snapshot saved: {filename}")
    
    except KeyboardInterrupt:
        print("\n   ⚠️  Interrupted by user (Ctrl+C)")
    
    except Exception as e:
        print(f"\n   ❌ Error during detection: {e}")
    
    finally:
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        
        # Print summary
        elapsed = time.time() - start_time
        avg_fps = frame_count / elapsed if elapsed > 0 else 0
        
        print()
        print("="*60)
        print("✅ TEST COMPLETE")
        print("="*60)
        print(f"Total frames: {frame_count}")
        print(f"Total time: {elapsed:.1f}s")
        print(f"Average FPS: {avg_fps:.1f}")
        print()

if __name__ == "__main__":
    main()
