# Live Detection Panel - User Guide

## 🎯 Overview
The live detection panel displays real-time obstacle information directly on the camera feed, similar to the demo webcam output.

---

## 📍 Location
The detection panel appears **at the bottom of the camera feed** with a dark semi-transparent background.

```
┌─────────────────────────────┐
│      CAMERA FEED            │
│                             │
│                             │
│  [Camera controls - top]    │
│                             │
│  ┌───────────────────────┐  │
│  │ 📊 Live Detections    │  │ ← Live Panel
│  │ 🔴 car         5.2m   │  │
│  │ 🟡 truck       8.3m   │  │
│  │ 🟢 bench      12.1m   │  │
│  └───────────────────────┘  │
└─────────────────────────────┘
```

---

## 🎨 Visual Layout

### Panel Header
```
📊 Live Detections
───────────────────
```

### Detection Items
Each detection shows:
```
🔴 car                    5.2m
   85% confidence
```

**Components:**
- **Icon** (🔴🟡🟢): Color-coded distance warning
- **Object Name**: Type of obstacle (car, truck, bench, etc.)
- **Distance**: Real distance in meters
- **Confidence**: AI detection accuracy percentage

---

## 🚦 Color Coding

### 🔴 Critical (Red)
- **Distance**: < 3 meters
- **Action**: IMMEDIATE attention needed
- **Visual**: Red background with red left border
- **Audio**: High-pitch beep (880 Hz)
```
🔴 car                    2.3m
   87% confidence
```

### 🟡 Warning (Yellow/Orange)
- **Distance**: 3-10 meters
- **Action**: Proceed with caution
- **Visual**: Orange background with orange left border
- **Audio**: Low-pitch beep (440 Hz)
```
🟡 truck                  8.5m
   82% confidence
```

### 🟢 Safe (Green)
- **Distance**: > 10 meters
- **Action**: Informational only
- **Visual**: Green background with green left border
- **Audio**: No sound
```
🟢 bench                 15.2m
   79% confidence
```

---

## 📊 Detection Display Features

### 1. **Real-Time Updates**
- Detections appear **instantly** when obstacles are found
- Smooth slide-in animation from left
- Most recent detection appears at **top**

### 2. **Auto-Removal**
- Each detection disappears after **10 seconds**
- Fade-out animation for smooth removal
- Keeps panel clean and relevant

### 3. **Maximum Display**
- Shows last **5 detections** maximum
- Oldest detection auto-removed when limit reached
- Prevents panel overflow

### 4. **Empty State**
When no obstacles detected:
```
┌───────────────────────────┐
│ 📊 Live Detections        │
│                           │
│   🔍 Scanning for         │
│      obstacles...         │
│                           │
└───────────────────────────┘
```

After detections cleared:
```
┌───────────────────────────┐
│ 📊 Live Detections        │
│                           │
│   ✅ All clear            │
│                           │
└───────────────────────────┘
```

---

## 🎬 Example Scenarios

### Scenario 1: Multiple Obstacles
```
┌─────────────────────────────┐
│ 📊 Live Detections          │
│ ┌─────────────────────────┐ │
│ │ 🔴 car          2.8m    │ │  ← Critical!
│ │    89% confidence       │ │
│ ├─────────────────────────┤ │
│ │ 🟡 bicycle      6.2m    │ │  ← Warning
│ │    78% confidence       │ │
│ ├─────────────────────────┤ │
│ │ 🟡 truck        9.1m    │ │  ← Warning
│ │    85% confidence       │ │
│ ├─────────────────────────┤ │
│ │ 🟢 traffic light 14.5m  │ │  ← Safe
│ │    92% confidence       │ │
│ └─────────────────────────┘ │
└─────────────────────────────┘
```

### Scenario 2: Close Call
```
┌─────────────────────────────┐
│ 📊 Live Detections          │
│ ┌─────────────────────────┐ │
│ │ 🔴 truck        1.5m    │ │  ← CRITICAL!
│ │    91% confidence       │ │  ← Very close!
│ └─────────────────────────┘ │
└─────────────────────────────┘

+ Audio: High-pitch beep! 🔊
+ Toast: ⚠️ CRITICAL: truck detected 1.5m ahead!
```

---

## 🔧 Technical Details

### Detection Flow
```
1. Camera captures frame every 3 seconds
2. TensorFlow.js COCO-SSD analyzes frame
3. Filters out ignored objects (people, etc.)
4. Checks for duplicates (30s cooldown)
5. Calculates GPS distance
6. Adds to live panel with animation
7. Triggers audio warning if close
8. Removes after 10 seconds
```

### Distance Calculation
Uses **Haversine formula** for accurate GPS distance:
```javascript
Distance = Earth_radius × angular_distance
         = 6,371,000m × acos(...)
```

**Accuracy**: ±1-5 meters depending on GPS precision

---

## 🎮 User Controls

### Detection Settings (Control Panel)
```
⚙️ Detection Settings
───────────────────────
☑️ Ignore People (Recommended)
☑️ Audio Warnings
Confidence Threshold: 75%
```

