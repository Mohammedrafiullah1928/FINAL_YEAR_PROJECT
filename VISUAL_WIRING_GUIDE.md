# 🔌 Visual Wiring & Assembly Guide
## ESP32-CAM Pedestrian Navigation System

---

## 📦 **COMPONENTS YOU NEED**

### **Required:**
1. ✅ ESP32-CAM Module (AI-Thinker)
2. ✅ FTDI USB-to-Serial Programmer (3.3V/5V)
3. ✅ 10 x Female-to-Female Jumper Wires
4. ✅ Power Bank (10,000mAh with USB output)
5. ✅ USB Cable (compatible with power bank)
6. ✅ Baseball Cap or similar headwear
7. ✅ Computer with Arduino IDE

### **Optional:**
8. ⭕ Mini Breadboard
9. ⭕ Bluetooth Audio Module (HC-05/JDY-62)
10. ⭕ Bluetooth Earpiece/Speaker
11. ⭕ Velcro Strips
12. ⭕ Small Project Box (for ESP32 protection)

---

## 🔌 **WIRING DIAGRAMS**

### **STEP 1: Programming Setup (On Desktop)**

```
┌─────────────────────────────────────────────────────────────┐
│                    PROGRAMMING MODE                         │
│                                                             │
│   FTDI Adapter                     ESP32-CAM               │
│   ┌──────────┐                    ┌──────────┐            │
│   │          │                    │          │            │
│   │  [GND]   ├──────BLACK─────────┤  GND     │            │
│   │          │                    │          │            │
│   │  [VCC]   ├──────RED───────────┤  5V      │            │
│   │  (5V)    │                    │          │            │
│   │          │                    │          │            │
│   │  [TX]    ├──────YELLOW────────┤  U0R     │            │
│   │          │                    │  (RX)    │            │
│   │          │                    │          │            │
│   │  [RX]    ├──────GREEN─────────┤  U0T     │            │
│   │          │                    │  (TX)    │            │
│   │          │                    │          │            │
│   │  [USB]   │◄────TO COMPUTER────┤          │            │
│   │          │                    │          │            │
│   └──────────┘                    │  IO0 ────┼──┐         │
│                                   │          │  │         │
│                              BLUE │  GND ────┼──┘         │
│                           (UPLOAD │          │  JUMPER    │
│                            ONLY!) └──────────┘            │
│                                                             │
└─────────────────────────────────────────────────────────────┘

⚠️ IMPORTANT: 
- Connect IO0 to GND ONLY during upload
- Remove this jumper after uploading code!
- TX and RX are crossed (FTDI TX → ESP32 RX)
```

### **STEP 2: Normal Operation (Portable)**

```
┌─────────────────────────────────────────────────────────────┐
│                    NORMAL OPERATION                         │
│                                                             │
│   Power Bank                       ESP32-CAM               │
│   ┌──────────┐                    ┌──────────┐            │
│   │          │                    │          │            │
│   │  [USB]   ├──── USB CABLE ─────┤  5V      │            │
│   │  OUTPUT  │                    │          │            │
│   │          │                    │  GND     │            │
│   │  10000mAh│                    │          │            │
│   │          │                    │ (CAMERA) │            │
│   │  [●●●●]  │                    │  ◉ ◉     │            │
│   │  [POWER] │                    │          │            │
│   └──────────┘                    └──────────┘            │
│                                                             │
│   ⚠️ REMOVE IO0-to-GND jumper!                             │
│   ✅ ESP32-CAM should start automatically                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### **STEP 3: With Bluetooth Audio (Advanced)**

```
┌─────────────────────────────────────────────────────────────┐
│               WITH BLUETOOTH MODULE                         │
│                                                             │
│   Bluetooth Module                 ESP32-CAM               │
│   (HC-05/JDY-62)                                           │
│   ┌──────────┐                    ┌──────────┐            │
│   │          │                    │          │            │
│   │  [VCC]   ├──────RED───────────┤  3.3V    │⚠️ NOT 5V! │
│   │          │                    │          │            │
│   │  [GND]   ├──────BLACK─────────┤  GND     │            │
│   │          │                    │          │            │
│   │  [RX]    ├──────YELLOW────────┤  GPIO12  │            │
│   │          │                    │  (TX2)   │            │
│   │          │                    │          │            │
│   │  [TX]    ├──────GREEN─────────┤  GPIO13  │            │
│   │          │                    │  (RX2)   │            │
│   └──────────┘                    └──────────┘            │
│       │                                                     │
│       └────────PAIRS WITH──────►  [Bluetooth Earpiece]    │
│                                                             │
└─────────────────────────────────────────────────────────────┘

