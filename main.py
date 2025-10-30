"""
Main Application for Intelligent Pedestrian Navigation System
SAITR02 Hackathon Project

Real-time Computer Vision system for detecting urban hazards
and providing audio feedback for visually/mobility-impaired users.
"""

import cv2
import numpy as np
import time
import argparse
import sys
from pathlib import Path
import urllib.request
import urllib.error

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

import config
from src.detector import HazardDetector
from src.proximity import ProximityEstimator
from src.audio_feedback import AudioManager
from src.sidewalk_detector import SidewalkDetector
from src.utils import (
    draw_detection_box, draw_fps, draw_status_panel, 
    draw_help_text, calculate_fps, log_detection
)


class PedestrianNavigationSystem:
    """Main application class for the navigation system"""
    
    def __init__(self, video_source=0, confidence=0.45, debug=False):
        """
        Initialize the navigation system
        
        Args:
            video_source: Camera index, path to video file, or HTTP stream URL
            confidence: Detection confidence threshold (0-1)
            debug: Enable debug mode with extra visualizations
        """
        print("="*60)
        print("🦯 INTELLIGENT PEDESTRIAN NAVIGATION SYSTEM")
        print("   SAITR02 Hackathon Project")
        print("="*60)
        
        self.video_source = video_source
        self.confidence = confidence
        self.debug = debug
        self.is_http_stream = isinstance(video_source, str) and video_source.startswith('http')
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        self.reconnect_delay = 2  # seconds
        
        # Initialize video capture with retry logic for HTTP streams
        print(f"\n📹 Initializing camera/video source: {video_source}")
        if self.is_http_stream:
            print("   Detected HTTP stream - enabling reconnection logic")
            self._test_http_stream()
        
        self.cap = self._create_video_capture()
        
        if not self.cap.isOpened():
            raise RuntimeError(f"Failed to open video source: {video_source}")
        
        # Get frame dimensions
        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(f"   Resolution: {self.frame_width}x{self.frame_height}")
        
        # Initialize components
        print("\n🔧 Initializing AI/ML components...")
        self.detector = HazardDetector()
        self.proximity_estimator = ProximityEstimator(self.frame_width, self.frame_height)
        self.audio_manager = AudioManager()
        self.sidewalk_detector = SidewalkDetector(self.frame_width, self.frame_height)
        
        # State variables
        self.running = True
        self.paused = False
        self.show_debug = debug
        self.audio_enabled = config.AUDIO_ENABLED
        
        # Performance tracking
        self.prev_time = time.time()
        self.fps = 0
        
        print("\n✅ System initialized successfully!")
        print("\nStarting detection loop...")
        print("-"*60)
    
    def _test_http_stream(self):
        """Test if HTTP stream is accessible before starting"""
        try:
            print("   Testing HTTP stream connectivity...")
            req = urllib.request.Request(self.video_source)
            response = urllib.request.urlopen(req, timeout=5)
            print(f"   ✅ HTTP stream accessible (status: {response.status})")
        except urllib.error.URLError as e:
            print(f"   ⚠️  Warning: Could not verify stream accessibility: {e}")
            print(f"   Will attempt to connect anyway...")
        except Exception as e:
            print(f"   ⚠️  Warning: Stream test failed: {e}")
    
    def _create_video_capture(self):
        """Create video capture object with proper configuration"""
        cap = cv2.VideoCapture(self.video_source)
        
        # Configure buffering for HTTP streams
        if self.is_http_stream:
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimize latency
        
        return cap
    
    def _reconnect_stream(self):
        """Attempt to reconnect to the video stream"""
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            print(f"   ❌ Max reconnection attempts ({self.max_reconnect_attempts}) reached")
            return False
        
        self.reconnect_attempts += 1
        print(f"\n🔄 Connection lost. Reconnecting... (Attempt {self.reconnect_attempts}/{self.max_reconnect_attempts})")
        
        # Release old capture
        if self.cap is not None:
            self.cap.release()
        
        # Wait before reconnecting
        time.sleep(self.reconnect_delay)
        
        # Try to reconnect
        self.cap = self._create_video_capture()
        
        if self.cap.isOpened():
            print("   ✅ Reconnected successfully!")
            self.reconnect_attempts = 0  # Reset counter on success
            return True
        else:
            print(f"   ❌ Reconnection attempt {self.reconnect_attempts} failed")
            return False
    
    def process_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Process a single frame through the complete pipeline
        
        Args:
            frame: Input BGR frame
            
        Returns:
            Annotated output frame
        """
        # 1. HAZARD DETECTION
        # Run YOLO detection
        ml_detections = self.detector.detect(frame, self.confidence)
        
        # Run computer vision detection (supplement)
        cv_detections = self.detector.detect_custom_hazards(frame)
        
        # Combine detections
        all_detections = self.detector.combine_detections(ml_detections, cv_detections)
        
        # 2. PROXIMITY ANALYSIS
        analyzed_detections = []
        for detection in all_detections:
            analyzed = self.proximity_estimator.analyze_detection(detection)
            analyzed_detections.append(analyzed)
        
        # 3. PATH CLEARANCE CHECK
        path_clear, clearance_distance = self.proximity_estimator.calculate_path_clearance(
            analyzed_detections
        )
        
        # 4. SIDEWALK EDGE DETECTION
        sidewalk_result = self.sidewalk_detector.process_frame(frame)
        
        # 5. AUDIO FEEDBACK
        # Process hazard detections
        self.audio_manager.process_frame_detections(
            analyzed_detections, 
            path_clear, 
            clearance_distance
        )
        
        # Warn about sidewalk edge if needed
        if sidewalk_result['near_edge']:
            self.audio_manager.announce_edge(sidewalk_result['edge_side'])
        
        # 6. VISUALIZATION
        output_frame = frame.copy()
        
        # Draw sidewalk edges if detected
        if config.EDGE_DETECTION_ENABLED and self.show_debug:
            output_frame = sidewalk_result['annotated_frame']
        
        # Draw detection boxes
        if config.SHOW_BOUNDING_BOXES:
            for detection in analyzed_detections:
                output_frame = draw_detection_box(
                    output_frame, 
                    detection,
                    show_label=config.SHOW_LABELS,
                    show_confidence=config.SHOW_CONFIDENCE,
                    show_distance=config.SHOW_DISTANCE
                )
        
        # Draw FPS
        if config.SHOW_FPS:
            output_frame = draw_fps(output_frame, self.fps)
        
        # Draw status panel
        if self.show_debug:
            status_info = {
                'detections_count': len(analyzed_detections),
                'audio_enabled': self.audio_enabled,
                'path_clear': path_clear,
                'clearance_distance': clearance_distance
            }
            output_frame = draw_status_panel(output_frame, status_info)
        
        # Draw help text
        output_frame = draw_help_text(output_frame)
        
        # Log most critical detection
        if analyzed_detections and self.debug:
            most_critical = self.proximity_estimator.filter_most_critical(analyzed_detections)
            if most_critical:
                log_detection(most_critical)
        
        return output_frame
    
    def run(self):
        """Main application loop"""
        print("\n🎮 Controls:")
        print("   Q - Quit application")
        print("   S - Toggle sound warnings")
        print("   D - Toggle debug display")
        print("   P - Pause/Resume detection")
        print("\n")
        
        try:
            while self.running:
                if not self.paused:
                    # Read frame
                    ret, frame = self.cap.read()
                    
                    if not ret:
                        # Handle disconnection for HTTP streams
                        if self.is_http_stream:
                            if self._reconnect_stream():
                                continue  # Try reading again
                            else:
                                print("\n❌ Failed to reconnect to stream")
                                break
                        else:
                            print("\n⚠️  End of video stream")
                            break
                    
                    # Process frame
                    output_frame = self.process_frame(frame)
                    
                    # Calculate FPS
                    current_time = time.time()
                    self.fps = calculate_fps(self.prev_time, current_time)
                    self.prev_time = current_time
                else:
                    # Paused - use last frame
                    output_frame = frame.copy()
                    cv2.putText(output_frame, "PAUSED", 
                              (self.frame_width // 2 - 100, self.frame_height // 2),
                              cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)
                
                # Display frame
                cv2.imshow('Pedestrian Navigation System', output_frame)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q') or key == 27:  # Q or ESC
                    print("\n👋 Quitting application...")
                    self.running = False
                
                elif key == ord('s'):  # Toggle sound
                    self.audio_enabled = self.audio_manager.toggle_audio()
                    status = "ON" if self.audio_enabled else "OFF"
                    print(f"🔊 Audio: {status}")
                
                elif key == ord('d'):  # Toggle debug
                    self.show_debug = not self.show_debug
                    status = "ON" if self.show_debug else "OFF"
                    print(f"🐛 Debug: {status}")
                
                elif key == ord('p'):  # Pause
                    self.paused = not self.paused
                    status = "PAUSED" if self.paused else "RESUMED"
                    print(f"⏸️  {status}")
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted by user")
        
        except Exception as e:
            print(f"\n\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        print("\n🧹 Cleaning up resources...")
        
        # Release video capture
        if self.cap is not None:
            self.cap.release()
        
        # Close windows
        cv2.destroyAllWindows()
        
        # Clean up audio
        if self.audio_manager is not None:
            self.audio_manager.cleanup()
        
        print("✅ Cleanup complete")
        print("\n" + "="*60)
        print("Thank you for using the Pedestrian Navigation System!")
        print("="*60)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Intelligent Pedestrian Navigation System for Impaired Users',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use webcam (default)
  python main.py
  
  # Use ESP32-CAM HTTP stream
  python main.py --source http://192.168.1.100:81/stream
  
  # Use video file
  python main.py --source path/to/video.mp4
  
  # Adjust confidence threshold
  python main.py --confidence 0.5
  
  # Enable debug mode
  python main.py --debug
        """
    )
    
    parser.add_argument(
        '--source', '-s',
        type=str,
        default='0',
        help='Video source: 0 for webcam, path to video file, or HTTP stream URL (e.g., http://192.168.1.100:81/stream)'
    )
    
    parser.add_argument(
        '--confidence', '-c',
        type=float,
        default=config.CONFIDENCE_THRESHOLD,
        help=f'Detection confidence threshold 0-1 (default: {config.CONFIDENCE_THRESHOLD})'
    )
    
    parser.add_argument(
        '--debug', '-d',
        action='store_true',
        help='Enable debug mode with extra visualizations and logging'
    )
    
    args = parser.parse_args()
    
    # Convert source to int if it's a digit
    video_source = args.source
    if isinstance(video_source, str) and video_source.isdigit():
        video_source = int(video_source)
    
    # Validate confidence
    if not 0 <= args.confidence <= 1:
        print("❌ Error: Confidence must be between 0 and 1")
        sys.exit(1)
    
    # Create and run system
    try:
        system = PedestrianNavigationSystem(
            video_source=video_source,
            confidence=args.confidence,
            debug=args.debug
        )
        system.run()
    
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
