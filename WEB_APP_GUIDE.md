# 🌐 Web Application - Pedestrian Navigation System

## Overview

A **real-time web-based obstacle mapping system** that integrates with your pedestrian navigation project. The system displays detected obstacles on an interactive map with GPS coordinates, providing visual feedback for urban navigation safety.

---

## 🎯 Features

### 🗺️ Interactive Map
- **Real-time obstacle markers** with GPS coordinates
- **OpenStreetMap integration** (free, no API key required)
- **Live updates** via WebSocket connection
- **User location tracking** with geolocation API
- **Nearby obstacle detection** (500m radius)
- **Filter by obstacle type** (potholes, cracks, pedestrians, objects)

### 📊 Analytics Dashboard
- **Statistics** - Total obstacles, by type, by severity
- **Charts** - Pie chart (types), bar chart (severity)
- **Recent detections** - Latest 20 obstacles with details
- **Auto-refresh** - Updates every 10 seconds

### 🔌 Real-time Integration
- **WebSocket server** for instant updates
- **RESTful API** for mobile/ESP32 integration
- **GPS coordinate tracking** for each obstacle
- **Confidence scoring** from YOLOv8
- **Severity levels** (low, medium, high, critical)

### 📱 Responsive Design
- Works on desktop, tablet, and mobile
- Touch-friendly interface
- Adaptive layout

---

## 📁 Project Structure

```
web_app/
├── server.py                 # Flask web server with WebSocket
├── templates/
│   ├── map.html             # Interactive map interface
│   └── dashboard.html       # Analytics dashboard
├── static/                  # (future: CSS/JS files)
└── requirements.txt         # Python dependencies

web_integrated_demo.py       # Detection client with web reporting
```

---

## 🚀 Quick Start

### **Step 1: Install Dependencies**

```powershell
# Navigate to web_app directory
cd web_app

# Install web server dependencies
pip install -r requirements.txt
```

**Dependencies installed:**
- `Flask` - Web framework
- `flask-socketio` - WebSocket support
- `flask-cors` - Cross-origin resource sharing
- `python-socketio` - Socket.IO client/server
- `requests` - HTTP client

### **Step 2: Start Web Server**

```powershell
# From web_app directory
python server.py
```

**Expected output:**
```
============================================================
🗺️  PEDESTRIAN NAVIGATION WEB SERVER
============================================================

📍 Access the map at: http://localhost:5000
📊 Access dashboard at: http://localhost:5000/dashboard

🔌 WebSocket enabled for real-time updates
🌐 CORS enabled for mobile app integration

💡 API Endpoints:
   GET  /api/obstacles - Get all obstacles
   POST /api/obstacles/nearby - Get nearby obstacles
   POST /api/obstacles/report - Report new obstacle
   GET  /api/stats - Get statistics

============================================================
```

### **Step 3: Run Detection Client**

**Open a NEW terminal** and run:

```powershell
# From project root
python web_integrated_demo.py
```

This starts:
- ✅ Webcam capture
- ✅ YOLOv8 detection
- ✅ GPS simulation (random walk around Hyderabad)
- ✅ Automatic reporting to web server
- ✅ Audio warnings

### **Step 4: View Map**

1. Open browser: **http://localhost:5000**
2. Allow location access (optional)
3. Watch obstacles appear in real-time!

---

## 🖥️ User Interface Guide

### **Map Interface** (`/`)

#### Control Panel (Top Right)
- **Connection Status** - Green (connected) or Red (disconnected)
- **Statistics**:
  - Total Obstacles
  - Nearby (500m radius)
  - Active Users
- **Filters**:
  - ☑️ Potholes
  - ☑️ Cracks
  - ☑️ Pedestrians
  - ☑️ Other Obstacles
- **Buttons**:
  - 🎯 Center on Me - Focus on your location
  - 🔄 Refresh Data - Reload obstacles
  - 📊 View Dashboard - Open analytics

#### Map Features
- **Colored markers** for different obstacle types:
  - 🔴 Red - Potholes
  - 🟠 Orange - Cracks
  - 🔵 Blue - Pedestrians
  - 🟣 Purple - Other obstacles
  - 🟢 Green - Your location

- **Click markers** to see details:
  - Obstacle type
  - Confidence score
  - Severity level
  - Timestamp
  - GPS coordinates
  - Distance from you

#### Legend (Bottom Left)
- Visual guide to marker colors

### **Dashboard** (`/dashboard`)

#### Statistics Cards
- **Total Obstacles** - All detected obstacles
- **Potholes** - Count of pothole detections
- **Cracks** - Count of crack detections
- **Active Users** - Number of connected clients

#### Charts
- **Obstacles by Type** - Pie chart showing distribution
- **Severity Distribution** - Bar chart (low → critical)

#### Recent Detections
- Latest 20 obstacles
- Sorted by timestamp (newest first)
- Shows: type, GPS, time, confidence, severity

---

## 🔌 API Reference

### **GET /api/obstacles**
Get all detected obstacles

