# 📱 Android App Setup - Quick Guide

## Prerequisites
- ✅ Android Studio installed
- ✅ YOLOv8 model converted to TFLite
- ✅ ESP32-CAM running and streaming

## Step 1: Convert Model (5 minutes)

```bash
cd model_conversion
python convert_yolov8_to_tflite.py
```

You'll get: `yolov8n_float16.tflite` (~3MB)

## Step 2: Add Model to App

```bash
# Create assets folder
mkdir -p android_app/app/src/main/assets

# Copy model
cp model_conversion/yolov8n_saved_model/yolov8n_float16.tflite android_app/app/src/main/assets/
```

## Step 3: Open in Android Studio

1. Launch Android Studio
2. Click "Open"
3. Navigate to `android_app` folder
4. Click "OK"
5. Wait for Gradle sync (2-3 minutes)

## Step 4: Connect Phone

### Enable Developer Mode (if not already)
1. Settings → About Phone
2. Tap "Build Number" 7 times
3. Enter PIN/password
4. Developer Options now enabled

### Enable USB Debugging
1. Settings → Developer Options
2. Enable "USB Debugging"
3. Connect phone via USB
4. Accept "Allow USB Debugging" popup

## Step 5: Build & Run

1. Click green "Run" button (or Shift+F10)
2. Select your connected device
3. Wait for build (first time: 5-10 minutes)
4. App installs and launches automatically

## Step 6: Configure ESP32 IP

1. In app, click Settings icon (top right)
2. Enter your ESP32-CAM IP address
   - Example: `192.168.1.100`
   - Find IP in ESP32 Serial Monitor
3. Click "Save"

## Step 7: Test Detection

1. Ensure ESP32-CAM is powered on
2. Phone connected to same WiFi as ESP32
3. Click "Start Detection" button
4. Point ESP32 camera at objects
5. You should see:
   - Live video stream
   - Bounding boxes on objects
   - Voice alerts
   - FPS counter updating

## Troubleshooting

### "Model file not found"
```
Solution: Check yolov8n_float16.tflite is in app/src/main/assets/
```

### "Connection failed"
```
Solutions:
1. Verify ESP32 IP in Settings
2. Check WiFi connectivity
3. Test ESP32 stream in browser: http://ESP32_IP:81/stream
4. Restart ESP32-CAM
```

### "Build failed"
```
Solutions:
1. File → Invalidate Caches / Restart
2. Build → Clean Project
3. Build → Rebuild Project
```

### Slow performance
```
Solutions:
1. Close other apps
2. Lower confidence threshold in Settings
3. Increase alert cooldown to 5 seconds
```

## Quick Commands

### Install via ADB
```bash
adb install app/build/outputs/apk/debug/app-debug.apk
```

### View Logs
```bash
adb logcat | grep PedestrianNav
```

### Uninstall
```bash
adb uninstall com.finalyear.pedestriannav
```

## What's Included

✅ Complete Android app with UI
✅ TensorFlow Lite integration
✅ ESP32-CAM stream reader
✅ Voice alerts (TTS)
✅ Haptic feedback (vibration)
✅ Settings screen
✅ Real-time bounding boxes
✅ Detection statistics (FPS, latency)
✅ Recent detections list

## Next Steps

After app works:
1. Test with Bluetooth earbuds
2. Calibrate distance estimation
3. Mount ESP32 on cap
4. Test outdoor navigation
5. Optimize battery settings

---

**Total Setup Time: ~30 minutes**
**Ready for demo!** 🎉
