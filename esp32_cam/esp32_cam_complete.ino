/*
 * ═══════════════════════════════════════════════════════════════════
 * ESP32-CAM Complete Pedestrian Navigation System
 * ═══════════════════════════════════════════════════════════════════
 * 
 * Purpose: Stream video from cap-mounted ESP32-CAM for obstacle detection
 * Hardware: ESP32-CAM AI-Thinker module with OV2640 camera
 * 
 * Features:
 * - MJPEG video streaming over WiFi
 * - Optional Bluetooth audio alerts
 * - Status LED indicators
 * - Power-efficient operation for battery use
 * - Web interface for configuration
 * 
 * ═══════════════════════════════════════════════════════════════════
 * WIRING DIAGRAM
 * ═══════════════════════════════════════════════════════════════════
 * 
 * FOR PROGRAMMING (with FTDI):
 * ┌─────────────────┬──────────────────┐
 * │ FTDI Adapter    │ ESP32-CAM        │
 * ├─────────────────┼──────────────────┤
 * │ GND             │ GND              │
 * │ VCC (5V)        │ 5V               │
 * │ TX              │ U0R (RX)         │
 * │ RX              │ U0T (TX)         │
 * │                 │ IO0 → GND        │ (for upload only)
 * └─────────────────┴──────────────────┘
 * 
 * FOR NORMAL OPERATION:
 * ┌─────────────────┬──────────────────┐
 * │ Power Bank      │ ESP32-CAM        │
 * ├─────────────────┼──────────────────┤
 * │ 5V USB Out      │ 5V               │
 * │ GND             │ GND              │
 * └─────────────────┴──────────────────┘
 * 
 * OPTIONAL BLUETOOTH MODULE (HC-05 or JDY-62):
 * ┌─────────────────┬──────────────────┐
 * │ Bluetooth Module│ ESP32-CAM        │
 * ├─────────────────┼──────────────────┤
 * │ VCC             │ 3.3V (NOT 5V!)   │
 * │ GND             │ GND              │
 * │ RX              │ GPIO12 (TX2)     │
 * │ TX              │ GPIO13 (RX2)     │
 * └─────────────────┴──────────────────┘
 * 
 * ═══════════════════════════════════════════════════════════════════
 */

#include "esp_camera.h"
#include <WiFi.h>
#include <WebServer.h>
#include <WiFiClient.h>

// ═══════════════════════════════════════════════════════════════════
// 🔧 CONFIGURATION - CHANGE THESE VALUES
// ═══════════════════════════════════════════════════════════════════

// WiFi Credentials - IMPORTANT: Change to your network!
const char* ssid = "YOUR_WIFI_SSID";          // Your WiFi name
const char* password = "YOUR_WIFI_PASSWORD";   // Your WiFi password

// Device Configuration
const char* deviceName = "ESP32-CAM-Navigation";  // Device identifier
const int serverPort = 81;                        // Web server port

// Camera Settings
#define FRAME_SIZE FRAMESIZE_VGA   // VGA (640x480) - good balance
#define JPEG_QUALITY 12            // 0-63, lower = higher quality (10-15 recommended)
#define FRAME_RATE 30              // Target FPS (adjust for performance)

// LED Configuration
#define FLASH_LED_PIN 4            // Built-in flash LED
#define STATUS_LED_PIN 33          // Built-in status LED
#define LED_BRIGHTNESS 0           // Flash LED brightness (0-255, 0=off)

// Feature Flags
#define ENABLE_BLUETOOTH false     // Set true if using Bluetooth module
#define ENABLE_STATUS_LED true     // Blink status LED on activity
#define ENABLE_DEEP_SLEEP false    // Enable power-saving sleep mode

// ═══════════════════════════════════════════════════════════════════
// 📷 CAMERA PIN DEFINITIONS (AI-Thinker ESP32-CAM)
// ═══════════════════════════════════════════════════════════════════

#define CAMERA_MODEL_AI_THINKER
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

// Bluetooth Serial Pins (if enabled)
#define BT_TX_PIN 12
#define BT_RX_PIN 13

