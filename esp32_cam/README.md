# ESP32-CAM Setup Guide

## Hardware Requirements

- **ESP32-CAM AI-Thinker module** with OV2640 camera
- **FTDI USB-to-Serial adapter** (3.3V/5V) for programming
- **Jumper wires** (female-to-female recommended)
- **Micro-USB cable** for FTDI adapter

## Wiring Instructions

### Programming Mode (Upload Sketch)

Connect FTDI adapter to ESP32-CAM:

| ESP32-CAM Pin | FTDI Pin | Notes |
|---------------|----------|-------|
| GND | GND | Ground connection |
| 5V | VCC (5V) | Power supply (can also use 3.3V) |
| U0R | TX | Receive data |
| U0T | RX | Transmit data |
| IO0 | GND | **ONLY during upload** - enables programming mode |

**Important:** 
- Connect IO0 to GND **before** powering on to enter programming mode
- After upload completes, **disconnect IO0 from GND**
- Press the RESET button to start normal operation

### Normal Operation Mode

After uploading:
1. Disconnect IO0 from GND
2. Press RESET button
3. ESP32-CAM will boot and connect to WiFi
4. Camera stream will be available at the displayed IP address

## Software Setup

### 1. Install Arduino IDE

Download and install Arduino IDE from: https://www.arduino.cc/en/software

### 2. Add ESP32 Board Support

1. Open Arduino IDE
2. Go to **File → Preferences**
3. Add to "Additional Board Manager URLs":
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
4. Go to **Tools → Board → Boards Manager**
5. Search for "esp32" and install **ESP32 by Espressif Systems**

### 3. Configure WiFi Credentials

Open `esp32_cam_stream.ino` and modify these lines:

```cpp
const char* ssid = "YOUR_WIFI_SSID";        // Your WiFi network name
const char* password = "YOUR_WIFI_PASSWORD"; // Your WiFi password
```

### 4. Upload Sketch

1. Connect ESP32-CAM to FTDI with IO0 connected to GND
2. In Arduino IDE:
   - **Tools → Board** → Select "AI Thinker ESP32-CAM"
   - **Tools → Port** → Select your FTDI adapter port (COM3, COM4, etc. on Windows)
   - **Tools → Upload Speed** → 115200
3. Click **Upload** button
4. Wait for "Connecting..." message
5. If it doesn't connect, press RESET button on ESP32-CAM
6. Wait for upload to complete (may take 1-2 minutes)

### 5. Start Camera Stream

1. **Disconnect IO0 from GND**
2. Open **Tools → Serial Monitor** (115200 baud)
3. Press **RESET** button on ESP32-CAM
4. Watch for WiFi connection and IP address

You should see output like:
```
=================================
ESP32-CAM Stream Server Starting
=================================

Initializing camera...
Camera initialized successfully
Connecting to WiFi: YourNetwork
......
WiFi connected!
IP Address: 192.168.1.100
Stream URL: http://192.168.1.100:81/stream

Web server started!
=================================
Ready to stream video
=================================
```

## Finding Your Camera IP Address

### Method 1: Serial Monitor (Recommended)
- Open Serial Monitor after uploading (115200 baud)
- Press RESET button
- IP address will be displayed

### Method 2: Router Admin Panel
- Log into your router's web interface
- Check connected devices list
- Look for "ESP32-CAM" or device with hostname starting with "ESP_"

### Method 3: Network Scanner
- Use tools like:
  - **Angry IP Scanner** (Windows/Mac/Linux)
  - **Fing** (Mobile app)
  - **Advanced IP Scanner** (Windows)
- Scan your network for devices on port 81

## Testing the Stream

### Web Browser Test
Open in browser: `http://<ESP32_IP>:81/`

You should see:
- Camera status page
- Live video preview
- Links to /stream, /capture, and /status endpoints

### Python Test
```python
import cv2

stream_url = "http://192.168.1.100:81/stream"
cap = cv2.VideoCapture(stream_url)

ret, frame = cap.read()
if ret:
    print("✅ Stream working!")
    print(f"Frame size: {frame.shape}")
else:
    print("❌ Stream failed")

cap.release()
```

