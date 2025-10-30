# ESP32-CAM Integration Guide

## Overview

This document explains how to integrate the ESP32-CAM module as a wireless video source for the Intelligent Pedestrian Navigation System. The ESP32-CAM streams MJPEG video over WiFi, which can be consumed by the Python application in real-time.

## System Architecture

### How It Works

1. **ESP32-CAM Module**
   - Captures video frames using OV2640 camera sensor
   - Encodes frames as JPEG images
   - Serves MJPEG stream via HTTP web server on port 81
   - Endpoint: `http://<ESP32_IP>:81/stream`

2. **WiFi Network**
   - ESP32-CAM connects to local WiFi network
   - Gets IP address via DHCP
   - Both ESP32-CAM and computer must be on same network

3. **Python Application**
   - OpenCV's `VideoCapture` reads HTTP MJPEG stream
   - Processes frames through YOLOv8 detection pipeline
   - Provides audio feedback for detected hazards
   - Automatic reconnection on stream interruption

### Data Flow

```
ESP32-CAM Camera → JPEG Encoding → WiFi Transmission → 
Python/OpenCV → YOLOv8 Detection → Audio Feedback
```

## Hardware Setup

See `esp32_cam/README.md` for complete hardware setup instructions including:
- Wiring diagrams (FTDI programming)
- Arduino IDE configuration
- Firmware upload procedure
- WiFi configuration

## Software Integration

### 1. Upload Firmware to ESP32-CAM

Navigate to `esp32_cam/` folder and follow the README to upload `esp32_cam_stream.ino`.

Key configuration in the Arduino sketch:
```cpp
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
```

After upload, note the IP address displayed in Serial Monitor (e.g., `192.168.1.100`).

### 2. Test the Stream

**Browser Test:**
```
http://192.168.1.100:81/
```
You should see the camera info page with live preview.

**Stream Endpoint:**
```
http://192.168.1.100:81/stream
```
This is the MJPEG stream used by Python.

**Quick Python Test:**
```bash
python test_esp32_stream.py http://192.168.1.100:81/stream
```

### 3. Run Navigation System with ESP32-CAM

**Basic usage:**
```bash
python main.py --source http://192.168.1.100:81/stream
```

**With custom confidence threshold:**
```bash
python main.py --source http://192.168.1.100:81/stream --confidence 0.5
```

**With debug mode:**
```bash
python main.py --source http://192.168.1.100:81/stream --debug
```

## Stream Connection Features

### Automatic Reconnection

The Python application includes robust reconnection logic:

- **Connection Testing**: Verifies stream accessibility before starting
- **Auto-Reconnect**: Automatically reconnects if stream is interrupted
- **Retry Logic**: Up to 5 reconnection attempts with 2-second delays
- **Status Messages**: Clear feedback on connection status

### Buffer Management

- Stream buffer size minimized to reduce latency
- Prioritizes real-time feed over frame buffering
- Typical latency: 200-500ms depending on network

### Error Handling

Graceful handling of:
- Network interruptions
- ESP32-CAM restarts
- WiFi connectivity issues
- Stream timeouts

## Performance Optimization

### Recommended YOLOv8 Settings

For optimal performance with ESP32-CAM streaming:

**1. Frame Resolution (ESP32-CAM firmware):**
```cpp
#define FRAME_SIZE FRAMESIZE_VGA  // 640x480 (recommended)
```

- **VGA (640x480)**: Best balance of quality and bandwidth
- **QVGA (320x240)**: Lower bandwidth, faster processing, reduced accuracy
- **SVGA (800x600)**: Higher quality but more bandwidth required

**2. JPEG Quality (ESP32-CAM firmware):**
```cpp
#define JPEG_QUALITY 10  // 0-63, lower = better quality
```

- **8-12**: Recommended range for AI processing
- **Lower values**: Better image quality, higher bandwidth
- **Higher values**: Faster transmission, may affect detection accuracy

