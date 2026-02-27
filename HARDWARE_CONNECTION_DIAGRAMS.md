# 🔌 Complete Hardware Connection Diagrams
## ESP32-CAM Pedestrian Navigation System

---

## 📋 **TABLE OF CONTENTS**

1. [Programming Setup (FTDI Connection)](#programming-setup)
2. [Normal Operation - Power Bank](#power-bank-setup)
3. [Normal Operation - 18650 Batteries](#battery-setup)
4. [Optional Bluetooth Audio](#bluetooth-audio)
5. [Complete Wearable Assembly](#wearable-assembly)
6. [Pin Reference Tables](#pin-reference)

---

## 🔧 **PROGRAMMING SETUP (FTDI Connection)**

### **Use This For:** Uploading code to ESP32-CAM

```
╔═══════════════════════════════════════════════════════════════╗
║               PROGRAMMING MODE - FTDI CONNECTION              ║
╚═══════════════════════════════════════════════════════════════╝

        FTDI USB Adapter                    ESP32-CAM Module
    ┌─────────────────────┐            ┌──────────────────────┐
    │                     │            │                      │
    │   GND ●             │────────────│ ● GND                │
    │       │             │  Black     │                      │
    │   VCC ●             │────────────│ ● 5V                 │
    │  (5V) │             │  Red       │                      │
    │    TX ●             │────────────│ ● U0R (RX)           │
    │       │             │  Yellow    │                      │
    │    RX ●             │────────────│ ● U0T (TX)           │
    │       │             │  Green     │                      │
    │       │             │            │                      │
    │  [USB]──┐           │            │   ┌─────────┐        │
    │         │           │            │   │ CAMERA  │        │
    └─────────┼───────────┘            │   │  ● ●    │        │
              │                        │   └─────────┘        │
              │                        │                      │
         To Computer                   │  IO0 ●               │
              │                        │      │               │
              │                        │  GND ●───┐           │
              │                        │      Blue│           │
              └────────────────────────┤          │           │
                                       │      Jumper          │
                                       │  (Upload Only!)      │
                                       └──────────────────────┘

╔═══════════════════════════════════════════════════════════════╗
║                    CONNECTION TABLE                           ║
╠═══════════════════════╦═══════════════╦══════════════════════╣
║ FTDI Pin              ║ Wire Color    ║ ESP32-CAM Pin        ║
╠═══════════════════════╬═══════════════╬══════════════════════╣
║ GND (Ground)          ║ Black         ║ GND                  ║
║ VCC (5V)              ║ Red           ║ 5V                   ║
║ TX (Transmit)         ║ Yellow        ║ U0R (Receive)        ║
║ RX (Receive)          ║ Green         ║ U0T (Transmit)       ║
║ ---                   ║ Blue          ║ IO0 to GND           ║
╚═══════════════════════╩═══════════════╩══════════════════════╝

⚠️  CRITICAL NOTES:
    1. TX and RX are CROSSED (TX → RX, RX → TX)
    2. IO0 to GND jumper ONLY for upload mode
    3. Remove IO0-GND jumper after uploading!
    4. Set FTDI to 5V mode (if switchable)
```

### **Step-by-Step Connection:**

```
Step 1: Place Components on Table
┌────────┐         ┌──────────┐
│  FTDI  │         │ ESP32-CAM│
│Adapter │         │  Module  │
└────────┘         └──────────┘

Step 2: Connect Ground First (Safety)
    FTDI                ESP32-CAM
     GND ●──────Black────● GND
         └──────────────────┘

Step 3: Connect Power
    FTDI                ESP32-CAM
     5V  ●──────Red──────● 5V
         └──────────────────┘

Step 4: Connect Data Lines (CROSSED!)
    FTDI                ESP32-CAM
     TX  ●────Yellow────● U0R (RX)
         └──────────────────┘
     RX  ●────Green─────● U0T (TX)
         └──────────────────┘

Step 5: Add Upload Mode Jumper
    ESP32-CAM Only
     IO0 ●──────Blue────● GND
         └──────────────┘
    (Connect IO0 to GND for programming)

Step 6: Connect USB
    FTDI ──── USB Cable ──── Computer

✅ Ready to Upload!
```

---

## 🔋 **NORMAL OPERATION - POWER BANK**

### **Use This For:** Daily use with power bank (easiest option)

```
╔═══════════════════════════════════════════════════════════════╗
║            POWER BANK SETUP - NORMAL OPERATION                ║
╚═══════════════════════════════════════════════════════════════╝

    Power Bank (10,000mAh)                ESP32-CAM Module
    ┌─────────────────────┐          ┌──────────────────────┐
    │                     │          │                      │
    │   [■■■■■■■■]        │          │                      │
    │   Battery Level     │          │   ┌─────────┐        │
    │                     │          │   │ CAMERA  │        │
    │   USB Output:       │          │   │  ● ●    │        │
    │   ┌────────┐        │          │   └─────────┘        │
    │   │  USB-A │        │          │                      │
    │   └───┬────┘        │          │                      │
    │       │             │          │                      │
    │   [Power Button]    │          │  5V  ●               │
    │                     │          │      │               │
    └───────┼─────────────┘          │  GND ●               │
            │                        │      │               │
            │ USB Cable              └──────┼───────────────┘
            │ (Micro or Mini-USB)           │
            │                               │
            └───────────────────────────────┘

METHOD 1: Using FTDI as Power Adapter
────────────────────────────────────────

Power Bank ──USB──► FTDI Adapter ──Wires──► ESP32-CAM
                    (Used as 5V converter)
                    
    Connections:
    • FTDI VCC (5V) → ESP32-CAM 5V
    • FTDI GND     → ESP32-CAM GND
    • TX/RX not connected (data not needed)


METHOD 2: USB to Bare Wire Cable (Better)
────────────────────────────────────────

Power Bank ──USB Cable with bare ends──► ESP32-CAM
             (Cut open USB cable or buy USB breakout)
             
    Connections:
    • USB Red (+5V)   → ESP32-CAM 5V
    • USB Black (GND) → ESP32-CAM GND
    • Green/White not needed


⚠️  REMOVE IO0-GND JUMPER!
    System should boot automatically when powered.
```

### **USB Cable Wiring:**

```
Standard USB Cable Pinout:
┌────────────────────────────────────┐
│  Looking at USB-A Connector        │
│  (Metal connector facing you)      │
│                                    │
│   ┌─────────────────────┐          │
│   │  1  2  3  4         │          │
│   └─────────────────────┘          │
│                                    │
│   Pin 1: +5V     (Red wire)        │
│   Pin 2: Data-   (White wire)      │
│   Pin 3: Data+   (Green wire)      │
│   Pin 4: GND     (Black wire)      │
│                                    │
│   For Power Only: Use Pin 1 & 4   │
└────────────────────────────────────┘

Cut USB Cable and Connect:
    Red wire   → ESP32-CAM 5V
    Black wire → ESP32-CAM GND
    (White/Green not needed)
```

---

## 🔋 **NORMAL OPERATION - 18650 BATTERIES (RECOMMENDED)**

### **Use This For:** Lightweight wearable setup (55% lighter!)

```
╔═══════════════════════════════════════════════════════════════╗
║         18650 BATTERY SETUP WITH BUCK CONVERTER               ║
╚═══════════════════════════════════════════════════════════════╝

18650 Battery Holder          Buck Converter         ESP32-CAM
┌─────────────────┐         ┌──────────────┐      ┌──────────┐
│                 │         │              │      │          │
│  [████] 3.7V    │         │   IN+  OUT+  │      │  ┌────┐  │
│  [████] 3.7V    │         │    ●────●    │      │  │ ●● │  │
│                 │         │              │      │  └────┘  │
│  Series = 7.4V  │         │   IN-  OUT-  │      │  Camera  │
│                 │         │    ●────●    │      │          │
│  ┌───────────┐  │         │              │      │  5V ●    │
│  │ON    OFF  │  │         │  [Adjust]    │      │     │    │
│  │ ●────○    │◄─┼─────────│   Screw      │      │  GND●    │
│  └───────────┘  │         │              │      │     │    │
│   Switch        │         │   Mini360    │      └─────┼────┘
└────┬────────┬───┘         │   LM2596     │            │
     │        │             └───┬────┬─────┘            │
     │ +      │ -               │    │                  │
     │ Red    │ Black           │    │                  │
     │        │                 │    │                  │
     │        └─────────────────┘    │                  │
     │                  Black        │ Red              │
     └──────────────────────────────────────────────────┘

╔═══════════════════════════════════════════════════════════════╗
║                    CONNECTION SEQUENCE                        ║
╠═══════════════════╦═══════════════╦═════════════════════════╣
║ From              ║ Wire Color    ║ To                      ║
╠═══════════════════╬═══════════════╬═════════════════════════╣
║ Battery + (Red)   ║ Red           ║ Buck Converter IN+      ║
║ Battery - (Black) ║ Black         ║ Buck Converter IN-      ║
║ Buck OUT+ (Red)   ║ Red           ║ ESP32-CAM 5V            ║
║ Buck OUT- (Black) ║ Black         ║ ESP32-CAM GND           ║
╚═══════════════════╩═══════════════╩═════════════════════════╝

⚠️  SETUP BUCK CONVERTER FIRST!
    1. Connect batteries to buck INPUT
    2. Turn on switch
    3. Measure OUTPUT with multimeter
    4. Adjust screw until output = 5.0V exactly
    5. Turn off, disconnect
    6. Connect to ESP32-CAM
    7. Test!
```

### **Buck Converter Detail:**

```
╔═══════════════════════════════════════════════════════════════╗
║              BUCK CONVERTER (Mini360 / LM2596)                ║
╚═══════════════════════════════════════════════════════════════╝

Top View:
┌─────────────────────────────────────┐
│                                     │
│     ●  IN+   [Chip]    OUT+  ●      │
│                                     │
│                [✚]                  │ ← Adjustment screw
│                                     │   Turn clockwise: ↑V
│                                     │   Turn counter:   ↓V
│     ●  IN-             OUT-  ●      │
│                                     │
└─────────────────────────────────────┘

BEFORE connecting ESP32:
1. Connect INPUT: 7.4V from batteries
2. Measure OUTPUT with multimeter
3. Adjust screw slowly
4. Target: Exactly 5.0V (±0.05V)
5. Verify voltage is stable
6. Then connect to ESP32-CAM
```

### **Detailed Step-by-Step:**

```
STEP 1: Prepare Batteries
─────────────────────────
☐ Charge 2x 18650 batteries to 4.2V each
☐ Insert into holder (check +/- polarity!)
☐ Series connection: + of cell1 to - of cell2
☐ Total voltage: 7.4V
☐ Switch: OFF position

STEP 2: Connect Buck Converter Input
────────────────────────────────────
☐ Battery holder RED wire    → Buck IN+
☐ Battery holder BLACK wire  → Buck IN-
☐ Do NOT turn on yet!

STEP 3: Adjust Buck Converter Output
────────────────────────────────────
☐ Get multimeter ready
☐ Set multimeter to DC voltage (20V range)
☐ Connect multimeter probes to Buck OUT+ and OUT-
☐ Turn battery switch ON
☐ Read voltage on multimeter
☐ Use small screwdriver to adjust
   • Clockwise = increase voltage
   • Counter-clockwise = decrease voltage
☐ Adjust until multimeter reads: 5.00V
☐ Turn battery switch OFF
☐ Remove multimeter

STEP 4: Connect to ESP32-CAM
────────────────────────────
☐ Buck converter OUT+ (Red)   → ESP32-CAM 5V pin
☐ Buck converter OUT- (Black) → ESP32-CAM GND pin
☐ Secure connections (solder or reliable connectors)
☐ Double-check polarity!

STEP 5: First Power-On Test
───────────────────────────
☐ Turn battery switch ON
☐ ESP32-CAM red LED lights up immediately
☐ Press RESET button
☐ System boots (check Serial Monitor)
☐ Success! ✅

If LED doesn't light:
☐ Check all connections
☐ Verify buck converter output is 5V
☐ Check battery voltage (should be >6V)
☐ Verify polarity (red to 5V, black to GND)
```

---

## 🎧 **OPTIONAL: BLUETOOTH AUDIO MODULE**

### **Use This For:** Direct audio from ESP32 (advanced)

```
╔═══════════════════════════════════════════════════════════════╗
║           BLUETOOTH MODULE (HC-05 or JDY-62)                  ║
╚═══════════════════════════════════════════════════════════════╝

    ESP32-CAM                      Bluetooth Module
┌──────────────────┐            ┌────────────────────┐
│                  │            │    HC-05 / JDY-62  │
│  GPIO12 (TX2) ●  │────Yellow──│ ● RX               │
│               │  │            │                    │
│  GPIO13 (RX2) ●  │────Green───│ ● TX               │
│               │  │            │                    │
│  3.3V         ●  │────Red─────│ ● VCC              │
│               │  │            │                    │
│  GND          ●  │────Black───│ ● GND              │
│                  │            │                    │
│   ┌─────────┐   │            │  [Antenna]         │
│   │ CAMERA  │   │            │  [Status LED]      │
│   │  ● ●    │   │            │                    │
│   └─────────┘   │            └────────────────────┘
└──────────────────┘                    │
                                        │ Pairs with
                                        ▼
                              ┌─────────────────┐
                              │ Bluetooth       │
                              │ Earpiece/Speaker│
                              └─────────────────┘

╔═══════════════════════════════════════════════════════════════╗
║                    CONNECTION TABLE                           ║
╠═══════════════════╦═══════════════╦══════════════════════════╣
║ ESP32-CAM Pin     ║ Wire Color    ║ Bluetooth Module Pin     ║
╠═══════════════════╬═══════════════╬══════════════════════════╣
║ GPIO12 (TX2)      ║ Yellow        ║ RX                       ║
║ GPIO13 (RX2)      ║ Green         ║ TX                       ║
║ 3.3V              ║ Red           ║ VCC (⚠️ NOT 5V!)         ║
║ GND               ║ Black         ║ GND                      ║
╚═══════════════════╩═══════════════╩══════════════════════════╝

⚠️  CRITICAL: Bluetooth module uses 3.3V, NOT 5V!
    Using 5V will damage the module permanently!
```

---

## 👔 **COMPLETE WEARABLE ASSEMBLY**

### **Full System Integration:**

```
╔═══════════════════════════════════════════════════════════════╗
║               COMPLETE WEARABLE SYSTEM                        ║
╚═══════════════════════════════════════════════════════════════╝

                    ┌────────────────┐
                    │   Baseball Cap │
                    │                │
                    │  ┌──────────┐  │
                    │  │ESP32-CAM │  │ ← Mounted on brim
                    │  │  ● ●     │  │    Camera faces forward
                    │  └────┬─────┘  │
                    └───────┼────────┘
                            │
                            │ USB/Power Cable
                            │ (Runs down side)
                            │
                    ┌───────┼────────┐
                    │       │        │
                    │   Clip here    │ ← Shirt collar
                    │       │        │
                    └───────┼────────┘
                            │
                            │ (Inside shirt)
                            │
                    ┌───────┼────────┐
                    │       ▼        │
                    │  ┌─────────┐   │ ← Front pocket
                    │  │Battery  │   │    or belt pouch
                    │  │Pack     │   │
                    │  │[ON/OFF] │   │
                    │  └─────────┘   │
                    └────────────────┘

Additional Components:
┌──────────────────────────────────────┐
│  Laptop/Phone in Backpack:           │
│  • Runs Python detection             │
│  • Connects via WiFi                 │
│  • Generates audio alerts            │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│  Bluetooth Earbuds:                  │
│  • Paired with laptop/phone          │
│  • Receives audio warnings           │
│  • User hears "Warning! Stairs!"     │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│  Guardian's Phone:                   │
│  • Connects to web dashboard         │
│  • Monitors user location            │
│  • Views live camera feed            │
└──────────────────────────────────────┘
```

### **Physical Layout:**

```
TOP VIEW (Looking Down):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

               [Head]
                 │
        ┌────────┴────────┐
        │   Baseball Cap   │
        │   ┌────────┐    │
        │   │ESP32CAM│◄───┼─── Camera points forward
        │   └───┬────┘    │
        └───────┼─────────┘
                │
            [Wire runs down]
                │
        ┌───────┴─────────┐
        │   Shirt/Jacket   │
        │       │          │
        │   [Pocket]       │
        │   ┌─────┐        │
        │   │Batt │        │
        │   └─────┘        │
        └──────────────────┘

SIDE VIEW:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        ┌─┐
        │●│ ← Head
        └┬┘
      ┌──┴──┐
      │ Cap │
      └──┬──┘
     [ESP32]
         │   Camera points 15° down
         │   to see path ahead
         ↓
      ═══════ ← Ground level
     [Path]
```

### **Wire Management:**

```
CABLE ROUTING:
══════════════

1. From ESP32-CAM on cap
   └─► Down temple/side of head
   
2. Behind/around ear
   └─► Down neck
   
3. Clip to shirt collar
   └─► Prevents pulling
   
4. Run inside shirt/jacket
   └─► Hidden, protected
   
5. Exit at pocket level
   └─► Connect to battery pack

Use cable clips every 10-15cm:
┌────┐  ┌────┐  ┌────┐
│Clip│  │Clip│  │Clip│
└─┬──┘  └─┬──┘  └─┬──┘
  │       │       │
══╪═══════╪═══════╪══ Cable
  │       │       │
```

---

## 📊 **PIN REFERENCE TABLES**

### **ESP32-CAM Pinout:**

```
╔═══════════════════════════════════════════════════════════════╗
║                ESP32-CAM PIN REFERENCE                        ║
╠════════════╦══════════════╦═════════════════════════════════╣
║ Pin Name   ║ Function     ║ Notes                           ║
╠════════════╬══════════════╬═════════════════════════════════╣
║ 5V         ║ Power Input  ║ Connect to 5V power source      ║
║ GND        ║ Ground       ║ Common ground                   ║
║ 3.3V       ║ Power Output ║ For 3.3V devices (BT module)    ║
║ U0R (RX)   ║ Serial RX    ║ Connect to FTDI TX (crossed)    ║
║ U0T (TX)   ║ Serial TX    ║ Connect to FTDI RX (crossed)    ║
║ IO0        ║ Boot Mode    ║ Connect to GND for upload only  ║
║ GPIO12     ║ TX2          ║ For Bluetooth module TX         ║
║ GPIO13     ║ RX2          ║ For Bluetooth module RX         ║
║ GPIO4      ║ Flash LED    ║ Built-in flash (optional)       ║
║ RESET      ║ Reset Button ║ Press to restart ESP32          ║
╚════════════╩══════════════╩═════════════════════════════════╝
```

### **Power Requirements:**

```
╔═══════════════════════════════════════════════════════════════╗
║                POWER SPECIFICATIONS                           ║
╠════════════════════╦══════════════════════════════════════════╣
║ Parameter          ║ Value                                    ║
╠════════════════════╬══════════════════════════════════════════╣
║ Input Voltage      ║ 5V (±0.25V acceptable)                   ║
║ Current (Idle)     ║ ~180mA                                   ║
║ Current (WiFi)     ║ ~120-180mA additional                    ║
║ Current (Camera)   ║ ~200-250mA additional                    ║
║ Current (Stream)   ║ ~400-600mA total                         ║
║ Peak Current       ║ ~800mA (startup/flash)                   ║
║ Recommended Supply ║ 5V 1A minimum, 2A preferred              ║
╚════════════════════╩══════════════════════════════════════════╝
```

---

## 🔍 **VISUAL IDENTIFICATION GUIDE**

### **ESP32-CAM Module:**

```
TOP VIEW (Component Side):
┌────────────────────────────────────┐
│                                    │
│  ┌──────────────────────┐          │
│  │      OV2640 Camera   │          │
│  │      (Lens Module)   │          │
│  │         ● ●          │          │
│  └──────────────────────┘          │
│                                    │
│         [ESP32 Chip]               │
│                                    │
│    [Flash Memory]  [Antenna]      │
│                                    │
│  ○ Reset Button    ● Red LED      │
│                                    │
└────────────────────────────────────┘

BOTTOM VIEW (Pin Side):
┌────────────────────────────────────┐
│ GND  IO0  U0T  U0R  5V  ...       │ ← Pin labels
│  ○    ○    ○    ○   ○   ...       │ ← Pins/holes
│                                    │
│                                    │
│  [Camera Ribbon Cable]             │
│                                    │
│                                    │
│  GND  IO4  IO2  3.3V  ...         │
│  ○    ○    ○    ○    ...          │
└────────────────────────────────────┘
```

### **FTDI Adapter:**

```
┌────────────────────────────────────┐
│         FTDI USB Adapter           │
├────────────────────────────────────┤
│                                    │
│  [USB Mini/Micro Connector]        │
│                                    │
│  ┌──────────────┐                 │
│  │  FT232 Chip  │                 │
│  └──────────────┘                 │
│                                    │
│  ● GND    ● VCC (5V/3.3V)         │
│  ● TX     ● RX                     │
│  ● ...    ● ...                    │
│                                    │
│  [3.3V/5V Switch] ← Set to 5V!    │
│                                    │
└────────────────────────────────────┘
```

### **Buck Converter:**

```
Mini360 / LM2596 Module:
┌────────────────────────────────────┐
│                                    │
│  ●  IN+          OUT+  ●           │
│                                    │
│            ┌────────┐              │
│            │ Chip   │              │
│            └────────┘              │
│                                    │
│       [✚] ← Adjustment             │
│       Potentiometer                │
│                                    │
│  ●  IN-          OUT-  ●           │
│                                    │
└────────────────────────────────────┘
```

---

## ✅ **CONNECTION CHECKLIST**

### **Before Uploading Code:**

```
☐ FTDI connected to computer via USB
☐ GND (black) connected correctly
☐ 5V (red) connected correctly
☐ TX and RX crossed (yellow/green)
☐ IO0 connected to GND (blue jumper)
☐ Camera ribbon cable secure
☐ No loose wires
☐ FTDI set to 5V mode
☐ Correct COM port selected in Arduino IDE
```

### **For Normal Operation (Power Bank):**

```
☐ IO0-GND jumper REMOVED
☐ Power bank fully charged
☐ USB cable connected: Power bank → ESP32
☐ Red LED lights when powered
☐ WiFi credentials updated in code
☐ System boots normally (check Serial Monitor)
```

### **For Normal Operation (18650 Batteries):**

```
☐ Batteries fully charged (4.2V each)
☐ Batteries inserted correctly (+/- polarity)
☐ Buck converter adjusted to 5.0V
☐ Buck IN+ connected to battery +
☐ Buck IN- connected to battery -
☐ Buck OUT+ connected to ESP32 5V
☐ Buck OUT- connected to ESP32 GND
☐ All connections secure (soldered or reliable)
☐ Switch in OFF position before first connection
☐ Turn ON → Red LED lights → System boots
```

---

## 🆘 **TROUBLESHOOTING**

### **No Power / Red LED Not Lit:**

```
Check:
☐ Power source is ON and charged
☐ Voltage is correct (5V)
☐ Polarity correct (red → 5V, black → GND)
☐ Connections are solid (not loose)
☐ No broken wires
☐ ESP32-CAM not damaged

Test:
• Measure voltage at ESP32 5V pin with multimeter
• Should read 5.0V when powered
```

### **Upload Fails:**

```
Check:
☐ IO0 connected to GND
☐ TX/RX not swapped
☐ Correct COM port selected
☐ FTDI drivers installed
☐ USB cable is data-capable (not charge-only)

Try:
• Press RESET when "Connecting..." appears
• Try different USB port
• Reinstall FTDI drivers
```

### **System Boots But No WiFi:**

```
Check:
☐ WiFi credentials correct in code
☐ WiFi is 2.4GHz (ESP32 doesn't support 5GHz)
☐ Router is on and working
☐ ESP32 within WiFi range
☐ Check Serial Monitor for error messages
```

---

## 📸 **REFERENCE PHOTOS**

### **What Good Connections Look Like:**

```
✅ GOOD:
• Wires firmly inserted/soldered
• No exposed wire near connections
• Correct colors matched
• Neat organization
• No strain on wires
• Secure with heatshrink/tape

❌ BAD:
• Loose wires (fall out easily)
• Exposed bare wire (short risk)
• Wrong polarity (red to GND, etc.)
• Messy/tangled wires
• Pulled/strained connections
• No insulation
```

---

## 🎯 **FINAL ASSEMBLY TIPS**

1. **Test Each Stage:**
   - Test FTDI upload first
   - Test power supply separately
   - Test complete system on desk
   - Only then mount on cap

2. **Use Proper Wire:**
   - 22-24 AWG for power
   - Flexible stranded wire
   - Good quality insulation

3. **Secure Connections:**
   - Solder if possible
   - Or use reliable crimped connectors
   - Not just twisted wire!

4. **Label Everything:**
   - Mark +/- on wires
   - Label converter input/output
   - Note voltage settings

5. **Leave Extra Length:**
   - 10-20cm extra wire at ESP32
   - Allows adjustment and movement
   - Strain relief

---

## 📚 **RELATED DOCUMENTS**

- **BUILD_IN_ONE_DAY.md** - Complete build guide
- **BATTERY_POWER_GUIDE.md** - Battery setup details
- **VISUAL_WIRING_GUIDE.md** - Additional diagrams
- **PROJECT_SUMMARY.md** - Quick reference

---

**With these diagrams, you can now easily implement the hardware connections! 🔌⚡🚀**

*Good luck with your assembly!*