// ═══════════════════════════════════════════════════════════════════
// 🌐 WEB SERVER & GLOBAL VARIABLES
// ═══════════════════════════════════════════════════════════════════

WebServer server(serverPort);
unsigned long streamStartTime = 0;
unsigned long frameCount = 0;
bool isStreaming = false;

// ═══════════════════════════════════════════════════════════════════
// 🎥 CAMERA INITIALIZATION
// ═══════════════════════════════════════════════════════════════════

bool initCamera() {
  Serial.println("🎥 Initializing camera...");
  
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  
  // Frame buffer settings
  config.frame_size = FRAME_SIZE;
  config.jpeg_quality = JPEG_QUALITY;
  config.fb_count = 2;  // Double buffering for smoother streaming
  config.grab_mode = CAMERA_GRAB_LATEST;  // Always get latest frame
  
  // Initialize camera
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("❌ Camera init failed with error 0x%x\n", err);
    return false;
  }
  
  // Get sensor for advanced settings
  sensor_t * s = esp_camera_sensor_get();
  if (s == NULL) {
    Serial.println("❌ Failed to get camera sensor");
    return false;
  }
  
  // Optimize camera settings for outdoor navigation
  s->set_brightness(s, 0);     // -2 to 2 (0 = auto)
  s->set_contrast(s, 0);       // -2 to 2 (0 = auto)
  s->set_saturation(s, 0);     // -2 to 2 (0 = normal)
  s->set_special_effect(s, 0); // 0 = no effect
  s->set_whitebal(s, 1);       // Enable auto white balance
  s->set_awb_gain(s, 1);       // Enable auto white balance gain
  s->set_wb_mode(s, 0);        // 0 = auto white balance
  s->set_exposure_ctrl(s, 1);  // Enable auto exposure
  s->set_aec2(s, 1);           // Enable automatic exposure control
  s->set_ae_level(s, 0);       // -2 to 2 (exposure compensation)
  s->set_aec_value(s, 300);    // 0 to 1200 (exposure value)
  s->set_gain_ctrl(s, 1);      // Enable auto gain
  s->set_agc_gain(s, 0);       // 0 to 30 (auto gain value)
  s->set_gainceiling(s, (gainceiling_t)0); // Gain ceiling
  s->set_bpc(s, 0);            // Black pixel correction
  s->set_wpc(s, 1);            // White pixel correction
  s->set_raw_gma(s, 1);        // Enable raw gamma
  s->set_lenc(s, 1);           // Enable lens correction
  s->set_hmirror(s, 0);        // 0 = no horizontal mirror
  s->set_vflip(s, 0);          // 0 = no vertical flip
  s->set_dcw(s, 1);            // Enable downsize
  s->set_colorbar(s, 0);       // 0 = disable test pattern
  
  Serial.println("✅ Camera initialized successfully!");
  Serial.printf("   Resolution: %dx%d\n", 
                s->status.framesize == FRAMESIZE_VGA ? 640 : 0, 
                s->status.framesize == FRAMESIZE_VGA ? 480 : 0);
  Serial.printf("   JPEG Quality: %d\n", JPEG_QUALITY);
  
  return true;
}

// ═══════════════════════════════════════════════════════════════════
// 💡 LED CONTROL FUNCTIONS
// ═══════════════════════════════════════════════════════════════════

void initLEDs() {
  pinMode(FLASH_LED_PIN, OUTPUT);
  pinMode(STATUS_LED_PIN, OUTPUT);
  digitalWrite(FLASH_LED_PIN, LOW);
  digitalWrite(STATUS_LED_PIN, LOW);
}

void blinkStatusLED(int times = 1, int delayMs = 100) {
  if (!ENABLE_STATUS_LED) return;
  
  for (int i = 0; i < times; i++) {
    digitalWrite(STATUS_LED_PIN, HIGH);
    delay(delayMs);
    digitalWrite(STATUS_LED_PIN, LOW);
    if (i < times - 1) delay(delayMs);
  }
}

void setFlashLED(bool state) {
  digitalWrite(FLASH_LED_PIN, state ? HIGH : LOW);
}

// ═══════════════════════════════════════════════════════════════════
// 🌐 WEB SERVER HANDLERS
// ═══════════════════════════════════════════════════════════════════

