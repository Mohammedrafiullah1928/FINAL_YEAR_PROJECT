"""
Demo using video file instead of webcam
Perfect for testing when camera is unavailable
"""

import cv2
from ultralytics import YOLO
import os

def main():
    print("="*60)
    print("🎬 PEDESTRIAN NAVIGATION - VIDEO FILE DEMO")
    print("="*60)
    
    # Check if video file exists
    video_file = "test_video.mp4"
    if not os.path.exists(video_file):
        print("\n⚠️  No test video found.")
        print("   You can:")
        print("   1. Add a video file named 'test_video.mp4'")
        print("   2. Or modify this script to use your video path")
        return
    
    # Load model
    print("\n🤖 Loading YOLOv8 model...")
    model = YOLO('yolov8n.pt')
    print("✅ Model loaded")
    
    # Open video
    print(f"\n📹 Opening video: {video_file}")
    cap = cv2.VideoCapture(video_file)
    
    if not cap.isOpened():
        print("❌ Cannot open video file")
        return
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"✅ Video: {width}x{height} @ {fps} FPS")
    print(f"   Total frames: {total_frames}")
    
    print("\n🎮 Controls:")
    print("   Q - Quit")
    print("   SPACE - Pause/Resume")
    print()
    
    frame_num = 0
    paused = False
    
    try:
        while True:
            if not paused:
                ret, frame = cap.read()
                if not ret:
                    print("\n✅ Video ended")
                    break
                
                frame_num += 1
                
                # Run detection
                results = model(frame, verbose=False)
                
                # Draw results
                annotated = results[0].plot()
                
                # Add info overlay
                info = f"Frame: {frame_num}/{total_frames}"
                cv2.putText(annotated, info, (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                cv2.imshow('Pedestrian Navigation - Video Demo', annotated)
            
            # Handle keys
            key = cv2.waitKey(int(1000/fps)) & 0xFF
            if key == ord('q'):
                break
            elif key == ord(' '):
                paused = not paused
                status = "PAUSED" if paused else "PLAYING"
                print(f"   {status}")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("\n✅ Demo complete!")

if __name__ == '__main__':
    main()