**Options:**
- **Ignore People**: Prevents repeated person detections (recommended for dashcam)
- **Audio Warnings**: Enable/disable distance beeps
- **Confidence**: Shows current detection threshold (75% = high accuracy)

---

## 📱 Responsive Design

### Desktop/Laptop
- Panel width: Full camera width
- Height: Max 150px with scrollbar
- Font: 12px readable

### Mobile/Tablet
- Panel adapts to screen size
- Touch-friendly spacing
- Same functionality

---

## 🆚 Comparison: Demo vs Web

### Demo Webcam Output (Terminal)
```
Frame 1 | Detections: 2
━━━━━━━━━━━━━━━━━━━━━━━━━━
🚗 car (87%) - Location: [lat, lon]
🚌 bus (82%) - Location: [lat, lon]
```

### Web Live Panel (Visual)
```
┌─────────────────────────┐
│ 📊 Live Detections      │
│ 🔴 car          5.2m    │
│    87% confidence       │
│ 🟡 bus          8.1m    │
│    82% confidence       │
└─────────────────────────┘
```

**Advantages:**
- ✅ Visual color coding (red/yellow/green)
- ✅ Real distance display
- ✅ Smooth animations
- ✅ Auto-removal (no clutter)
- ✅ Audio warnings
- ✅ Better UX than terminal output

---

## 🐛 Troubleshooting

### "Panel not showing"
- Check if camera is started
- Wait for AI model to load (~10 seconds)
- Verify location permission granted

### "No detections appearing"
- Ensure objects are in camera view
- Check "Ignore People" is enabled (if testing with people)
- Verify 75% confidence threshold (high accuracy)
- Wait 3 seconds between scans

### "Duplicate detections"
- Fixed! 30-second cooldown per object type
- Same object won't appear twice within 30s

### "Distance shows 0.0m"
- Location not yet acquired
- Grant GPS permission
- Wait for "Center on Me" to activate

---

## 💡 Tips for Best Results

### 1. **Camera Positioning**
- Point at road/path ahead
- Keep camera stable
- Good lighting helps accuracy

### 2. **Detection Optimization**
- Enable "Ignore People" for dashcam use
- Keep "Audio Warnings" on for safety
- Monitor both panel and map

### 3. **Understanding Distance**
- **< 3m**: STOP or change direction
- **3-10m**: Slow down, prepare to avoid
- **> 10m**: Informational, no immediate action

### 4. **Interpreting Confidence**
- **75-100%**: Very reliable detection
- **60-75%**: Filtered out (not shown)
- Panel only shows high-confidence detections

---

## 🎯 Usage Examples

### Walking Mode
```
☑️ Ignore People: OFF
☑️ Audio Warnings: ON

Expected detections:
- People walking nearby
- Vehicles on road
- Traffic signs
- Obstacles on path
```

### Dashboard Camera Mode
```
☑️ Ignore People: ON  ← Recommended
☑️ Audio Warnings: ON

Expected detections:
- Vehicles ahead
- Traffic signs
- Road obstacles
- Bicycles
```

### Indoor Testing
```
☑️ Ignore People: ON
☑️ Audio Warnings: OFF

Expected detections:
- Furniture (chair, bench)
- Objects (bottle, cup)
- Electronics (tv, laptop)
```

---

## 📊 Sample Output Log

### Browser Console (F12)
```javascript
✓ Detected: car (87% confidence, 5.2m away)
⚠️ WARNING: car detected 5.2m ahead

⊘ Ignoring: person (82% confidence)

✓ Detected: truck (85% confidence, 8.3m away)
⚠️ WARNING: truck detected 8.3m ahead

Skipping duplicate: car (last seen 15.3s ago)

✓ Detected: bicycle (78% confidence, 6.5m away)
⚠️ WARNING: bicycle detected 6.5m ahead
```

### Live Panel (Visual)
```
🔴 car          5.2m  ← Added at 10:00:00
   87% confidence

🟡 truck        8.3m  ← Added at 10:00:03
   85% confidence

🟡 bicycle      6.5m  ← Added at 10:00:06
   78% confidence
```

---

## 🚀 Next Steps

1. **Refresh Browser**: http://localhost:5000
2. **Start Camera**: Click "Start Camera" button
3. **Wait for Model**: ~10 seconds for AI to load
4. **Point Camera**: At road/objects ahead
5. **Watch Panel**: Detections appear at bottom
6. **Monitor Distance**: Red = critical, Yellow = warning, Green = safe

---

## 📞 Support

If detections aren't showing:
1. Check browser console (F12) for logs
2. Verify camera and location permissions
3. Ensure objects are visible in frame
4. Wait 3 seconds between detections
5. Review `DETECTION_IMPROVEMENTS.md` for algorithm details

---

## 🏆 Summary

**Live Detection Panel Features:**
- ✅ Real-time obstacle display
- ✅ Color-coded distance warnings (🔴🟡🟢)
- ✅ Accurate distance calculation
- ✅ High confidence detections (75%+)
- ✅ Smooth animations
- ✅ Auto-removal (10s timeout)
- ✅ Maximum 5 items displayed
- ✅ Audio alerts for close obstacles
- ✅ No repeated detections (30s cooldown)

**Result**: Professional dashboard display matching demo webcam functionality! 🎉