// Root page - Device information and links
void handleRoot() {
  String html = "<!DOCTYPE html><html><head>";
  html += "<title>ESP32-CAM Navigation</title>";
  html += "<meta name='viewport' content='width=device-width, initial-scale=1'>";
  html += "<style>";
  html += "body { font-family: Arial, sans-serif; margin: 20px; background: #f0f0f0; }";
  html += "h1 { color: #333; }";
  html += ".card { background: white; padding: 20px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }";
  html += ".endpoint { background: #e8f4f8; padding: 10px; margin: 5px 0; border-radius: 4px; }";
  html += ".endpoint a { color: #0066cc; text-decoration: none; font-weight: bold; }";
  html += ".status { color: #00cc00; font-weight: bold; }";
  html += "img { max-width: 100%; border-radius: 8px; }";
  html += ".code { background: #2d2d2d; color: #f8f8f2; padding: 10px; border-radius: 4px; font-family: monospace; overflow-x: auto; }";
  html += "</style></head><body>";
  
  html += "<h1>🎥 ESP32-CAM Pedestrian Navigation</h1>";
  html += "<div class='card'>";
  html += "<h2>Status: <span class='status'>● ONLINE</span></h2>";
  html += "<p><strong>Device:</strong> " + String(deviceName) + "</p>";
  html += "<p><strong>IP Address:</strong> " + WiFi.localIP().toString() + "</p>";
  html += "<p><strong>Uptime:</strong> " + String(millis() / 1000) + " seconds</p>";
  html += "<p><strong>Free Heap:</strong> " + String(ESP.getFreeHeap() / 1024) + " KB</p>";
  html += "</div>";
  
  html += "<div class='card'>";
  html += "<h2>📡 Available Endpoints</h2>";
  html += "<div class='endpoint'><a href='/stream'>/stream</a> - MJPEG video stream</div>";
  html += "<div class='endpoint'><a href='/capture'>/capture</a> - Single JPEG capture</div>";
  html += "<div class='endpoint'><a href='/status'>/status</a> - JSON status information</div>";
  html += "<div class='endpoint'><a href='/control?led=on'>/control?led=on</a> - Turn flash LED on</div>";
  html += "<div class='endpoint'><a href='/control?led=off'>/control?led=off</a> - Turn flash LED off</div>";
  html += "</div>";
  
  html += "<div class='card'>";
  html += "<h2>🐍 Python Integration</h2>";
  html += "<p>Use this URL in your Python code:</p>";
  html += "<div class='code'>";
  html += "import cv2<br>";
  html += "cap = cv2.VideoCapture('http://" + WiFi.localIP().toString() + ":" + String(serverPort) + "/stream')<br>";
  html += "ret, frame = cap.read()";
  html += "</div>";
  html += "</div>";
  
  html += "<div class='card'>";
  html += "<h2>📹 Live Preview</h2>";
  html += "<img src='/stream' alt='Live Camera Stream' />";
  html += "</div>";
  
  html += "<div class='card'>";
  html += "<p style='color: #666; font-size: 12px;'>Pedestrian Navigation System v1.0 | ESP32-CAM</p>";
  html += "</div>";
  
  html += "</body></html>";
  
  server.send(200, "text/html", html);
  blinkStatusLED(1);
}

// Status endpoint - JSON information
void handleStatus() {
  String json = "{";
  json += "\"device\":\"" + String(deviceName) + "\",";
  json += "\"status\":\"online\",";
  json += "\"ip\":\"" + WiFi.localIP().toString() + "\",";
  json += "\"port\":" + String(serverPort) + ",";
  json += "\"resolution\":\"" + String(FRAME_SIZE) + "\",";
  json += "\"jpeg_quality\":" + String(JPEG_QUALITY) + ",";
  json += "\"uptime_seconds\":" + String(millis() / 1000) + ",";
  json += "\"free_heap_kb\":" + String(ESP.getFreeHeap() / 1024) + ",";
  json += "\"is_streaming\":" + String(isStreaming ? "true" : "false") + ",";
  json += "\"frames_sent\":" + String(frameCount);
  json += "}";
  
  server.send(200, "application/json", json);
  blinkStatusLED(1);
}

