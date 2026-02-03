"""
ESP32-CAM Detector Integration
Connects to ESP32-CAM stream and performs real-time obstacle detection
Sends results to the web application via API
"""

import cv2
import requests
import time
from ultralytics import YOLO
import numpy as np
from datetime import datetime
import json

# ===========================================
# CONFIGURATION
# ===========================================

# ESP32-CAM stream URL (change to your ESP32-CAM IP)
ESP32_STREAM_URL = "http://192.168.1.100:81/stream"

# Web application API endpoint
WEB_APP_URL = "http://localhost:5000/api/obstacles/report"

# Model configuration
MODEL_PATH = "yolov8n.pt"  # Will auto-use custom model if available
CONFIDENCE_THRESHOLD = 0.75

# Detection settings
DETECTION_INTERVAL = 3  # seconds between detections
DUPLICATE_THRESHOLD = 30  # seconds before same object can be reported again

# Priority obstacles for road monitoring
PRIORITY_OBJECTS = [
    'car', 'truck', 'bus', 'motorcycle', 'bicycle',
    'traffic light', 'fire hydrant', 'stop sign',
    'parking meter', 'bench', 'pothole', 'crack'
]

# Objects to ignore (reduce noise)
IGNORE_OBJECTS = ['person', 'backpack', 'handbag', 'umbrella', 'tie', 'suitcase']

# Simulated GPS coordinates (replace with actual GPS if available)
DEFAULT_LATITUDE = 17.385044
DEFAULT_LONGITUDE = 78.486671

# ===========================================
# DETECTION SYSTEM
# ===========================================