**Response:**
```json
{
  "success": true,
  "count": 5,
  "obstacles": [
    {
      "id": 1,
      "type": "pothole",
      "confidence": 0.89,
      "latitude": 17.385044,
      "longitude": 78.486671,
      "timestamp": "2025-12-12T10:30:00",
      "severity": "high",
      "description": "pothole detected with 89% confidence",
      "user_id": "demo_user"
    }
  ]
}
```

### **POST /api/obstacles/nearby**
Get obstacles near a location

**Request:**
```json
{
  "latitude": 17.385044,
  "longitude": 78.486671,
  "radius_km": 1.0
}
```

**Response:**
```json
{
  "success": true,
  "count": 2,
  "obstacles": [
    {
      "id": 1,
      "type": "pothole",
      "distance_km": 0.15,
      ...
    }
  ]
}
```

### **POST /api/obstacles/report**
Report new obstacle

**Request:**
```json
{
  "type": "pothole",
  "confidence": 0.89,
  "latitude": 17.385044,
  "longitude": 78.486671,
  "severity": "high",
  "description": "Large pothole on main road",
  "user_id": "mobile_app_1"
}
```

**Response:**
```json
{
  "success": true,
  "obstacle": {
    "id": 1,
    "type": "pothole",
    ...
  }
}
```

### **GET /api/stats**
Get statistics

**Response:**
```json
{
  "success": true,
  "total_obstacles": 15,
  "by_type": {
    "pothole": 5,
    "crack": 3,
    "person": 7
  },
  "by_severity": {
    "low": 2,
    "medium": 8,
    "high": 4,
    "critical": 1
  },
  "active_users": 2
}
```

---

## 🔧 WebSocket Events

### **Client → Server**

#### `update_location`
Send current GPS location

```javascript
socket.emit('update_location', {
  latitude: 17.385044,
  longitude: 78.486671
});
```

#### `report_detection`
Report obstacle detection

```javascript
socket.emit('report_detection', {
  type: 'pothole',
  confidence: 0.89,
  latitude: 17.385044,
  longitude: 78.486671,
  severity: 'high'
});
```

### **Server → Client**

#### `new_obstacle`
Broadcast when new obstacle detected

```javascript
socket.on('new_obstacle', function(obstacle) {
  console.log('New obstacle:', obstacle);
  // Add marker to map
});
```

#### `nearby_obstacles`
Response to location update

```javascript
socket.on('nearby_obstacles', function(data) {
  console.log('Nearby count:', data.count);
  // Update UI
});
```

---

## 📱 Mobile App Integration

### **Using GPS from Mobile**

Replace GPS simulation in `web_integrated_demo.py`:

```python
# Import GPS library (e.g., gpsd, serial GPS, Android GPS)
import gps

def get_real_gps():
    # Connect to GPS device
    session = gps.gps("localhost", "2947")
    session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
    
    report = session.next()
    if report['class'] == 'TPV':
        return {
            'latitude': report.lat,
            'longitude': report.lon
        }
```

### **ESP32-CAM Integration**

Send detections from ESP32-CAM:

```cpp
// In ESP32 code
#include <HTTPClient.h>

void reportObstacle(String type, float conf, float lat, float lon) {
  HTTPClient http;
  http.begin("http://YOUR_SERVER_IP:5000/api/obstacles/report");
  http.addHeader("Content-Type", "application/json");
  
  String json = "{\"type\":\"" + type + 
                "\",\"confidence\":" + String(conf) + 
                ",\"latitude\":" + String(lat, 6) + 
                ",\"longitude\":" + String(lon, 6) + 
                ",\"severity\":\"high\"}";
  
  int httpCode = http.POST(json);
  http.end();
}
```

---

## 🌍 Using Real GPS Coordinates

### **Option 1: Browser Geolocation API** (already implemented)
The map automatically requests your location when you open it.

### **Option 2: External GPS Device**
- USB GPS dongle
- Bluetooth GPS receiver
- Phone GPS via USB tethering

### **Option 3: Smartphone GPS**
- Use Termux on Android
- Install GPS libraries
- Share location via API

### **Option 4: Google Location API** (requires API key)

```python
import googlemaps

gmaps = googlemaps.Client(key='YOUR_API_KEY')
geocode_result = gmaps.geocode('Address')
location = geocode_result[0]['geometry']['location']
```

---

## 🎨 Customization

### **Change Map Style**

Edit `map.html` line 442:

```javascript
// Dark mode
L.tileLayer('https://{s}.tile.jawg.io/jawg-dark/{z}/{x}/{y}.png', {
  attribution: 'Map © Jawg',
  maxZoom: 19
}).addTo(map);

// Satellite
L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
  attribution: 'Tiles © Esri',
  maxZoom: 19
}).addTo(map);
```

### **Adjust Detection Threshold**

Edit `web_integrated_demo.py` line 115:

```python
if confidence < 0.7:  # Change from 0.5 to 0.7 for higher confidence
    continue
```

### **Change Nearby Radius**