// Single capture endpoint - Get one JPEG frame
void handleCapture() {
  camera_fb_t * fb = esp_camera_fb_get();
  if (!fb) {
    server.send(500, "text/plain", "Camera capture failed");
    Serial.println("❌ Capture failed");
    return;
  }
  
  server.sendHeader("Content-Disposition", "inline; filename=capture.jpg");
  server.send_P(200, "image/jpeg", (const char *)fb->buf, fb->len);
  
  esp_camera_fb_return(fb);
  blinkStatusLED(1);
  Serial.println("📸 Single frame captured");
}

// Control endpoint - LED and camera controls
void handleControl() {
  if (server.hasArg("led")) {
    String ledState = server.arg("led");
    if (ledState == "on") {
      setFlashLED(true);
      server.send(200, "text/plain", "Flash LED ON");
      Serial.println("💡 Flash LED turned ON");
    } else if (ledState == "off") {
      setFlashLED(false);
      server.send(200, "text/plain", "Flash LED OFF");
      Serial.println("💡 Flash LED turned OFF");
    }
  } else {
    server.send(400, "text/plain", "Invalid control command");
  }
  blinkStatusLED(1);
}

// MJPEG stream endpoint - Main video streaming
void handleStream() {
  WiFiClient client = server.client();
  
  // Send MJPEG HTTP headers
  client.println("HTTP/1.1 200 OK");
  client.println("Content-Type: multipart/x-mixed-replace; boundary=frame");
  client.println("Access-Control-Allow-Origin: *");
  client.println("Cache-Control: no-cache, no-store, must-revalidate");
  client.println("Pragma: no-cache");
  client.println();
  
  isStreaming = true;
  streamStartTime = millis();
  frameCount = 0;
  
  Serial.println("📡 Stream started");
  Serial.println("   Client: " + client.remoteIP().toString());
  
  while (client.connected()) {
    // Capture frame
    camera_fb_t * fb = esp_camera_fb_get();
    if (!fb) {
      Serial.println("❌ Frame capture failed");
      break;
    }
    
    // Send MJPEG frame
    client.printf("--frame\r\n");
    client.printf("Content-Type: image/jpeg\r\n");
    client.printf("Content-Length: %d\r\n\r\n", fb->len);
    
    // Send frame data
    size_t sent = client.write(fb->buf, fb->len);
    if (sent != fb->len) {
      Serial.println("⚠️ Incomplete frame sent");
    }
    
    client.printf("\r\n");
    
    // Return frame buffer
    esp_camera_fb_return(fb);
    
    // Update statistics
    frameCount++;
    
    // Blink LED every 30 frames
    if (ENABLE_STATUS_LED && frameCount % 30 == 0) {
      digitalWrite(STATUS_LED_PIN, !digitalRead(STATUS_LED_PIN));
    }
    
    // Calculate and print FPS every 5 seconds
    if (frameCount % 150 == 0) {
      float elapsedSeconds = (millis() - streamStartTime) / 1000.0;
      float fps = frameCount / elapsedSeconds;
      Serial.printf("📊 FPS: %.1f | Frames: %lu | Uptime: %.1fs\n", fps, frameCount, elapsedSeconds);
    }
    
    // Frame rate control
    delay(1000 / FRAME_RATE);
  }
  
  isStreaming = false;
  digitalWrite(STATUS_LED_PIN, LOW);
  
  float totalSeconds = (millis() - streamStartTime) / 1000.0;
  float avgFps = frameCount / totalSeconds;
  
  Serial.println("📡 Stream ended");
  Serial.printf("   Duration: %.1f seconds\n", totalSeconds);
  Serial.printf("   Total frames: %lu\n", frameCount);
  Serial.printf("   Average FPS: %.1f\n", avgFps);
}

// 404 handler
void handleNotFound() {
  server.send(404, "text/plain", "404: Endpoint not found");
}

// ═══════════════════════════════════════════════════════════════════
// 📡 WIFI CONNECTION
// ═══════════════════════════════════════════════════════════════════