class ESP32CAMDetector:
    def __init__(self):
        self.detected_objects = {}
        self.last_detection_time = time.time()
        self.model = None
        self.cap = None
        
    def load_model(self):
        """Load YOLO model"""
        print("🤖 Loading YOLO model...")
        
        # Try custom model first
        try:
            self.model = YOLO('models/custom_pothole.pt')
            print("✅ Custom pothole model loaded!")
        except:
            self.model = YOLO(MODEL_PATH)
            print(f"✅ {MODEL_PATH} model loaded")
        
        return True
    
    def connect_camera(self):
        """Connect to ESP32-CAM stream"""
        print(f"📡 Connecting to ESP32-CAM: {ESP32_STREAM_URL}")
        
        try:
            self.cap = cv2.VideoCapture(ESP32_STREAM_URL)
            
            if not self.cap.isOpened():
                print("❌ Failed to connect to ESP32-CAM")
                return False
            
            # Test read
            ret, frame = self.cap.read()
            if not ret:
                print("❌ Cannot read frames from ESP32-CAM")
                return False
            
            print(f"✅ Connected! Frame size: {frame.shape[1]}x{frame.shape[0]}")
            return True
            
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False
    
    def is_duplicate(self, obj_type):
        """Check if detection is duplicate"""
        now = time.time()
        
        if obj_type in self.detected_objects:
            time_diff = now - self.detected_objects[obj_type]
            if time_diff < DUPLICATE_THRESHOLD:
                print(f"⊘ Skipping duplicate: {obj_type} (last seen {time_diff:.1f}s ago)")
                return True
        
        self.detected_objects[obj_type] = now
        return False
    
    def should_ignore(self, obj_type):
        """Check if object should be ignored"""
        if obj_type in IGNORE_OBJECTS:
            print(f"⊘ Ignoring: {obj_type}")
            return True
        return False
    
    def calculate_severity(self, obj_type, confidence):
        """Determine obstacle severity"""
        if obj_type in PRIORITY_OBJECTS:
            return 'high'
        elif confidence > 0.85:
            return 'high'
        elif confidence > 0.75:
            return 'medium'
        else:
            return 'low'
    
    def send_to_webapp(self, detection):
        """Send detection to web application"""
        try:
            response = requests.post(WEB_APP_URL, json=detection, timeout=2)
            
            if response.status_code == 200:
                print(f"✅ Sent to webapp: {detection['type']} ({detection['confidence']:.0%})")
                return True
            else:
                print(f"⚠️  Webapp response: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"⚠️  Cannot connect to webapp: {e}")
            return False
    
    def process_frame(self, frame):
        """Process single frame with YOLO"""
        results = self.model(frame, conf=CONFIDENCE_THRESHOLD, verbose=False)
        
        detections = []
        for result in results:
            boxes = result.boxes
            
            for box in boxes:
                # Get detection info
                cls_id = int(box.cls[0])
                confidence = float(box.conf[0])
                obj_type = result.names[cls_id].lower()
                
                # Filter and process
                if self.should_ignore(obj_type):
                    continue
                
                if self.is_duplicate(obj_type):
                    continue
                
                # Calculate severity
                severity = self.calculate_severity(obj_type, confidence)
                
                # Prepare detection data
                detection = {
                    'type': obj_type,
                    'confidence': confidence,
                    'severity': severity,
                    'latitude': DEFAULT_LATITUDE + (np.random.random() - 0.5) * 0.0001,
                    'longitude': DEFAULT_LONGITUDE + (np.random.random() - 0.5) * 0.0001,
                    'description': f"{obj_type} detected with {confidence*100:.1f}% confidence from ESP32-CAM",
                    'user_id': 'esp32cam',
                    'timestamp': datetime.now().isoformat()
                }
                
                detections.append(detection)
                
                # Draw on frame
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                
                label = f"{obj_type} {confidence:.2f}"
                cv2.putText(frame, label, (int(x1), int(y1)-10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        return frame, detections
    
    def run(self):
        """Main detection loop"""
        print("\n" + "="*50)
        print("🎥 ESP32-CAM OBSTACLE DETECTION SYSTEM")
        print("="*50 + "\n")
        
        # Load model
        if not self.load_model():
            return
        
        # Connect to camera
        if not self.connect_camera():
            print("\n💡 Make sure ESP32-CAM is:")
            print("   1. Powered on and connected to WiFi")
            print("   2. Accessible at:", ESP32_STREAM_URL)
            print("   3. Not being used by another program")
            return
        
        print("\n✅ System ready! Starting detection...\n")
        print("Controls:")
        print("  - Press 'q' to quit")
        print("  - Press 's' to save screenshot")
        print("  - Detection interval:", DETECTION_INTERVAL, "seconds\n")
        
        frame_count = 0
        last_detection = time.time()
        
        try:
            while True:
                # Read frame
                ret, frame = self.cap.read()
                
                if not ret:
                    print("⚠️  Failed to read frame, reconnecting...")
                    time.sleep(2)
                    if not self.connect_camera():
                        break
                    continue
                
                frame_count += 1
                current_time = time.time()
                
                # Run detection at intervals
                if current_time - last_detection >= DETECTION_INTERVAL:
                    annotated_frame, detections = self.process_frame(frame.copy())
                    
                    # Send detections to webapp
                    for detection in detections:
                        self.send_to_webapp(detection)
                    
                    last_detection = current_time
                    display_frame = annotated_frame
                else:
                    display_frame = frame
                
                # Add status overlay
                status_text = f"Frame: {frame_count} | FPS: {frame_count/(current_time-self.last_detection_time):.1f}"
                cv2.putText(display_frame, status_text, (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                next_scan = DETECTION_INTERVAL - (current_time - last_detection)
                scan_text = f"Next scan: {max(0, next_scan):.1f}s"
                cv2.putText(display_frame, scan_text, (10, 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # Display
                cv2.imshow('ESP32-CAM Detection', display_frame)
                
                # Handle keys
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("\n👋 Quitting...")
                    break
                elif key == ord('s'):
                    filename = f"esp32cam_capture_{int(time.time())}.jpg"
                    cv2.imwrite(filename, display_frame)
                    print(f"📸 Screenshot saved: {filename}")
        
        except KeyboardInterrupt:
            print("\n\n👋 Stopped by user")
        
        finally:
            print("\n🧹 Cleaning up...")
            if self.cap:
                self.cap.release()
            cv2.destroyAllWindows()
            print("✅ Done!\n")

# ===========================================
# MAIN EXECUTION
# ===========================================

if __name__ == "__main__":
    print("\n" + "="*50)
    print("ESP32-CAM DETECTOR - Pedestrian Navigation System")
    print("="*50 + "\n")
    
    print("📋 Configuration:")
    print(f"   ESP32-CAM URL: {ESP32_STREAM_URL}")
    print(f"   Web App URL: {WEB_APP_URL}")
    print(f"   Model: {MODEL_PATH}")
    print(f"   Confidence: {CONFIDENCE_THRESHOLD*100}%")
    print(f"   Detection interval: {DETECTION_INTERVAL}s")
    print(f"   Duplicate threshold: {DUPLICATE_THRESHOLD}s\n")
    
    # Instructions
    print("⚙️  Before running:")
    print("   1. Upload firmware to ESP32-CAM")
    print("   2. Note the IP address from Serial Monitor")
    print("   3. Update ESP32_STREAM_URL in this script")
    print("   4. Ensure web app is running (python web_app/server.py)")
    print("   5. Press Enter to start...")
    
    input()
    
    # Run detector
    detector = ESP32CAMDetector()
    detector.run()
