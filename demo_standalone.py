"""
Complete Standalone Pedestrian Navigation Demo
Real-time hazard detection with audio warnings using laptop camera

Features:
- YOLOv8 object detection
- Proximity estimation
- Audio warnings for hazards
- Distance estimation
- Priority-based alerts

Controls:
- Q: Quit
- S: Toggle sound
- D: Toggle debug info
- P: Pause/Resume
"""

import cv2
import numpy as np
from ultralytics import YOLO
import time
import threading
import queue

# Try to import TTS, fallback if not available
try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    print("⚠️  pyttsx3 not available - audio warnings disabled")


class AudioManager:
    """Manages audio feedback with threading"""
    
    def __init__(self):
        self.audio_enabled = True
        self.audio_queue = queue.Queue()
        self.last_announcement = {}
        self.announcement_cooldown = 3.0  # seconds
        
        if TTS_AVAILABLE:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 180)  # Speed
            self.engine.setProperty('volume', 0.9)  # Volume
            
            # Start audio thread
            self.audio_thread = threading.Thread(target=self._audio_worker, daemon=True)
            self.audio_thread.start()
            print("✅ Audio system initialized")
        else:
            print("⚠️  Audio system disabled (pyttsx3 not installed)")
    
    def _audio_worker(self):
        """Background thread for audio announcements"""
        while True:
            try:
                message = self.audio_queue.get(timeout=1.0)
                if message and TTS_AVAILABLE:
                    self.engine.say(message)
                    self.engine.runAndWait()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Audio error: {e}")
    
    def announce(self, message, key="default"):
        """Announce message with cooldown"""
        if not self.audio_enabled or not TTS_AVAILABLE:
            return
        
        current_time = time.time()
        
        # Check cooldown
        if key in self.last_announcement:
            if current_time - self.last_announcement[key] < self.announcement_cooldown:
                return
        
        self.last_announcement[key] = current_time
        self.audio_queue.put(message)
    
    def toggle(self):
        """Toggle audio on/off"""
        self.audio_enabled = not self.audio_enabled
        return self.audio_enabled


class HazardDetector:
    """Detects pedestrian hazards using YOLOv8"""
    
    # Hazard categories for pedestrian navigation
    HAZARD_CLASSES = {
        'person': 'high',
        'bicycle': 'high',
        'car': 'high',
        'motorcycle': 'high',
        'bus': 'high',
        'truck': 'high',
        'chair': 'medium',
        'bench': 'medium',
        'potted plant': 'medium',
        'dog': 'high',
        'cat': 'medium',
        'backpack': 'low',
        'umbrella': 'low',
        'handbag': 'low',
        'suitcase': 'medium',
        'bottle': 'low',
        'cup': 'low',
        'laptop': 'low',
        'keyboard': 'low',
        'cell phone': 'low',
    }
    
    def __init__(self, model_name='yolov8n.pt'):
        print(f"Loading YOLOv8 model: {model_name}")
        self.model = YOLO(model_name)
        print("✅ Model loaded")
    
    def detect(self, frame, confidence=0.45):
        """Run detection on frame"""
        results = self.model(frame, conf=confidence, verbose=False)
        return results[0]
    
    def get_hazard_priority(self, class_name):
        """Get hazard priority level"""
        return self.HAZARD_CLASSES.get(class_name, 'low')


class ProximityEstimator:
    """Estimates distance and proximity to detected objects"""
    
    def __init__(self, frame_width, frame_height):
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.frame_center_x = frame_width // 2
        self.frame_center_y = frame_height // 2
    
    def estimate_distance(self, box):
        """Estimate distance based on bounding box size"""
        x1, y1, x2, y2 = box
        box_height = y2 - y1
        box_width = x2 - x1
        box_area = box_height * box_width
        
        # Simple heuristic: larger objects are closer
        frame_area = self.frame_width * self.frame_height
        area_ratio = box_area / frame_area
        
        # Estimate distance in meters (rough approximation)
        if area_ratio > 0.3:
            return 1.0, "immediate", (0, 0, 255)  # Red
        elif area_ratio > 0.15:
            return 2.0, "close", (0, 165, 255)  # Orange
        elif area_ratio > 0.05:
            return 3.5, "near", (0, 255, 255)  # Yellow
        else:
            return 5.0, "far", (0, 255, 0)  # Green
    
    def get_direction(self, box):
        """Get direction relative to camera center"""
        x1, y1, x2, y2 = box
        center_x = (x1 + x2) / 2
        
        if center_x < self.frame_center_x - 100:
            return "left"
        elif center_x > self.frame_center_x + 100:
            return "right"
        else:
            return "ahead"
    
    def get_position_in_frame(self, box):
        """Get vertical position in frame"""
        x1, y1, x2, y2 = box
        center_y = (y1 + y2) / 2
        
        if center_y > self.frame_height * 0.6:
            return "ground level"
        elif center_y > self.frame_height * 0.3:
            return "mid level"
        else:
            return "upper level"


