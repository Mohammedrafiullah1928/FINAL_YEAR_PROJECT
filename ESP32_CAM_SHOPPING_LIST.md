# 🛒 ESP32-CAM Shopping List & Quick Start

## 📦 What to Buy

### **Required Components** (~$15-20 total)

| Item | Price | Link Example | Notes |
|------|-------|--------------|-------|
| **ESP32-CAM AI-Thinker** | $7-10 | [Amazon](https://amazon.com/s?k=esp32+cam) | Get with OV2640 camera |
| **FTDI USB Programmer** | $3-5 | [Amazon](https://amazon.com/s?k=ftdi+usb+serial) | 3.3V/5V switchable |
| **Jumper Wires (F-F)** | $2-3 | [Amazon](https://amazon.com/s?k=jumper+wires+female) | Pack of 40 wires |
| **USB Cable (Mini/Micro)** | $2 | [Amazon](https://amazon.com/s?k=usb+cable) | For FTDI power |

### **Optional but Recommended** (~$15-25 extra)

| Item | Price | Purpose |
|------|-------|---------|
| **Power Bank (10000mAh)** | $10-15 | Portable power for 8+ hours |
| **microSD Card (16-32GB)** | $5-8 | Local video storage |
| **Breadboard** | $3-5 | Easier prototyping |
| **Action Camera Mount** | $5-10 | Helmet/dashboard mounting |
| **Waterproof Case** | $5-10 | Outdoor protection |

### **Where to Buy**

1. **Amazon** (Fast shipping, easy returns)
2. **AliExpress** (Cheapest, 2-4 weeks shipping)
3. **eBay** (Good deals, check seller ratings)
4. **Local electronics store** (Immediate, may be pricier)

---

## 🔌 Wiring Diagram

### **Programming Mode**

```
┌────────────────────┐
│  FTDI USB Adapter  │
│                    │
│  [GND] [VCC] [TX]  │
│              [RX]  │
└─┬─────┬─────┬─────┘
  │     │     │  └────┐
  │     │     │       │
  │     │     │       │
┌─┴─────┴─────┴───────┴─────┐
│       ESP32-CAM            │
│                            │
│  [GND] [5V] [U0R] [U0T]   │
│                            │
│  [IO0]─────┐               │
│  [GND]─────┘ (Jumper!)     │
│                            │
│      [OV2640 Camera]       │
└────────────────────────────┘

Connections:
• FTDI GND  → ESP32 GND  (Black wire)
• FTDI VCC  → ESP32 5V   (Red wire)
• FTDI TX   → ESP32 U0R  (Yellow wire)
• FTDI RX   → ESP32 U0T  (Green wire)
• ESP32 IO0 → ESP32 GND  (Blue jumper - UPLOAD ONLY!)
```

### **Normal Operation Mode**

```
┌────────────────────┐
│   Power Source     │
│  (USB/Battery)     │
│                    │
│    [+5V]  [GND]    │
└─────┬──────┬───────┘
      │      │
      │      │
┌─────┴──────┴────────────┐
│       ESP32-CAM          │
│                          │
│    [5V]      [GND]       │
│                          │
│  ⚠️ IO0 NOT connected!  │
│                          │
│     [OV2640 Camera]      │
└──────────────────────────┘

⚠️ IMPORTANT: Remove IO0-to-GND jumper!
```

---

## 📸 ESP32-CAM Pin Reference

```
                    ESP32-CAM Top View
    
    ┌────────────────────────────────────────┐
    │                                        │
    │  [Reset Button]    [Camera Module]    │
    │                                        │
    │  ┌──┐                                  │
    │  │  │  GPIO Pins                       │
    │  └──┘                                  │
    │                                        │
    │  GND   ●  Ground                       │
    │  5V    ●  5V Power Input               │
    │  3.3V  ●  3.3V Output (DO NOT USE)     │
    │  U0R   ●  UART RX (connect to FTDI TX)│
    │  U0T   ●  UART TX (connect to FTDI RX)│
    │  IO0   ●  Programming Mode (GND=Upload)│
    │  IO2   ●  SD Card Data                 │
    │  IO4   ●  Flash LED                    │
    │  ...   ●  (other GPIO pins)            │
    │                                        │
    │  [microSD Card Slot]                   │
    └────────────────────────────────────────┘
```

---

## ⚡ Quick Start Steps

### **Day 1: Hardware Assembly**

1. ✅ Receive all components
2. ✅ Connect FTDI to ESP32-CAM (Programming Mode)
3. ✅ Plug FTDI into computer
4. ✅ Install Arduino IDE
5. ✅ Add ESP32 board support

### **Day 2: Software Setup**

1. ✅ Open `esp32_cam_stream.ino`
2. ✅ Change WiFi SSID and password
3. ✅ Select board: "AI Thinker ESP32-CAM"
4. ✅ Upload firmware
5. ✅ Remove IO0 jumper

### **Day 3: Testing**

1. ✅ Press RESET button
2. ✅ Check Serial Monitor for IP address
3. ✅ Open browser: `http://IP:81`
4. ✅ See live camera feed
5. ✅ Test detection with `esp32_detector.py`

### **Day 4: Integration**

1. ✅ Update `ESP32_STREAM_URL` in `esp32_detector.py`
2. ✅ Start web server: `python web_app/server.py`
3. ✅ Run detector: `python esp32_detector.py`
4. ✅ Open browser: `http://localhost:5000`
5. ✅ Watch detections appear on map!

---

## 🚨 Common Mistakes to Avoid

### ❌ **Don't Do This:**
- Connect 3.3V from FTDI to 5V pin (wrong voltage)
- Swap TX/RX connections (won't upload)
- Forget to remove IO0 jumper (won't boot)
- Use cheap USB cable (power issues)
- Connect to 5GHz WiFi (ESP32 only supports 2.4GHz)

### ✅ **Do This:**
- Use 5V power for stable operation
- Connect TX → RX and RX → TX (crossover)
- Remove IO0 jumper after upload
- Use quality USB cable with data lines
- Use 2.4GHz WiFi network

---

## 📊 Power Consumption

| Mode | Current | Runtime (10000mAh) |
|------|---------|-------------------|
| Streaming | ~400mA | ~25 hours |
| Idle | ~200mA | ~50 hours |
| Deep Sleep | ~6mA | ~2000 hours |

---

## 🎯 Expected Results

### **Serial Monitor Output:**
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

### **Browser View:**
- Clear video stream at 640x480
- ~15-20 FPS (frames per second)
- Low latency (~200-500ms)

### **Detection Output:**
```
✅ Connected! Frame size: 640x480
✅ System ready! Starting detection...

✓ Detected: car (87% confidence, 5.2m away)
⚠️ WARNING: car detected 5.2m ahead
✅ Sent to webapp: car (87%)

⊘ Ignoring: person
Skipping duplicate: car (last seen 15.3s ago)
```

---

## 📞 Need Help?

### **Upload Issues:**
- Check: [ESP32_CAM_HARDWARE_GUIDE.md](ESP32_CAM_HARDWARE_GUIDE.md) - Troubleshooting section
- Forum: [Arduino ESP32 Community](https://forum.arduino.cc/c/hardware/esp32/83)

### **Connection Issues:**
- Verify: WiFi SSID and password correct
- Check: 2.4GHz network (not 5GHz)
- Test: Ping ESP32-CAM IP address

### **Detection Issues:**
- Ensure: Web server running (`python web_app/server.py`)
- Update: ESP32_STREAM_URL with correct IP
- Check: Camera has clear view of obstacles

---

## ✅ Checklist Before First Run

- [ ] ESP32-CAM purchased and received
- [ ] FTDI adapter purchased and received
- [ ] Jumper wires available
- [ ] Arduino IDE installed
- [ ] ESP32 board support added
- [ ] WiFi credentials configured in code
- [ ] Firmware uploaded successfully
- [ ] IO0 jumper removed
- [ ] IP address noted from Serial Monitor
- [ ] Browser shows camera stream
- [ ] Web server running
- [ ] esp32_detector.py URL updated
- [ ] Detection script tested

---

## 🎉 You're Ready to Build!

Follow the steps in order, and you'll have a working ESP32-CAM system integrated with your pedestrian navigation app!

**Total Time:** 1-2 hours for complete setup
**Skill Level:** Beginner-friendly with detailed instructions

**Let's build this! 🚀**
