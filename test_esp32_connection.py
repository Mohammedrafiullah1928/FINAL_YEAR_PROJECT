"""
Quick test script to verify your ESP32-CAM connection
Run this first before proceeding with full implementation
"""

import requests
import cv2
import numpy as np
from PIL import Image
from io import BytesIO

def test_esp32_connection(esp32_ip):
    """Test if ESP32-CAM is accessible and streaming"""
    
    print("=" * 60)
    print("ESP32-CAM CONNECTION TEST")
    print("=" * 60)
    
    # Test 1: Check if ESP32 responds
    print(f"\n[1/3] Testing connection to ESP32-CAM...")
    print(f"   IP: {esp32_ip}")
    
    try:
        stream_url = f"http://{esp32_ip}:81/stream"
        response = requests.get(stream_url, stream=True, timeout=5)
        
        if response.status_code == 200:
            print(f"   ✅ ESP32-CAM is responding!")
            print(f"   ✅ Stream URL: {stream_url}")
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Connection failed!")
        print(f"   • Check ESP32-CAM is powered on")
        print(f"   • Verify IP address: {esp32_ip}")
        print(f"   • Ensure both on same WiFi")
        return False
    except requests.exceptions.Timeout:
        print(f"   ❌ Connection timeout!")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 2: Try to get a single frame
    print(f"\n[2/3] Testing video stream...")
    
    try:
        capture_url = f"http://{esp32_ip}/capture"
        response = requests.get(capture_url, timeout=5)
        
        if response.status_code == 200:
            # Convert to image
            image = Image.open(BytesIO(response.content))
            width, height = image.size
            print(f"   ✅ Received frame: {width}×{height}")
        else:
            print(f"   ⚠️  Capture endpoint not available (OK, stream should work)")
            
    except Exception as e:
        print(f"   ⚠️  Capture test failed (OK if stream works): {e}")
    
    # Test 3: Verify MJPEG stream format
    print(f"\n[3/3] Verifying MJPEG stream format...")
    
    try:
        response = requests.get(stream_url, stream=True, timeout=5)
        
        # Read first few bytes
        chunk = next(response.iter_content(chunk_size=1024))
        
        if b'Content-Type: image/jpeg' in chunk or chunk[0:2] == b'\xff\xd8':
            print(f"   ✅ MJPEG stream format confirmed!")
        else:
            print(f"   ⚠️  Unexpected format (might still work)")
            
    except Exception as e:
        print(f"   ⚠️  Format test failed: {e}")
    
    print("\n" + "=" * 60)
    print("TEST RESULT: ✅ ESP32-CAM IS READY!")
    print("=" * 60)
    print(f"\nYour ESP32-CAM stream URL:")
    print(f"   {stream_url}")
    print(f"\nYou can test in browser:")
    print(f"   1. Open Chrome/Firefox")
    print(f"   2. Go to: {stream_url}")
    print(f"   3. You should see live video!")
    print("\n✅ Proceed to next step: Convert YOLOv8 model")
    print("=" * 60)
    
    return True


def main():
    print("\n🚀 ESP32-CAM Quick Test\n")
    
    # Get IP from user
    print("Enter your ESP32-CAM IP address")
    print("(You can find it in Arduino Serial Monitor)")
    print("Example: 192.168.1.100")
    
    esp32_ip = input("\nESP32-CAM IP: ").strip()
    
    if not esp32_ip:
        print("\n❌ No IP address provided!")
        print("\nTo find your ESP32-CAM IP:")
        print("1. Open Arduino IDE")
        print("2. Tools → Serial Monitor")
        print("3. Set baud rate: 115200")
        print("4. Press RESET on ESP32-CAM")
        print("5. Look for: 'Camera Ready! Use http://192.168.x.x'")
        return
    
    # Run test
    success = test_esp32_connection(esp32_ip)
    
    if success:
        print("\n🎉 SUCCESS! Your ESP32-CAM is working!")
        print("\n📝 Next steps:")
        print("1. Convert YOLOv8 model:")
        print("   python convert_yolov8_to_tflite.py")
        print("\n2. Build Android app:")
        print("   Follow android_app/QUICK_SETUP.md")
    else:
        print("\n❌ ESP32-CAM connection failed")
        print("\n🔧 Troubleshooting:")
        print("1. Verify ESP32-CAM is powered on (red LED lit)")
        print("2. Check IP address in Serial Monitor")
        print("3. Ensure PC and ESP32 on same WiFi network")
        print("4. Try accessing in browser first")
        print("5. Restart ESP32-CAM and try again")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Test cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
