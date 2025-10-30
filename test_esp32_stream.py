#!/usr/bin/env python3
"""
ESP32-CAM Stream Testing Script
Tests connectivity and frame capture from ESP32-CAM MJPEG stream

Usage:
    python test_esp32_stream.py http://192.168.1.100:81/stream
    python test_esp32_stream.py <STREAM_URL>

Exit codes:
    0 - Success (stream accessible and frames captured)
    1 - Connection failed or invalid URL
    2 - Cannot read frames from stream
"""

import sys
import cv2
import time
import urllib.request
import urllib.error
from typing import Tuple


def test_http_connectivity(url: str) -> bool:
    """
    Test if the HTTP endpoint is accessible
    
    Args:
        url: Stream URL to test
        
    Returns:
        True if accessible, False otherwise
    """
    print(f"🔍 Testing HTTP connectivity: {url}")
    
    try:
        req = urllib.request.Request(url)
        response = urllib.request.urlopen(req, timeout=5)
        status = response.status
        
        if status == 200:
            print(f"   ✅ HTTP endpoint accessible (status: {status})")
            return True
        else:
            print(f"   ⚠️  Unexpected status code: {status}")
            return False
            
    except urllib.error.HTTPError as e:
        print(f"   ❌ HTTP Error: {e.code} - {e.reason}")
        return False
        
    except urllib.error.URLError as e:
        print(f"   ❌ URL Error: {e.reason}")
        print(f"   → Check: Is ESP32-CAM powered on?")
        print(f"   → Check: Are you on the same network?")
        print(f"   → Check: Is the IP address correct?")
        return False
        
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False


def test_stream_capture(url: str, num_frames: int = 5) -> Tuple[bool, dict]:
    """
    Test if frames can be captured from the stream
    
    Args:
        url: Stream URL
        num_frames: Number of frames to capture for testing
        
    Returns:
        Tuple of (success, statistics_dict)
    """
    print(f"\n📹 Testing video stream capture...")
    print(f"   Attempting to capture {num_frames} frames...")
    
    stats = {
        'frames_captured': 0,
        'capture_time': 0.0,
        'avg_fps': 0.0,
        'resolution': None,
        'failed': False
    }
    
    cap = None
    
    try:
        # Open stream
        cap = cv2.VideoCapture(url)
        
        # Set minimal buffer to reduce latency
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        if not cap.isOpened():
            print("   ❌ Failed to open video stream")
            print("   → OpenCV could not connect to MJPEG stream")
            stats['failed'] = True
            return False, stats
        
        print("   ✅ Stream opened successfully")
        
        # Capture frames
        start_time = time.time()
        frames_captured = 0
        
        for i in range(num_frames):
            ret, frame = cap.read()
            
            if not ret:
                print(f"   ❌ Failed to read frame {i+1}/{num_frames}")
                stats['failed'] = True
                break
            
            frames_captured += 1
            
            # Get resolution from first frame
            if i == 0:
                height, width = frame.shape[:2]
                stats['resolution'] = f"{width}x{height}"
                print(f"   📐 Resolution: {width}x{height}")
            
            print(f"   ✓ Frame {i+1}/{num_frames} captured")
            
            # Small delay between frames
            time.sleep(0.1)
        
        end_time = time.time()
        
        # Calculate statistics
        stats['frames_captured'] = frames_captured
        stats['capture_time'] = end_time - start_time
        
        if stats['capture_time'] > 0:
            stats['avg_fps'] = frames_captured / stats['capture_time']
        
        if frames_captured == num_frames:
            print(f"\n✅ Successfully captured all {num_frames} frames!")
            print(f"   📊 Statistics:")
            print(f"      - Capture time: {stats['capture_time']:.2f}s")
            print(f"      - Average FPS: {stats['avg_fps']:.1f}")
            print(f"      - Resolution: {stats['resolution']}")
            return True, stats
        else:
            print(f"\n⚠️  Only captured {frames_captured}/{num_frames} frames")
            return False, stats
            
    except Exception as e:
        print(f"   ❌ Capture error: {e}")
        stats['failed'] = True
        return False, stats
        
    finally:
        if cap is not None:
            cap.release()


def print_usage():
    """Print usage instructions"""
    print("Usage:")
    print("  python test_esp32_stream.py <STREAM_URL>")
    print("")
    print("Example:")
    print("  python test_esp32_stream.py http://192.168.1.100:81/stream")
    print("")
    print("To find your ESP32-CAM IP address:")
    print("  1. Open Serial Monitor in Arduino IDE (115200 baud)")
    print("  2. Press RESET button on ESP32-CAM")
    print("  3. Look for 'IP Address:' in the output")


def main():
    """Main test function"""
    print("="*60)
    print("ESP32-CAM STREAM TEST")
    print("="*60)
    print()
    
    # Check arguments
    if len(sys.argv) < 2:
        print("❌ Error: No stream URL provided\n")
        print_usage()
        sys.exit(1)
    
    stream_url = sys.argv[1]
    
    # Validate URL format
    if not stream_url.startswith('http://') and not stream_url.startswith('https://'):
        print(f"❌ Error: Invalid URL format: {stream_url}")
        print("   URL must start with http:// or https://\n")
        print_usage()
        sys.exit(1)
    
    print(f"Stream URL: {stream_url}")
    print()
    
    # Test 1: HTTP Connectivity
    http_ok = test_http_connectivity(stream_url)
    
    if not http_ok:
        print("\n" + "="*60)
        print("❌ TEST FAILED: Cannot connect to stream")
        print("="*60)
        sys.exit(1)
    
    # Test 2: Stream Capture
    capture_ok, stats = test_stream_capture(stream_url)
    
    print("\n" + "="*60)
    
    if capture_ok:
        print("✅ ALL TESTS PASSED")
        print("="*60)
        print("\nYour ESP32-CAM stream is working correctly!")
        print(f"\nTo use with the navigation system, run:")
        print(f"  python main.py --source {stream_url}")
        sys.exit(0)
    else:
        print("❌ TEST FAILED: Cannot capture frames from stream")
        print("="*60)
        print("\nTroubleshooting:")
        print("  1. Check ESP32-CAM power supply (needs stable 5V)")
        print("  2. Verify camera module is properly connected")
        print("  3. Try accessing stream in web browser first")
        print("  4. Check Serial Monitor for error messages")
        print("  5. Press RESET button on ESP32-CAM")
        sys.exit(2)


if __name__ == '__main__':
    main()