**3. Confidence Threshold (Python):**
```bash
python main.py --source http://192.168.1.100:81/stream --confidence 0.45
```

- **Default: 0.45** - Good balance for real-world scenarios
- **0.3-0.4**: More detections, higher false positives
- **0.5-0.7**: Fewer detections, higher confidence required

**4. Network Considerations:**

- Use 2.4GHz WiFi (ESP32-CAM doesn't support 5GHz)
- Position ESP32-CAM near router for strong signal
- Minimize WiFi congestion by reducing other devices
- Expected bandwidth: 1-3 Mbps depending on settings

### Performance Metrics

| Configuration | FPS | Detection Quality | Bandwidth |
|--------------|-----|-------------------|-----------|
| VGA @ Q10 | 20-25 | Excellent | ~2 Mbps |
| VGA @ Q15 | 25-30 | Good | ~1.5 Mbps |
| QVGA @ Q10 | 30+ | Fair | ~1 Mbps |

*Note: FPS may vary based on Python processing speed and CPU capabilities*

### Optimization Tips

1. **Reduce Stream Resolution**: If experiencing lag, lower FRAME_SIZE in ESP32 code
2. **Adjust JPEG Quality**: Increase value (e.g., 15-20) for faster streaming
3. **Lower Confidence**: Decrease threshold for faster processing with more detections
4. **Close Other Apps**: Free up CPU for YOLOv8 inference
5. **Use Wired Connection**: Connect PC via Ethernet to router for stable network

## Comparison: Webcam vs ESP32-CAM

| Feature | USB Webcam | ESP32-CAM Stream |
|---------|-----------|------------------|
| **Connection** | Wired (USB) | Wireless (WiFi) |
| **Mobility** | Limited by cable | Fully mobile |
| **Latency** | <50ms | 200-500ms |
| **Setup** | Plug & play | Firmware + WiFi config |
| **Power** | USB powered | External 5V required |
| **Resolution** | 720p-1080p+ | Up to 1600x1200 (UXGA) |
| **Cost** | $20-100+ | $8-15 |
| **Reliability** | Very high | Network-dependent |

**When to use ESP32-CAM:**
- Wireless/portable deployment needed
- Cost-effective solution
- Outdoor or remote monitoring
- Multiple camera setups

**When to use USB Webcam:**
- Lowest latency required
- Stationary setup
- Maximum reliability
- Higher resolution needed

## Troubleshooting

### Stream Not Connecting

**Symptom:** `Failed to open video source` error

**Solutions:**
1. Verify ESP32-CAM is powered on (check LED indicator)
2. Confirm WiFi connection in Serial Monitor
3. Test stream in browser: `http://<IP>:81/`
4. Ping ESP32-CAM: `ping 192.168.1.100`
5. Check firewall settings
6. Ensure both devices on same network (not guest network)

### Frequent Disconnections

**Symptom:** "Connection lost. Reconnecting..." messages

**Solutions:**
1. Move ESP32-CAM closer to WiFi router
2. Check WiFi signal strength
3. Use external 5V power supply (not FTDI power)
4. Reduce stream quality in firmware (increase JPEG_QUALITY value)
5. Check router for device connection limits
6. Restart ESP32-CAM and router

### Poor Detection Performance

**Symptom:** Missing objects or false detections

**Solutions:**
1. Increase JPEG quality (lower JPEG_QUALITY value in firmware)
2. Use higher resolution (FRAMESIZE_SVGA or FRAMESIZE_XGA)
3. Improve lighting conditions
4. Adjust confidence threshold: `--confidence 0.35`
5. Clean camera lens
6. Position camera at optimal angle

### High Latency

**Symptom:** 1+ second delay in video feed

**Solutions:**
1. Reduce FRAME_SIZE in ESP32 firmware
2. Increase JPEG_QUALITY value (e.g., 20)
3. Check network bandwidth (close streaming services)
4. Move closer to WiFi router
5. Use 2.4GHz WiFi (not 5GHz) as ESP32 only supports 2.4GHz
6. Restart router to clear congestion

### Stream Freezes

**Symptom:** Video stops updating but doesn't disconnect

**Solutions:**
1. Check ESP32-CAM power supply (needs stable 5V, 2A)
2. Monitor Serial Monitor for error messages
3. Restart ESP32-CAM (press RESET button)
4. Re-upload firmware with updated settings
5. Check for overheating (add small heatsink if needed)

## Advanced Configuration

### Multiple Camera Setup

To use multiple ESP32-CAM modules:

1. Configure each with unique IP (via router DHCP reservation)
2. Run separate instances of main.py:
```bash
# Terminal 1
python main.py --source http://192.168.1.100:81/stream

# Terminal 2
python main.py --source http://192.168.1.101:81/stream
```

### Custom Stream Processing

For advanced users, you can modify the stream handling:

```python
import cv2

# Direct stream access
stream_url = "http://192.168.1.100:81/stream"
cap = cv2.VideoCapture(stream_url)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimize latency

while True:
    ret, frame = cap.read()
    if not ret:
        break
    # Your custom processing here
    cv2.imshow('Stream', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

### Static IP Configuration

For permanent deployment, configure static IP in ESP32 firmware:

```cpp
// Add after WiFi.begin()
IPAddress staticIP(192, 168, 1, 100);
IPAddress gateway(192, 168, 1, 1);
IPAddress subnet(255, 255, 255, 0);
WiFi.config(staticIP, gateway, subnet);
```

## Security Considerations

⚠️ **Important Security Notes:**

1. **No Authentication**: Default setup has no password protection
2. **Local Network Only**: Stream accessible to anyone on same WiFi
3. **Unencrypted**: Video transmitted in plain HTTP (not HTTPS)

**For production deployment:**
- Implement authentication in ESP32 web server
- Use VPN for remote access
- Deploy on isolated network segment
- Consider HTTPS (requires SSL library)

## Testing Checklist

Before deploying, verify:

- [ ] ESP32-CAM connects to WiFi successfully
- [ ] Browser can access `http://<IP>:81/` info page
- [ ] Stream visible in browser at `http://<IP>:81/stream`
- [ ] `test_esp32_stream.py` passes (captures at least one frame)
- [ ] `main.py` runs with `--source http://<IP>:81/stream`
- [ ] Detections work correctly (test with objects)
- [ ] Audio feedback is clear and timely
- [ ] Reconnection works (unplug/replug ESP32-CAM power)
- [ ] Performance is acceptable (check FPS with debug mode)
- [ ] Battery/power setup works for mobile deployment

## Support and Resources

### Documentation
- ESP32-CAM Hardware Setup: `esp32_cam/README.md`
- Main Application Usage: `QUICKSTART.md`
- Project Overview: `README.md`

### External Resources
- ESP32-CAM Datasheet: https://github.com/raphaelbs/esp32-cam-ai-thinker
- OpenCV VideoCapture Docs: https://docs.opencv.org/4.x/d8/dfe/classcv_1_1VideoCapture.html
- YOLOv8 Documentation: https://docs.ultralytics.com/

### Common Issues
- WiFi won't connect → Check SSID/password, ensure 2.4GHz network
- Camera init failed → Reseat camera ribbon cable
- Can't upload firmware → IO0 must be connected to GND during upload
- Black screen → Check camera orientation (remove lens cap if present)

## Future Enhancements

Potential improvements for future versions:

- [ ] HTTPS support for encrypted streams
- [ ] Basic authentication for stream access
- [ ] H.264 streaming for reduced bandwidth
- [ ] Battery voltage monitoring and alerts
- [ ] On-board SD card recording
- [ ] Motion detection to save bandwidth
- [ ] Multiple resolution profiles
- [ ] WebRTC for ultra-low latency

---

**Ready to start?** Follow the setup in `esp32_cam/README.md` and then run:
```bash
python main.py --source http://<YOUR_ESP32_IP>:81/stream
```
