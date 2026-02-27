# Pedestrian Navigator - Android App

Complete Android application for real-time obstacle detection using ESP32-CAM and YOLOv8.

## 🏗️ Project Structure

```
android_app/
├── app/
│   ├── src/main/
│   │   ├── java/com/finalyear/pedestriannav/
│   │   │   ├── MainActivity.java           # Main UI controller
│   │   │   ├── SettingsActivity.java       # Settings screen
│   │   │   ├── DetectorManager.java        # TFLite model manager
│   │   │   ├── ESP32StreamReader.java      # MJPEG stream reader
│   │   │   ├── VoiceAlertManager.java      # TTS & haptic feedback
│   │   │   ├── Detection.java              # Detection data model
│   │   │   ├── DetectionOverlay.java       # Bounding box overlay
│   │   │   ├── DetectionAdapter.java       # RecyclerView adapter
│   │   │   ├── DetectionItem.java          # Detection list item
│   │   │   ├── DetectionService.java       # Foreground service
│   │   │   └── CocoLabels.java             # COCO class names
│   │   ├── res/
│   │   │   ├── layout/                     # UI layouts
│   │   │   ├── values/                     # Strings, colors, themes
│   │   │   ├── drawable/                   # Icons and shapes
│   │   │   └── xml/                        # Configuration files
│   │   ├── assets/                         # ⚠️ PUT MODEL HERE
│   │   │   ├── yolov8n_float16.tflite      # TFLite model (YOU ADD THIS)
│   │   │   └── labels.txt                  # Class names (optional)
│   │   └── AndroidManifest.xml             # App manifest
│   ├── build.gradle                        # App dependencies
│   └── proguard-rules.pro                  # ProGuard rules
├── build.gradle                            # Project build config
└── settings.gradle                         # Project settings
```

## 📦 Setup Instructions

### 1. Install Android Studio

Download from: https://developer.android.com/studio

### 2. Open Project

```
File → Open → Select android_app folder
```

### 3. Add TFLite Model

**IMPORTANT:** You must add the model file manually:

```bash
# Convert model first (in parent directory)
cd ../model_conversion
python convert_yolov8_to_tflite.py

# Copy model to assets
mkdir -p android_app/app/src/main/assets
cp yolov8n_saved_model/yolov8n_float16.tflite android_app/app/src/main/assets/
```

### 4. Sync Gradle

Android Studio will prompt to sync. Click "Sync Now".

### 5. Build & Run

```
Build → Make Project
Run → Run 'app'
```

## 🎨 UI Features

### Main Screen
- **Camera Preview**: Live ESP32-CAM stream
- **Detection Overlay**: Bounding boxes with labels
- **Status Indicator**: Connection status (red/yellow/green)
- **Stats Panel**: FPS, latency, detection count
- **Recent Detections**: Scrollable list of detected objects
- **Control Button**: Start/Stop detection

### Settings Screen
- **ESP32 IP Address**: Configure camera IP
- **Detection Confidence**: Adjust threshold (0.0-1.0)
- **Alert Cooldown**: Set time between alerts
- **Voice Alerts**: Enable/disable TTS
- **Vibration**: Enable/disable haptic feedback

## 🔧 Configuration

### Default Settings
```java
ESP32 IP: 192.168.1.100
Port: 81
Stream URL: http://192.168.1.100:81/stream
Confidence: 0.50
Cooldown: 3 seconds
Voice: Enabled
Vibration: Enabled
```

### Modify Settings
Settings are stored in SharedPreferences and persist between app restarts.

## 📱 Testing

### On Emulator (Limited)
```
1. Run emulator from Android Studio
2. Can test UI, but no camera stream
3. Use for UI development only
```

### On Real Device (Recommended)
```
1. Enable Developer Options on phone
2. Enable USB Debugging
3. Connect phone via USB
4. Click Run → Select your device
5. App installs and launches
```

## 🚀 Deployment

