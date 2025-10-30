"""
Simple Webcam Test Script
Tests basic camera functionality without requiring full project setup
"""

import sys

def test_camera_basic():
    """Test basic camera access"""
    print("="*60)
    print("🎥 SIMPLE WEBCAM TEST")
    print("="*60)
    print()
    
    # Test OpenCV import
    print("1. Testing OpenCV import...")
    try:
        import cv2
        print("   ✅ OpenCV installed")
        print(f"   Version: {cv2.__version__}")
    except ImportError as e:
        print("   ❌ OpenCV not installed")
        print(f"   Error: {e}")
        print("\n   Install with: pip install opencv-python")
        return False
    
    # Test camera access
    print("\n2. Testing camera access...")
    try:
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("   ❌ Cannot open camera (index 0)")
            print("   Possible issues:")
            print("      - Camera is being used by another application")
            print("      - Camera permissions not granted")
            print("      - No camera connected")
            return False
        
        print("   ✅ Camera opened successfully")
        
        # Get camera properties
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        
        print(f"   Resolution: {width}x{height}")
        print(f"   FPS: {fps}")
        
    except Exception as e:
        print(f"   ❌ Camera test failed: {e}")
        return False
    
    # Test frame capture
    print("\n3. Testing frame capture...")
    try:
        ret, frame = cap.read()
        
        if not ret:
            print("   ❌ Failed to capture frame")
            cap.release()
            return False
        
        print("   ✅ Frame captured successfully")
        print(f"   Frame shape: {frame.shape}")
        print(f"   Frame dtype: {frame.dtype}")
        
    except Exception as e:
        print(f"   ❌ Frame capture failed: {e}")
        cap.release()
        return False
    
    # Test live display
    print("\n4. Testing live video display...")
    print("   Opening live camera window...")
    print("   Press 'Q' to quit, 'S' to save snapshot")
    print()
    
    frame_count = 0
    
    try:
        while True:
            ret, frame = cap.read()
            
            if not ret:
                print("   ⚠️  Lost camera connection")
                break
            
            frame_count += 1
            
            # Add text overlay
            cv2.putText(
                frame,
                f"Frame: {frame_count} | Press Q to quit, S to save",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )
            
            cv2.putText(
                frame,
                f"Resolution: {width}x{height}",
                (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )
            
            # Display frame
            cv2.imshow('Webcam Test - Press Q to Quit', frame)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q') or key == ord('Q'):
                print("   ✅ Exiting (Q pressed)")
                break
            elif key == ord('s') or key == ord('S'):
                filename = f"webcam_snapshot_{frame_count}.jpg"
                cv2.imwrite(filename, frame)
                print(f"   📸 Snapshot saved: {filename}")
    
    except KeyboardInterrupt:
        print("\n   ⚠️  Interrupted by user (Ctrl+C)")
    
    except Exception as e:
        print(f"\n   ❌ Display error: {e}")
        return False
    
    finally:
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        print()
    
    print("="*60)
    print("✅ WEBCAM TEST COMPLETE")
    print("="*60)
    print()
    print(f"Total frames captured: {frame_count}")
    print()
    
    return True


def main():
    """Main function"""
    success = test_camera_basic()
    
    if success:
        print("✅ Your webcam is working correctly!")
        print()
        print("Next steps:")
        print("  1. Install project dependencies: pip install -r requirements.txt")
        print("  2. Run the full navigation system: python main.py --source 0")
        sys.exit(0)
    else:
        print("❌ Webcam test failed. Please fix the issues above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