bool connectWiFi() {
  Serial.println("📡 Connecting to WiFi...");
  Serial.println("   SSID: " + String(ssid));
  
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  WiFi.setSleep(false);  // Disable sleep for stable streaming
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 40) {
    delay(500);
    Serial.print(".");
    blinkStatusLED(1, 50);
    attempts++;
  }
  Serial.println();
  
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("❌ WiFi connection failed!");
    Serial.println("   Check SSID and password in code");
    return false;
  }
  
  Serial.println("✅ WiFi connected!");
  Serial.println("   IP Address: " + WiFi.localIP().toString());
  Serial.println("   Signal Strength: " + String(WiFi.RSSI()) + " dBm");
  Serial.println("   MAC Address: " + WiFi.macAddress());
  
  return true;
}

// ═══════════════════════════════════════════════════════════════════
// 🚀 SETUP - Runs once on boot
// ═══════════════════════════════════════════════════════════════════

void setup() {
  // Initialize serial communication
  Serial.begin(115200);
  Serial.setDebugOutput(false);
  delay(1000);
  
  // Print startup banner
  Serial.println("\n\n");
  Serial.println("═══════════════════════════════════════════════");
  Serial.println("   🦯 PEDESTRIAN NAVIGATION SYSTEM");
  Serial.println("   ESP32-CAM Stream Server");
  Serial.println("═══════════════════════════════════════════════");
  Serial.println();
  
  // Initialize LEDs
  initLEDs();
  blinkStatusLED(3, 200);  // 3 quick blinks on startup
  
  // Initialize camera
  if (!initCamera()) {
    Serial.println("❌ FATAL: Camera initialization failed!");
    Serial.println("   Check camera module connection");
    Serial.println("   Press RESET button to try again");
    while (true) { 
      blinkStatusLED(5, 100);  // Fast blinking = error
      delay(1000);
    }
  }
  
  // Connect to WiFi
  if (!connectWiFi()) {
    Serial.println("❌ FATAL: WiFi connection failed!");
    Serial.println("   1. Check SSID and password in code");
    Serial.println("   2. Ensure 2.4GHz WiFi (5GHz not supported)");
    Serial.println("   3. Move closer to router");
    Serial.println("   Press RESET button to try again");
    while (true) { 
      blinkStatusLED(3, 200);  // Medium blinking = WiFi error
      delay(1000);
    }
  }
  
  // Setup web server routes
  server.on("/", handleRoot);
  server.on("/stream", handleStream);
  server.on("/capture", handleCapture);
  server.on("/status", handleStatus);
  server.on("/control", handleControl);
  server.onNotFound(handleNotFound);
  
  // Start web server
  server.begin();
  
  // Print success information
  Serial.println();
  Serial.println("═══════════════════════════════════════════════");
  Serial.println("✅ SYSTEM READY!");
  Serial.println("═══════════════════════════════════════════════");
  Serial.println();
  Serial.println("📍 Access Points:");
  Serial.println("   • Web Interface: http://" + WiFi.localIP().toString() + ":" + String(serverPort));
  Serial.println("   • Video Stream:  http://" + WiFi.localIP().toString() + ":" + String(serverPort) + "/stream");
  Serial.println("   • JSON Status:   http://" + WiFi.localIP().toString() + ":" + String(serverPort) + "/status");
  Serial.println();
  Serial.println("🐍 Python Integration:");
  Serial.println("   cap = cv2.VideoCapture('http://" + WiFi.localIP().toString() + ":" + String(serverPort) + "/stream')");
  Serial.println();
  Serial.println("═══════════════════════════════════════════════");
  Serial.println();
  
  // Success blinks
  blinkStatusLED(5, 100);
}

// ═══════════════════════════════════════════════════════════════════
// 🔄 LOOP - Runs continuously
// ═══════════════════════════════════════════════════════════════════

void loop() {
  // Handle incoming web requests
  server.handleClient();
  
  // Check WiFi connection status
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("⚠️ WiFi disconnected! Reconnecting...");
    connectWiFi();
  }
  
  // Small delay to prevent watchdog timer issues
  delay(1);
}