⚠️ CRITICAL: Bluetooth module MUST use 3.3V, NOT 5V!
            Using 5V will damage the module!
```

---

## 🎓 **COLOR-CODED WIRE GUIDE**

| Wire Color | Connection | Purpose |
|------------|------------|---------|
| 🔴 RED | Power (5V or 3.3V) | Supplies power |
| ⚫ BLACK | Ground (GND) | Common ground |
| 🟡 YELLOW | Data (TX/RX) | Serial communication |
| 🟢 GREEN | Data (RX/TX) | Serial communication |
| 🔵 BLUE | Control (IO0) | Upload mode (temporary) |

---

## 🏗️ **STEP-BY-STEP ASSEMBLY**

### **Phase 1: Desktop Testing (Before Wearable)**

#### **1. Prepare Components**
```
Lay out on table:
├── ESP32-CAM module
├── FTDI adapter
├── 5 jumper wires
├── Computer with Arduino IDE
└── USB cable
```

#### **2. Make Connections**
```
Order of connection (important!):
1. GND first (black wire) - safety
2. Power (red wire) - 5V to 5V
3. TX to RX (yellow wire) - data
4. RX to TX (green wire) - data
5. IO0 to GND (blue wire) - upload mode only
```

#### **3. Physical Layout on Breadboard**
```
         FTDI              Breadboard              ESP32-CAM
      [========]          [----------]           [============]
      │ USB-PC │          │          │           │  ┌──┐      │
      └────┬───┘          │  Jumpers │           │  │▓▓│ Cam  │
           │              │   Cross  │           │  └──┘      │
           └──────────────┼─ here ───┼───────────┘            │
                          [----------]                         │
                                                               │
      Use breadboard to organize wires neatly                 │
```

#### **4. Upload Code Checklist**
```
☐ All 5 wires connected correctly
☐ IO0 connected to GND (blue jumper)
☐ FTDI plugged into computer USB
☐ Arduino IDE open with correct settings
☐ Board: "AI Thinker ESP32-CAM"
☐ Port: Selected (COM3, COM4, etc.)
☐ WiFi credentials updated in code
☐ Click Upload button
☐ Press RESET when "Connecting..." appears
☐ Wait for "Hard resetting..." message
☐ SUCCESS! ✅
```

#### **5. First Run Test**
```
☐ REMOVE IO0-to-GND jumper
☐ Press RESET button on ESP32-CAM
☐ Open Serial Monitor (115200 baud)
☐ See "WiFi connected!" message
☐ Note IP address (e.g., 192.168.1.100)
☐ Open browser: http://IP:81
☐ See live camera feed
☐ SUCCESS! Camera works! ✅
```

---

### **Phase 2: Wearable Assembly**

#### **6. Prepare Cap Mount**

```
Top View of Cap:
┌────────────────────────────────────┐
│                                    │
│    [BRIM]                          │
│     ┌──┐  ← Mount ESP32 here       │
│     │▓▓│    (front center of brim) │
│     └──┘                           │
│      ↓                             │
│   Camera lens points forward       │
│   and slightly down                │
└────────────────────────────────────┘

Side View:
     ┌─┐ ← Head
     │ │
   ┌─────┐
   │ CAP │
   └──┬──┘
      │ ESP32-CAM
     [▓]
      │ Camera points ~15° down
      ↓ to see path ahead
   [Path]
```

#### **7. Mounting Options**

**Option A: Velcro Mount (Easiest)**
```
1. Clean cap brim surface
2. Stick "hook" Velcro on cap brim
3. Stick "loop" Velcro on ESP32 back
   (or small plastic box containing ESP32)
4. Press together
5. Adjust camera angle
6. Test: Tilt head, camera should stay secure
```

**Option B: Clip Mount**
```
1. Use binder clip or similar
2. Attach to cap brim
3. Clip holds ESP32-CAM
4. More adjustable than Velcro
```

**Option C: 3D Printed (Best)**
```
1. Design clip for cap brim
2. 3D print
3. Snap onto brim
4. Secure ESP32-CAM inside
5. Professional look!
```

#### **8. Wire Routing**

```
             [Head with Cap]
                  ↓
          [ESP32-CAM on Brim]
                  ↓
             (USB Wire)
                  ↓ 
    Run down side of head/neck
                  ↓
         Clip to shirt collar
                  ↓
           Inside shirt/jacket
                  ↓
      [Power Bank in Pocket]