class PedestrianNavigationDemo:
    """Main demo application"""
    
    def __init__(self):
        print("="*60)
        print("🦯 PEDESTRIAN NAVIGATION DEMO")
        print("="*60)
        print()
        
        # Initialize camera
        print("📹 Opening webcam...")
        self.cap = cv2.VideoCapture(0)
        
        if not self.cap.isOpened():
            raise RuntimeError("Cannot open camera")
        
        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(f"   ✅ Camera: {self.frame_width}x{self.frame_height}")
        
        # Initialize components
        print("\n🤖 Initializing AI components...")
        self.detector = HazardDetector()
        self.proximity = ProximityEstimator(self.frame_width, self.frame_height)
        self.audio = AudioManager()
        
        # State
        self.running = True
        self.paused = False
        self.show_debug = True
        self.frame_count = 0
        self.start_time = time.time()
        
        print("\n✅ System ready!")
        print("\n🎮 Controls:")
        print("   Q - Quit")
        print("   S - Toggle sound")
        print("   D - Toggle debug info")
        print("   P - Pause/Resume")
        print("\n👁️  Point camera at objects to test detection")
        print("="*60)
        print()
    
    def process_detections(self, results):
        """Process detection results and generate warnings"""
        detections = []
        
        for box in results.boxes:
            # Get detection info
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            confidence = float(box.conf[0])
            class_id = int(box.cls[0])
            class_name = self.detector.model.names[class_id]
            
            # Estimate distance and direction
            distance, proximity, color = self.proximity.estimate_distance([x1, y1, x2, y2])
            direction = self.proximity.get_direction([x1, y1, x2, y2])
            priority = self.detector.get_hazard_priority(class_name)
            
            detections.append({
                'box': [x1, y1, x2, y2],
                'class': class_name,
                'confidence': confidence,
                'distance': distance,
                'proximity': proximity,
                'direction': direction,
                'priority': priority,
                'color': color
            })
        
        return detections
    
    def generate_warnings(self, detections):
        """Generate audio warnings for most critical hazards"""
        if not detections:
            # Clear path announcement (less frequent)
            if self.frame_count % 90 == 0:  # Every ~3 seconds
                self.audio.announce("Path clear", key="clear_path")
            return
        
        # Sort by priority and distance
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        detections.sort(key=lambda x: (priority_order[x['priority']], x['distance']))
        
        # Announce most critical hazard
        most_critical = detections[0]
        
        if most_critical['proximity'] in ['immediate', 'close']:
            message = f"{most_critical['proximity'].upper()}! {most_critical['class']} "
            message += f"{most_critical['direction']}, {int(most_critical['distance'])} meters"
            
            key = f"{most_critical['class']}_{most_critical['direction']}"
            self.audio.announce(message, key=key)
    
    def draw_detections(self, frame, detections):
        """Draw bounding boxes and info on frame"""
        for det in detections:
            x1, y1, x2, y2 = [int(v) for v in det['box']]
            
            # Draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), det['color'], 2)
            
            # Prepare label
            label = f"{det['class']}"
            if self.show_debug:
                label += f" {det['confidence']:.2f}"
                label += f" | {det['distance']:.1f}m {det['direction']}"
            
            # Draw label background
            (label_w, label_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(frame, (x1, y1 - label_h - 10), (x1 + label_w, y1), det['color'], -1)
            
            # Draw label text
            cv2.putText(frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.5, (255, 255, 255), 1)
            
            # Draw priority indicator
            priority_colors = {'high': (0, 0, 255), 'medium': (0, 165, 255), 'low': (0, 255, 0)}
            cv2.circle(frame, (x2 - 10, y1 + 10), 5, priority_colors[det['priority']], -1)
        
        return frame
    
    def draw_info_panel(self, frame, detections):
        """Draw info panel with stats"""
        # Semi-transparent overlay
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (400, 150), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # Calculate FPS
        elapsed = time.time() - self.start_time
        fps = self.frame_count / elapsed if elapsed > 0 else 0
        
        # Draw text
        y_pos = 35
        info_lines = [
            f"FPS: {fps:.1f}",
            f"Detections: {len(detections)}",
            f"Audio: {'ON' if self.audio.audio_enabled else 'OFF'}",
            f"Frame: {self.frame_count}",
        ]
        
        for line in info_lines:
            cv2.putText(frame, line, (20, y_pos), cv2.FONT_HERSHEY_SIMPLEX,
                       0.6, (0, 255, 0), 2)
            y_pos += 30
        
        # Most critical warning
        if detections:
            critical = detections[0]
            warning = f"ALERT: {critical['class']} {critical['direction']}"
            cv2.putText(frame, warning, (20, self.frame_height - 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, critical['color'], 2)
        
        return frame
    
    def draw_controls(self, frame):
        """Draw control hints"""
        controls = "Q:Quit | S:Sound | D:Debug | P:Pause"
        cv2.putText(frame, controls, (10, self.frame_height - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        return frame
    
    def run(self):
        """Main loop"""
        try:
            while self.running:
                if not self.paused:
                    # Read frame
                    ret, frame = self.cap.read()
                    
                    if not ret:
                        print("⚠️  Failed to read frame")
                        break
                    
                    self.frame_count += 1
                    
                    # Run detection
                    results = self.detector.detect(frame, confidence=0.45)
                    
                    # Process detections
                    detections = self.process_detections(results)
                    
                    # Generate audio warnings
                    self.generate_warnings(detections)
                    
                    # Draw visualizations
                    frame = self.draw_detections(frame, detections)
                    
                    if self.show_debug:
                        frame = self.draw_info_panel(frame, detections)
                    
                    frame = self.draw_controls(frame)
                
                else:
                    # Paused - show pause message
                    cv2.putText(frame, "PAUSED", 
                              (self.frame_width // 2 - 100, self.frame_height // 2),
                              cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)
                
                # Display frame
                cv2.imshow('Pedestrian Navigation Demo', frame)
                
                # Handle keyboard
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q') or key == ord('Q'):
                    print("\n✅ Quitting...")
                    self.running = False
                
                elif key == ord('s') or key == ord('S'):
                    status = "ON" if self.audio.toggle() else "OFF"
                    print(f"🔊 Audio: {status}")
                
                elif key == ord('d') or key == ord('D'):
                    self.show_debug = not self.show_debug
                    print(f"🐛 Debug: {'ON' if self.show_debug else 'OFF'}")
                
                elif key == ord('p') or key == ord('P'):
                    self.paused = not self.paused
                    print(f"⏸️  {'PAUSED' if self.paused else 'RESUMED'}")
        
        except KeyboardInterrupt:
            print("\n⚠️  Interrupted by user")
        
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup resources"""
        print("\n🧹 Cleaning up...")
        
        if self.cap:
            self.cap.release()
        
        cv2.destroyAllWindows()
        
        # Print stats
        elapsed = time.time() - self.start_time
        avg_fps = self.frame_count / elapsed if elapsed > 0 else 0
        
        print("\n" + "="*60)
        print("📊 SESSION SUMMARY")
        print("="*60)
        print(f"Total frames: {self.frame_count}")
        print(f"Duration: {elapsed:.1f}s")
        print(f"Average FPS: {avg_fps:.1f}")
        print("="*60)
        print("\n✅ Demo complete!")


def main():
    """Entry point"""
    try:
        demo = PedestrianNavigationDemo()
        demo.run()
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