## Available Endpoints

| Endpoint | Description | Usage |
|----------|-------------|-------|
| `/` | Info page | Browser: View camera status and preview |
| `/stream` | MJPEG stream | Python: Use as cv2.VideoCapture source |
| `/capture` | Single JPEG | Get one frame as JPEG image |
| `/status` | JSON status | Check camera health and config |

## Troubleshooting

### Upload Failed
- **"Failed to connect"**: IO0 not connected to GND during upload
- **"Timed out waiting for packet header"**: Press RESET button when "Connecting..." appears
- **"Port busy"**: Close Serial Monitor before uploading
- **Wrong port**: Check Device Manager (Windows) for correct COM port

### Camera Not Initializing
- Check camera ribbon cable is fully inserted (blue side up)
- Ensure 5V power supply is adequate (use external 5V if FTDI underpowered)
- Try pressing RESET button

### WiFi Connection Issues
- Verify SSID and password are correct
- ESP32-CAM only supports 2.4GHz WiFi (not 5GHz)
- Check WiFi signal strength - move closer to router
- Some enterprise/hotel WiFi may not work (requires device registration)

### Stream Not Accessible
- Verify IP address from Serial Monitor
- Ensure computer and ESP32-CAM are on same network
- Check firewall settings
- Try accessing from browser first: `http://<IP>:81/`

### Poor Video Quality
- Adjust `JPEG_QUALITY` in code (lower = better quality, higher bandwidth)
- Adjust `FRAME_SIZE` for different resolutions
- Check lighting conditions - camera works best with good lighting
- Clean camera lens

## Camera Settings

### Resolution Options (FRAME_SIZE)
```cpp
FRAMESIZE_QQVGA  // 160x120
FRAMESIZE_QVGA   // 320x240
FRAMESIZE_VGA    // 640x480 (default - recommended)
FRAMESIZE_SVGA   // 800x600
FRAMESIZE_XGA    // 1024x768
FRAMESIZE_SXGA   // 1280x1024
FRAMESIZE_UXGA   // 1600x1200
```

### Quality Settings (JPEG_QUALITY)
- Range: 0-63
- Lower = higher quality, more bandwidth
- Default: 10 (good balance)
- Recommended: 10-15 for AI processing

## Power Considerations

- ESP32-CAM draws 200-300mA during operation
- FTDI 5V may not provide enough current
- For stable operation:
  - Use external 5V power supply (2A recommended)
  - Or use USB power bank
- Keep GND connected between ESP32-CAM and FTDI

## Using with Pedestrian Navigation System

Once stream is working, use with main.py:

```bash
python main.py --source http://192.168.1.100:81/stream
```

See `esp32_integration.md` for complete usage guide.

## Hardware Specifications

### ESP32-CAM AI-Thinker
- **MCU**: ESP32-S (240MHz dual-core)
- **Camera**: OV2640 (2MP)
- **RAM**: 520KB SRAM + 4MB PSRAM
- **Flash**: 4MB
- **WiFi**: 802.11 b/g/n (2.4GHz only)
- **Power**: 5V via 5V pin or 3.3V via 3.3V pin

### Camera Module (OV2640)
- Resolution: Up to 1600x1200 (UXGA)
- Interface: DVP (Digital Video Port)
- Lens: Wide angle (~66° FOV)
- Format: JPEG, RGB, YUV

## Safety Notes

- Do not reverse power polarity (may damage module)
- Do not apply 5V to 3.3V pin (only to 5V pin)
- Handle camera module gently - ribbon cable is fragile
- Avoid touching camera lens
- Do not exceed 3.6V on GPIO pins

## Additional Resources

- ESP32-CAM Datasheet: https://github.com/raphaelbs/esp32-cam-ai-thinker
- ESP32 Arduino Core: https://github.com/espressif/arduino-esp32
- Camera Library: https://github.com/espressif/esp32-camera

## Support

For issues specific to this integration, check:
1. Serial Monitor output for error messages
2. `/status` endpoint: `http://<IP>:81/status`
3. Test with browser before using Python
4. Verify network connectivity with ping: `ping <IP>`