Tips:
- Use cable clips every 10cm
- Avoid wire crossing face
- Leave slack near neck (for head movement)
- Secure at shoulder to prevent pulling
```

---

### **Phase 3: Complete System Setup**

#### **9. Computer/Laptop Setup**

```
Laptop/Computer in Backpack:
├── Python detection running
├── Audio alerts via Bluetooth earbuds
├── Web server for guardian
└── Connected to same WiFi as ESP32-CAM

OR

Phone Setup (Advanced):
├── Termux app with Python
├── Run detection on phone
├── Audio via phone speaker/earbuds
└── More portable!
```

#### **10. Guardian Dashboard Access**

```
Guardian's Phone:
1. Connect to same WiFi
2. Open browser
3. Go to: http://COMPUTER_IP:5000
4. View live map and camera
5. Monitor user's path
6. Get alerts for obstacles

Example:
http://192.168.1.50:5000
```

---

## 🔋 **POWER MANAGEMENT**

### **Battery Life Calculation**

```
ESP32-CAM Power Consumption:
├── Streaming video: ~300-500mA
├── WiFi active: ~120mA
└── Camera sensor: ~150-200mA
    ─────────────────────────
    TOTAL: ~600-800mA average

Power Bank Capacity:
10,000mAh ÷ 700mA = ~14 hours theoretical
Actual runtime: ~8-10 hours (accounting for efficiency)

Tips for Longer Battery:
- Reduce frame rate (edit FRAME_RATE in code)
- Lower resolution (FRAMESIZE_HVGA instead of VGA)
- Increase DETECTION_INTERVAL (check less frequently)
- Use 20,000mAh power bank for full day use
```

### **Charging Strategy**

```
Daily Routine:
├── Night: Charge power bank
├── Morning: Connect ESP32-CAM
├── Use: 8-10 hours
├── Evening: Disconnect, recharge
└── Backup: Keep second power bank ready
```

---

## 📏 **CAMERA POSITIONING**

### **Optimal Angles**

```
Head-on View:            Top View:
                    
     [Human]              [Human]
       ⊙ ⊙               ┌──┬──┐
       ╲ ╱                │  │  │
        ▽                 │◄─┴─►│
    ╱ ╲ │ ╱ ╲               90° FOV
   ╱   ╲│╱   ╲              (field of view)
  ╱     ▼     ╱
 ╱   Vision   ╱
╱    Cone    ╱

Camera Tilt: 10-15° downward
Why: To see path 2-5 meters ahead
Too high: Only sees far objects
Too low: Only sees ground at feet
```

### **Testing Camera Angle**

```
Setup Test:
1. Mount camera on cap
2. Wear cap
3. Stand 3 meters from wall
4. View stream on phone/laptop
5. Adjust until you see:
   - Ground at bottom 1/3 of frame
   - Horizon at top 1/3 of frame
   - Objects 2-5m ahead clearly visible
6. Lock position with tape/glue
```

---

## 🎧 **AUDIO SYSTEM OPTIONS**

### **Option 1: Computer + Bluetooth Earbuds**

```
[ESP32-CAM] ─WiFi─► [Laptop in Backpack] ─Bluetooth─► [Earbuds]
                         │
                         └─► Runs Python detection
                         └─► Generates audio alerts
                         └─► Plays through earbuds

Pros:
✅ Easy setup (no extra hardware)
✅ Works with existing code
✅ High-quality audio
✅ Longer battery (laptop battery)

Cons:
❌ Must carry laptop/tablet
❌ More weight
```

### **Option 2: Phone + Mobile Hotspot**

```
[ESP32-CAM] ─WiFi─► [Phone WiFi Hotspot] ─Apps─► [Phone Speaker]
                         │
                         └─► Phone runs Termux + Python
                         └─► Detection on phone
                         └─► Audio from phone

Pros:
✅ More portable
✅ Phone battery adequate
✅ All-in-one device

Cons:
❌ Requires Termux setup (advanced)
❌ Phone battery drains faster
```

### **Option 3: ESP32 + Bluetooth Module (Future)**

```
[ESP32-CAM] ─Internal─► [Bluetooth Module] ─Bluetooth─► [Earpiece]
                              │
                              └─► Pre-recorded alerts
                              └─► Direct from ESP32

