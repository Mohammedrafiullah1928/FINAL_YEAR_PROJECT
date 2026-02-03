# 🎥 ESP32-CAM Hardware Integration Guide

## 📦 **What You Need to Buy**

### **1. ESP32-CAM Module (~$7-10)**
- **Model**: AI-Thinker ESP32-CAM
- **Camera**: OV2640 (2MP)
- **Features**: WiFi, Bluetooth, microSD slot
- **Where**: Amazon, AliExpress, eBay

### **2. FTDI USB-to-Serial Adapter (~$3-5)**
- **Voltage**: 3.3V/5V switchable
- **Chip**: FT232RL or CP2102
- **Purpose**: For uploading code to ESP32-CAM
- **Note**: ESP32-CAM has no USB port, needs external programmer

### **3. Jumper Wires (~$2)**
- Female-to-female recommended
- At least 5 wires needed
- Colors help identify connections

### **4. Optional but Recommended**
- **Breadboard** (~$3): For easier connections
- **Power bank** or **5V battery**: For portable use
- **Micro-USB cable**: For FTDI power
- **SD Card** (8-32GB): For local video recording (optional)

---

## 🔌 **Hardware Connections**

### **Programming Mode (Upload Code)**

```
FTDI Adapter          ESP32-CAM
━━━━━━━━━━━━━━       ━━━━━━━━━━━
GND         ──────────> GND
VCC (5V)    ──────────> 5V
TX          ──────────> U0R (RX)
RX          ──────────> U0T (TX)
                        IO0 ────┐
                        GND ────┘ (connect during upload only)
```

**Step-by-step:**
1. Connect GND to GND (black wire)
2. Connect VCC (5V) to 5V (red wire)
3. Connect TX to U0R (yellow wire)
4. Connect RX to U0T (green wire)
5. **Connect IO0 to GND** using jumper wire (blue wire)
6. Plug FTDI into computer USB port

### **Normal Operation Mode (After Upload)**

```
Power Source          ESP32-CAM
━━━━━━━━━━━━━━       ━━━━━━━━━━━
GND         ──────────> GND
5V          ──────────> 5V

⚠️ REMOVE the IO0-to-GND jumper!
```

---

## 💻 **Software Setup**

### **Step 1: Install Arduino IDE**

1. Download from: https://www.arduino.cc/en/software
2. Install for your OS (Windows/Mac/Linux)
3. Launch Arduino IDE

### **Step 2: Add ESP32 Board Support**

1. **File → Preferences**
2. In "Additional Board Manager URLs", add:
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
3. Click **OK**
4. **Tools → Board → Boards Manager**
5. Search for "**esp32**"
6. Install "**ESP32 by Espressif Systems**" (latest version)
7. Wait for download to complete

### **Step 3: Select ESP32-CAM Board**

1. **Tools → Board → ESP32 Arduino**
2. Select "**AI Thinker ESP32-CAM**"

### **Step 4: Configure Settings**

- **Tools → Upload Speed**: 115200
- **Tools → Flash Frequency**: 80MHz
- **Tools → Flash Mode**: QIO
- **Tools → Partition Scheme**: Huge APP (3MB No OTA/1MB SPIFFS)
- **Tools → Core Debug Level**: None (or Info for debugging)

---

## 📝 **Upload Firmware**

### **Step 1: Open the Sketch**

1. In Arduino IDE: **File → Open**
2. Navigate to: `pedestrian-navigation-esp32cam/esp32_cam/esp32_cam_stream.ino`
3. Sketch opens in Arduino IDE

### **Step 2: Configure WiFi**

Find these lines near the top and change them:

```cpp
const char* ssid = "YOUR_WIFI_SSID";         // Change to your WiFi name
const char* password = "YOUR_WIFI_PASSWORD"; // Change to your WiFi password
```

**Example:**
```cpp
const char* ssid = "MyHomeWiFi";
const char* password = "MyPassword123";
```

### **Step 3: Upload**

1. **Connect ESP32-CAM** to FTDI with **IO0 connected to GND**
2. **Plug FTDI** into computer USB
3. **Tools → Port** → Select COM port (e.g., COM3, COM4)
   - On Windows: Look for "USB Serial Port (COMx)"
   - On Mac: Look for "/dev/cu.usbserial-xxxxx"
   - On Linux: Look for "/dev/ttyUSB0"