Edit `server.py` line 144:

```python
radius_km=2.0  # Change from 0.5km to 2km
```

### **Add New Obstacle Types**

Edit `map.html` marker colors:

```javascript
const iconMap = {
    'curb': {icon: 'fa-circle', color: '#795548'},
    'debris': {icon: 'fa-circle', color: '#607d8b'}
};
```

---

## 🔒 Security Considerations

### **For Production Deployment:**

1. **Change Secret Key** in `server.py`:
```python
app.config['SECRET_KEY'] = 'your-secure-random-key-here'
```

2. **Use HTTPS** (SSL/TLS):
```python
socketio.run(app, host='0.0.0.0', port=5000, 
             certfile='cert.pem', keyfile='key.pem')
```

3. **Add Authentication**:
```python
from flask_login import LoginManager
```

4. **Use Database** (PostgreSQL/MySQL):
```python
from flask_sqlalchemy import SQLAlchemy
```

5. **Rate Limiting**:
```python
from flask_limiter import Limiter
```

---

## 🐛 Troubleshooting

### **Problem: Map doesn't load**
- ✅ Check server is running: `http://localhost:5000`
- ✅ Check browser console for errors (F12)
- ✅ Verify internet connection (for map tiles)

### **Problem: No location access**
- ✅ Browser location permission required
- ✅ HTTPS needed for production (HTTP ok for localhost)
- ✅ Check browser settings

### **Problem: Obstacles not appearing**
- ✅ Verify detection client is running
- ✅ Check server logs for connection
- ✅ Refresh map (F5)
- ✅ Check filters are enabled

### **Problem: WebSocket not connecting**
- ✅ Install: `pip install python-engineio==4.8.0`
- ✅ Check firewall settings
- ✅ Verify port 5000 is not blocked

### **Problem: Poor GPS accuracy**
- ✅ Enable high-accuracy mode in browser
- ✅ Use external GPS for better accuracy
- ✅ Ensure clear view of sky (for GPS devices)

---

## 📊 Performance Optimization

### **Limit Stored Obstacles**

Edit `server.py` line 20:

```python
MAX_OBSTACLES = 500  # Reduce from 1000
```

### **Reduce Update Frequency**

Edit `map.html` line 658:

```javascript
setInterval(updateStats, 30000);  // 30 seconds instead of 10
```

### **Enable Marker Clustering**

Add to `map.html`:

```html
<script src="https://unpkg.com/leaflet.markercluster@1.4.1/dist/leaflet.markercluster.js"></script>
<link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.4.1/dist/MarkerCluster.css">

<script>
let markers = L.markerClusterGroup();
map.addLayer(markers);
</script>
```

---

## 🚀 Deployment Options

### **Local Network (LAN)**

1. Find your IP:
```powershell
ipconfig
```

2. Start server:
```powershell
python server.py
```

3. Access from other devices:
```
http://YOUR_IP:5000
```

### **Cloud Deployment**

#### **Heroku** (Free tier available)
```bash
heroku create pedestrian-nav
git push heroku main
```

#### **Railway** (Free tier)
```bash
railway login
railway init
railway up
```

#### **DigitalOcean** (Basic droplet $6/month)
- Deploy Flask app with Gunicorn
- Use Nginx reverse proxy
- Enable SSL with Let's Encrypt

### **Ngrok** (Instant public URL)

```powershell
# Download ngrok, then:
ngrok http 5000
```

---

## 📈 Future Enhancements

### **Planned Features:**
- ✅ Database persistence (SQLite/PostgreSQL)
- ✅ User accounts and authentication
- ✅ Historical data and heatmaps
- ✅ Route planning with obstacle avoidance
- ✅ Community reporting and verification
- ✅ Mobile app (React Native/Flutter)
- ✅ Machine learning for false positive filtering
- ✅ Integration with Google Maps/Mapbox
- ✅ Offline mode with cached maps
- ✅ Multi-language support

---

## 📞 Support

**Issues? Questions?**
- Check the troubleshooting section
- Review server logs in terminal
- Test API endpoints with Postman/curl
- Check browser console (F12)

**Need help with:**
- GPS integration
- ESP32-CAM connection
- Custom deployment
- Performance tuning

---

## 📄 License

Part of the Pedestrian Navigation ESP32-CAM project.

---

## ✅ Summary

You now have a **complete web-based obstacle mapping system** that:

1. ✅ Displays obstacles on interactive map
2. ✅ Real-time updates via WebSocket
3. ✅ GPS coordinate tracking
4. ✅ Analytics dashboard
5. ✅ RESTful API for integration
6. ✅ Mobile-friendly responsive design
7. ✅ Ready for ESP32-CAM/mobile integration

**Next Steps:**
1. Start web server: `cd web_app; python server.py`
2. Run detection client: `python web_integrated_demo.py`
3. Open map: http://localhost:5000
4. Watch obstacles appear in real-time!
5. Integrate real GPS for production use

🎉 **Your pedestrian navigation system is now web-enabled!**