Pros:
✅ No computer needed
✅ Most portable
✅ Longest battery

Cons:
❌ Complex programming
❌ Limited to pre-recorded messages
❌ No real-time detection (would need edge AI)
```

---

## 🧪 **TESTING PROTOCOL**

### **Test 1: Component Test (Desktop)**
```
☐ ESP32-CAM powers on (red LED)
☐ Connects to WiFi
☐ Camera stream visible in browser
☐ Single capture works (/capture endpoint)
☐ Status endpoint returns JSON
☐ Python can connect to stream
☐ YOLO detection runs
☐ Audio alerts play
```

### **Test 2: Wearable Test (Indoor)**
```
☐ Camera stays mounted on cap
☐ Wire routing comfortable
☐ Power bank secure in pocket
☐ No loose wires
☐ Camera angle correct
☐ WiFi maintains connection
☐ Detection works while walking
☐ Audio clear while moving
```

### **Test 3: Outdoor Test (Supervised)**
```
☐ System works outdoors
☐ Detects real obstacles (stairs, curbs)
☐ Audio alerts timely
☐ Battery lasts expected duration
☐ Guardian can monitor
☐ User comfortable wearing system
☐ No overheating
☐ WiFi range adequate
```

### **Test 4: Real-World Scenario**
```
☐ Complete morning routine (5 min setup)
☐ Walk familiar route
☐ System alerts on known obstacles
☐ Guardian monitors successfully
☐ User navigates safely
☐ Battery lasts full session
☐ Easy to remove/store
```

---

## ⚠️ **SAFETY NOTES**

### **Electrical Safety**
```
⚡ DO:
✅ Use proper voltage (3.3V or 5V as specified)
✅ Check connections before powering on
✅ Use insulated wires
✅ Avoid water/moisture
✅ Disconnect when not in use

⚡ DON'T:
❌ Mix up voltage (5V on 3.3V pin = damage!)
❌ Short circuit power and ground
❌ Use damaged wires
❌ Operate in rain without waterproofing
❌ Leave powered on unattended (first tests)
```

### **User Safety**
```
🦯 CRITICAL:
⚠️ This system is an AID, not a replacement!
⚠️ User must still use cane/guide dog
⚠️ Test thoroughly before relying on it
⚠️ Always have guardian monitor initially
⚠️ Don't use in dangerous areas until proven
⚠️ Have emergency contact accessible
```

---

## 🎯 **QUICK TROUBLESHOOTING**

| Problem | Quick Fix |
|---------|-----------|
| **No power** | Check USB connection, try different power bank port |
| **No WiFi** | Check SSID/password in code, ensure 2.4GHz network |
| **No video** | Press RESET button, check camera ribbon cable |
| **Upload fails** | Ensure IO0-GND jumper connected, press RESET |
| **Hot ESP32** | Normal, reduce frame rate if too hot to touch |
| **Audio delays** | Reduce detection interval, check WiFi signal |
| **Camera loose** | Add more Velcro, use hot glue for permanent mount |
| **Battery drains fast** | Lower frame rate, use bigger power bank |

---

## 📋 **FINAL ASSEMBLY CHECKLIST**

```
Hardware:
☐ ESP32-CAM programmed with WiFi code
☐ Mounted securely on cap
☐ Camera angle adjusted (10-15° down)
☐ Wire routed and secured
☐ Power bank charged
☐ USB cable connected
☐ All connections tested

Software:
☐ Python environment set up
☐ YOLOv8 model downloaded
☐ esp32_detector.py configured with ESP32 IP
☐ Web server tested
☐ Guardian can access dashboard
☐ Audio alerts working

Safety:
☐ User trained on system
☐ Guardian monitoring set up
☐ Emergency contacts configured
☐ Backup power available
☐ Safe test route planned

Ready to Go:
☐ Morning setup takes <5 minutes
☐ User comfortable wearing system
☐ Detection accurate
☐ Audio clear
☐ Guardian monitoring
☐ Battery lasts needed duration

🎉 SYSTEM READY FOR DEPLOYMENT! 🎉
```

---

## 📞 **NEED HELP?**

Refer to these project files:
- `COMPLETE_IMPLEMENTATION_GUIDE.md` - Detailed instructions
- `ESP32_CAM_HARDWARE_GUIDE.md` - Hardware specifics
- `QUICKSTART.md` - Quick reference
- `README.md` - Project overview

**Remember:** Take it step by step, test at each phase, and prioritize safety! 🚀