4. Click **Upload** button (→ arrow icon)
5. Wait for "Connecting..." message
6. **If it hangs**: Press and hold RESET button on ESP32-CAM, then release
7. Upload progress will show (takes 1-2 minutes)
8. Wait for "**Hard resetting via RTS pin...**" message

### **Step 4: Troubleshooting Upload Issues**

**"Failed to connect":**
- Check all wire connections
- Ensure IO0 is connected to GND
- Press RESET button when "Connecting..." appears
- Try different USB port
- Check FTDI drivers are installed

**"Brownout detector was triggered":**
- Power supply issue
- Use external 5V power supply instead of USB
- Or use powered USB hub

**"A fatal error occurred":**
- Check TX/RX are not swapped
- Verify board selection is "AI Thinker ESP32-CAM"
- Try lower upload speed (Tools → Upload Speed: 115200)

---

## 🚀 **Test Camera Stream**

### **Step 1: Start Normal Operation**

1. **DISCONNECT IO0 from GND** (very important!)
2. Open **Tools → Serial Monitor**
3. Set baud rate to **115200**
4. Press **RESET** button on ESP32-CAM
5. Watch the Serial Monitor output

### **Step 2: Find IP Address**

You should see output like this:

```
=================================
ESP32-CAM Stream Server Starting
=================================

Initializing camera...
Camera initialized successfully
Connecting to WiFi: MyHomeWiFi
......
WiFi connected!
IP Address: 192.168.1.100
Stream URL: http://192.168.1.100:81/stream

Web server started!
=================================
Ready to stream video
=================================
```

**Write down the IP address!** (e.g., 192.168.1.100)

### **Step 3: Test in Browser**

1. Open Chrome or Edge
2. Go to: `http://YOUR_IP:81` (replace YOUR_IP with actual IP)
3. You should see ESP32-CAM info page
4. Click on `/stream` link
5. **Live camera feed appears!** 📹

---

## 🔗 **Connect to Your Web Application**

### **Option 1: Browser-Based Detection (Current)**

Your web app already uses browser camera. To switch to ESP32-CAM:

1. Go to: http://localhost:5000
2. Open browser console (F12)
3. Manually change video source:
   ```javascript
   // Instead of:
   navigator.mediaDevices.getUserMedia({video: true})
   
   // Use ESP32-CAM stream:
   video.src = 'http://192.168.1.100:81/stream';
   ```

### **Option 2: Python Backend Detection**

Create `esp32_detector.py`:

```python
import cv2
from ultralytics import YOLO

# ESP32-CAM stream URL
ESP32_STREAM = "http://192.168.1.100:81/stream"

# Load YOLO model
model = YOLO('yolov8n.pt')

# Connect to ESP32-CAM
cap = cv2.VideoCapture(ESP32_STREAM)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to get frame")
        break
    
    # Run detection
    results = model(frame)
    
    # Draw results
    annotated = results[0].plot()
    cv2.imshow('ESP32-CAM Detection', annotated)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

Run: `python esp32_detector.py`

---

## 🏗️ **Physical Mounting Options**

### **1. Dashboard Mount** (for cars)
- Use suction cup phone mount
- Attach ESP32-CAM with velcro or tape
- Power from car USB port
- Angle slightly downward to see road

### **2. Helmet Mount** (for pedestrians)
- Use action camera mount (GoPro style)
- Attach ESP32-CAM to helmet front
- Use power bank in backpack
- Cable from helmet to backpack

### **3. Chest Mount** (walking)
- Attach to shirt pocket or lanyard
- Forward-facing camera
- Power bank in pocket
- Good for hands-free navigation

### **4. Handlebar Mount** (bicycle)
- Use phone/camera mount
- Secure to bicycle handlebars
- Power from battery pack in bag
- Weatherproof case recommended

---

## 🔋 **Power Options**

### **Option 1: USB Power Bank**
- **Best for**: Portable use
- **Runtime**: 4-8 hours (depending on capacity)
- **Pros**: Rechargeable, compact
- **Connection**: USB cable to 5V pin

### **Option 2: 18650 Battery Holder**
- **Best for**: DIY projects
- **Runtime**: 2-4 hours per battery
- **Voltage**: 3.7V (use voltage regulator to 5V)
- **Pros**: Replaceable batteries

### **Option 3: Car USB Port**
- **Best for**: Dashboard mount
- **Runtime**: Unlimited while car is on
- **Pros**: No battery worries
- **Connection**: USB cable to 5V pin

### **Option 4: Solar Panel** (advanced)
- **Best for**: Outdoor long-duration
- **Runtime**: Continuous in daylight
- **Requirements**: 5V solar panel + charge controller
- **Pros**: Eco-friendly, unlimited

---

## 🛠️ **Troubleshooting**

### **Camera shows brown/purple image**
- **Cause**: Camera cable loose
- **Fix**: Reseat the camera ribbon cable

### **WiFi won't connect**
- Check SSID and password are correct
- Ensure 2.4GHz WiFi (ESP32 doesn't support 5GHz)
- Check router MAC filtering if enabled
- Try moving closer to router

### **Stream is laggy**
- Reduce JPEG quality (increase JPEG_QUALITY value)
- Lower frame size (FRAMESIZE_SVGA instead of VGA)
- Improve WiFi signal strength
- Reduce number of clients viewing stream

### **"Brownout detector" errors**
- Insufficient power supply
- Use 5V 2A power supply minimum
- Check USB cable quality
- Try external power source

### **Camera initialization failed**
- Press RESET button
- Check camera cable connection
- Re-upload firmware
- Try different ESP32-CAM board (might be faulty)

---

## 📊 **Specifications**

| Feature | Specification |
|---------|---------------|
| **Microcontroller** | ESP32 (dual-core 240MHz) |
| **Camera** | OV2640 (2MP, 1600x1200) |
| **WiFi** | 802.11b/g/n (2.4GHz) |
| **Bluetooth** | Bluetooth 4.2 BR/EDR & BLE |
| **Power** | 5V via GPIO / 3.3V via regulator |
| **Current** | ~200mA (normal), ~400mA (streaming) |
| **Flash** | 4MB |
| **RAM** | 520KB SRAM |
| **Storage** | microSD card slot (up to 4GB) |
| **Operating Temp** | -20°C to 85°C |

---

## 🎯 **Next Steps**

### **Phase 1: Basic Testing** (Now)
✅ Upload firmware
✅ Test stream in browser
✅ Verify camera quality

### **Phase 2: Integration** (Next)
- [ ] Connect to Python detection script
- [ ] Test with YOLOv8 model
- [ ] Integrate with web application

### **Phase 3: Hardware Build** (Future)
- [ ] Choose mounting solution
- [ ] Get power system ready
- [ ] Build weatherproof case
- [ ] Test in real outdoor conditions

### **Phase 4: Custom Model** (Advanced)
- [ ] Train YOLOv8 on pothole dataset
- [ ] Deploy custom model
- [ ] Test detection accuracy
- [ ] Fine-tune for road conditions

---

## 💡 **Tips for Best Results**

1. **Angle camera 20-30° downward** to see road better
2. **Clean lens regularly** for clear detection
3. **Mount securely** to avoid vibration blur
4. **Test in various lighting** (bright, shadow, night)
5. **Keep WiFi close** for stable streaming
6. **Use high-quality power supply** to prevent brownouts
7. **Weatherproof enclosure** for outdoor use
8. **Backup power bank** for long trips

---

## 📞 **Support Resources**

- **Arduino ESP32 Forum**: https://forum.arduino.cc/c/hardware/esp32/83
- **ESP32-CAM Docs**: https://github.com/espressif/esp32-camera
- **Random Nerd Tutorials**: https://randomnerdtutorials.com/esp32-cam-projects/
- **Our GitHub**: https://github.com/Mohammedrafiullah1928/FINAL_YEAR_PROJECT

---

## 🎉 **You're Ready!**

Follow this guide step-by-step, and you'll have a working ESP32-CAM streaming to your pedestrian navigation system!

**Need help?** Check the troubleshooting section or open an issue on GitHub.

**Happy Building!** 🚀
