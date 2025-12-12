"""
Detection Client for Web Integration
Sends obstacle detections to web server with GPS coordinates
"""

import cv2
import requests
import json
import time
from ultralytics import YOLO
import pyttsx3
import numpy as np
from datetime import datetime

class WebIntegratedDetector:
    """YOLOv8 detector with web server integration"""
    
    def __init__(self, model_path='yolov8n.pt', server_url='http://localhost:5000'):
        """
        Initialize detector with web integration
        
        Args:
            model_path: Path to YOLOv8 model
            server_url: URL of web server
        """
        print("🚀 Initializing Web-Integrated Detector...")
        
        # Check for custom model
        import os
        custom_model = 'models/custom_pothole.pt'
        if os.path.exists(custom_model):
            model_path = custom_model
            print("✅ Loading CUSTOM YOLOv8 model (with pothole detection)")
        else:
            print("ℹ️  Loading GENERIC YOLOv8 model (no pothole detection)")
        
        self.model = YOLO(model_path)
        self.server_url = server_url
        
        # Audio system
        try:
            self.audio = pyttsx3.init()
            self.audio.setProperty('rate', 150)
            self.audio_enabled = True
        except:
            print("⚠️  Audio system not available")
            self.audio_enabled = False
        
        # GPS simulation (replace with real GPS in production)
        self.current_location = {
            'latitude': 17.385044,  # Default: Hyderabad
            'longitude': 78.486671
        }
        
        # Detection tracking
        self.detection_cache = {}
        self.cache_timeout = 30  # Don't report same obstacle within 30 seconds
        
        print("✅ Detector initialized and ready!")
    
    def set_location(self, latitude, longitude):
        """Update current GPS location"""
        self.current_location = {
            'latitude': latitude,
            'longitude': longitude
        }
    
    def _get_obstacle_id(self, class_name, bbox):
        """Generate unique ID for obstacle based on location"""
        x_center = (bbox[0] + bbox[2]) / 2
        y_center = (bbox[1] + bbox[3]) / 2
        return f"{class_name}_{int(x_center)}_{int(y_center)}"
    
    def _should_report(self, obstacle_id):
        """Check if obstacle should be reported (not in cache)"""
        current_time = time.time()
        
        if obstacle_id in self.detection_cache:
            last_report = self.detection_cache[obstacle_id]
            if current_time - last_report < self.cache_timeout:
                return False
        
        self.detection_cache[obstacle_id] = current_time
        return True
    
    def _send_to_server(self, detection_data):
        """Send detection to web server"""
        try:
            response = requests.post(
                f"{self.server_url}/api/obstacles/report",
                json=detection_data,
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"✅ Reported to server: {detection_data['type']}")
                    return True
            else:
                print(f"⚠️  Server error: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to connect to server: {e}")
        
        return False
    
    def _simulate_gps_movement(self):
        """Simulate GPS movement for demo (random walk)"""
        # Add small random offset (simulates movement)
        lat_offset = (np.random.random() - 0.5) * 0.0001  # ~10 meters
        lon_offset = (np.random.random() - 0.5) * 0.0001
        
        self.current_location['latitude'] += lat_offset
        self.current_location['longitude'] += lon_offset
    
    def detect_and_report(self, frame):
        """
        Detect obstacles and report to server
        
        Args:
            frame: Video frame
            
        Returns:
            Annotated frame with detections
        """
        # Simulate GPS movement (remove in production with real GPS)
        self._simulate_gps_movement()
        
        # Run detection
        results = self.model(frame, verbose=False)
        
        # Process detections
        for result in results:
            boxes = result.boxes
            
            for box in boxes:
                # Extract detection info
                bbox = box.xyxy[0].cpu().numpy()
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])
                class_name = self.model.names[class_id]
                
                # Filter low confidence
                if confidence < 0.5:
                    continue
                
                # Generate unique ID
                obstacle_id = self._get_obstacle_id(class_name, bbox)
                
                # Check if should report
                if self._should_report(obstacle_id):
                    # Determine severity
                    severity = 'medium'
                    if class_name in ['pothole', 'crack']:
                        severity = 'high'
                    elif class_name == 'person':
                        severity = 'critical'
                    
                    # Prepare detection data
                    detection_data = {
                        'type': class_name,
                        'confidence': confidence,
                        'latitude': self.current_location['latitude'],
                        'longitude': self.current_location['longitude'],
                        'severity': severity,
                        'description': f"{class_name} detected with {confidence*100:.1f}% confidence",
                        'user_id': 'demo_user'
                    }
                    
                    # Send to server
                    if self._send_to_server(detection_data):
                        # Audio warning
                        if self.audio_enabled:
                            warning = f"Warning: {class_name} ahead"
                            try:
                                self.audio.say(warning)
                                self.audio.runAndWait()
                            except:
                                pass
                
                # Draw on frame
                x1, y1, x2, y2 = map(int, bbox)
                color = (0, 0, 255) if severity == 'critical' else (0, 165, 255)
                
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                
                label = f"{class_name} {confidence:.2f}"
                cv2.putText(frame, label, (x1, y1 - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Add GPS overlay
        gps_text = f"GPS: {self.current_location['latitude']:.6f}, {self.current_location['longitude']:.6f}"
        cv2.putText(frame, gps_text, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        return frame


def main():
    """Main function - Run detection with web integration"""
    print("\n" + "="*60)
    print("🌐 WEB-INTEGRATED PEDESTRIAN NAVIGATION SYSTEM")
    print("="*60 + "\n")
    
    # Initialize detector
    detector = WebIntegratedDetector(
        server_url='http://localhost:5000'
    )
    
    print("\n📷 Starting webcam...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Failed to open webcam")
        return
    
    print("\n✅ System Ready!")
    print("\n💡 Instructions:")
    print("   • Detections are automatically sent to web server")
    print("   • View live map at: http://localhost:5000")
    print("   • Press 'q' to quit")
    print("   • Press 's' to take screenshot")
    print("\n" + "="*60 + "\n")
    
    frame_count = 0
    start_time = time.time()
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Process frame
            annotated_frame = detector.detect_and_report(frame)
            
            # Calculate FPS
            frame_count += 1
            elapsed = time.time() - start_time
            fps = frame_count / elapsed if elapsed > 0 else 0
            
            # Add FPS overlay
            cv2.putText(annotated_frame, f"FPS: {fps:.1f}", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # Display
            cv2.imshow('Pedestrian Navigation - Web Integrated', annotated_frame)
            
            # Handle keys
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                cv2.imwrite(filename, annotated_frame)
                print(f"📸 Screenshot saved: {filename}")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    
    finally:
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        
        # Final stats
        elapsed = time.time() - start_time
        print(f"\n📊 Session Stats:")
        print(f"   • Total frames: {frame_count}")
        print(f"   • Duration: {elapsed:.1f}s")
        print(f"   • Average FPS: {frame_count/elapsed:.1f}")
        print(f"   • Detections reported: {len(detector.detection_cache)}")
        print("\n✅ System shutdown complete\n")


if __name__ == '__main__':
    main()
