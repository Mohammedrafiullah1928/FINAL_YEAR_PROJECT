"""
Quick camera test - tries multiple camera indices
"""
import cv2

print("Testing camera access...")
print("="*50)

for i in range(5):
    print(f"\nTrying camera index {i}...")
    cap = cv2.VideoCapture(i)
    
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            print(f"✅ Camera {i} works! Resolution: {frame.shape[1]}x{frame.shape[0]}")
            print(f"   Use this index in the demo")
        else:
            print(f"⚠️  Camera {i} opened but can't read frames")
        cap.release()
    else:
        print(f"❌ Camera {i} not available")

print("\n" + "="*50)
print("Test complete!")