### Build APK
```
Build → Build Bundle(s) / APK(s) → Build APK(s)
```

APK location: `app/build/outputs/apk/debug/app-debug.apk`

### Install on Phone
```
adb install app/build/outputs/apk/debug/app-debug.apk
```

Or transfer APK to phone and install manually.

## 🔍 Troubleshooting

### Model Loading Fails
```
Error: "Model file not found"
Solution: Ensure yolov8n_float16.tflite is in app/src/main/assets/
```

### Build Fails
```
Error: "Failed to resolve dependencies"
Solution: Check internet connection, sync Gradle again
```

### Connection Fails
```
Error: "Connection failed"
Solution: 
1. Check ESP32-CAM is powered and running
2. Verify ESP32 IP address in Settings
3. Ensure phone and ESP32 on same WiFi
```

### Slow Detection
```
Problem: Low FPS (<10)
Solution:
1. Enable GPU acceleration (automatic if supported)
2. Lower input resolution in DetectorManager
3. Increase alert cooldown to process fewer frames
```

## 📊 Performance

### Expected Metrics (Mid-range phone, 2020+)
- **FPS**: 15-25 (with GPU)
- **Latency**: 40-100ms per frame
- **Memory**: 200-400MB RAM
- **Battery**: 4-6 hours continuous use

### Optimization Tips
```
1. Process every 2nd or 3rd frame for battery saving
2. Reduce detection confidence for faster processing
3. Use Float16 model (not Float32)
4. Keep screen off when not testing
5. Close other apps
```

## 🔐 Permissions

App requires:
- Internet (ESP32 stream)
- Network State (check connectivity)
- WiFi State (detect WiFi)
- Bluetooth Connect (for earbuds)
- Vibrate (haptic feedback)
- Foreground Service (background operation)

All requested automatically on first launch.

## 🎓 For Developers

### Key Classes

**MainActivity**: UI controller, orchestrates all components
**DetectorManager**: TFLite model inference
**ESP32StreamReader**: MJPEG stream parsing
**VoiceAlertManager**: TTS and vibration
**DetectionOverlay**: Custom view for bounding boxes

### Adding Features

**Add new detection class filter:**
```java
// In MainActivity.isImportant()
String[] importantClasses = {
    "person", "car", "dog",
    "your-new-class"  // Add here
};
```

**Adjust distance estimation:**
```java
// In Detection.estimateDistance()
float distanceMeters = (imageHeight / boxHeight) * CALIBRATION_FACTOR;
```

**Change alert messages:**
```java
// In VoiceAlertManager.getUrgentMessage()
case "person":
    return "Your custom message!";
```

## 📚 Dependencies

- TensorFlow Lite 2.14.0
- OkHttp 4.12.0
- Material Components 1.11.0
- AndroidX Camera 1.3.1
- AndroidX AppCompat 1.6.1

## 🐛 Known Issues

1. **First-time TTS delay**: Android TTS takes ~2s to initialize on first launch
2. **GPU not detected**: Some older devices don't support GPU delegate
3. **Stream buffering**: WiFi congestion can cause frame drops

## 📞 Support

For issues:
1. Check logcat: `adb logcat | grep PedestrianNav`
2. Verify ESP32 stream in browser: `http://ESP32_IP:81/stream`
3. Test TFLite model separately

## 🎉 Success Criteria

App is working correctly when:
- ✅ Stream displays in preview
- ✅ Bounding boxes appear on detected objects
- ✅ FPS counter updates (>10 FPS)
- ✅ Voice alerts play for important objects
- ✅ Vibration triggers on detections
- ✅ Recent detections list populates

## 🚀 Next Steps

After basic app works:
1. Calibrate distance estimation
2. Add GPS tracking
3. Implement guardian dashboard sync
4. Add navigation guidance
5. Create route history
6. Optimize battery usage

---

**Built for Final Year Project 2026** 🎓
**Pedestrian Navigation for Visually Impaired Users** 👓
