/*
 * ESP32-CAM MJPEG Stream Server
 * For Intelligent Pedestrian Navigation System
 * 
 * Hardware: ESP32-CAM AI-Thinker module with OV2640 camera
 * Purpose: Streams MJPEG video at /stream endpoint for Python processing
 * 
 * WIRING (for programming with FTDI):
 * - ESP32-CAM GND → FTDI GND
 * - ESP32-CAM 5V → FTDI VCC (5V)
 * - ESP32-CAM U0R → FTDI TX
 * - ESP32-CAM U0T → FTDI RX
 * - ESP32-CAM IO0 → GND (for upload mode, disconnect after upload)
 * 
 * After uploading: Remove IO0-GND jumper and press RESET button
 */

#include "esp_camera.h"
#include <WiFi.h>
#include <WebServer.h>
#include <WiFiClient.h>

// =========================
// CONFIGURATION
// =========================

// WiFi credentials - CHANGE THESE!
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// Web server on port 81 (80 is often used by other services)
WebServer server(81);

// Camera model: AI-THINKER ESP32-CAM
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

// Camera settings
#define FRAME_SIZE FRAMESIZE_VGA  // 640x480 - good balance
#define JPEG_QUALITY 10           // 0-63, lower is higher quality

// =========================
// CAMERA INITIALIZATION
// =========================

bool initCamera() {
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
  
  // Frame size and quality
  config.frame_size = FRAME_SIZE;
  config.jpeg_quality = JPEG_QUALITY;
  config.fb_count = 2;  // Double buffering for smoother stream
  
  // Camera init
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x\n", err);
    return false;
  }
  
  // Sensor settings for better outdoor/indoor detection
  sensor_t * s = esp_camera_sensor_get();
  if (s != NULL) {
    s->set_brightness(s, 0);     // -2 to 2
    s->set_contrast(s, 0);       // -2 to 2
    s->set_saturation(s, 0);     // -2 to 2
    s->set_special_effect(s, 0); // 0-6 (0=None)
    s->set_whitebal(s, 1);       // Enable white balance
    s->set_awb_gain(s, 1);       // Enable auto white balance gain
    s->set_wb_mode(s, 0);        // 0-4 (auto)
    s->set_exposure_ctrl(s, 1);  // Enable auto exposure
    s->set_aec2(s, 1);           // Enable AEC2
    s->set_gain_ctrl(s, 1);      // Enable gain control
    s->set_agc_gain(s, 0);       // 0-30
    s->set_gainceiling(s, (gainceiling_t)0);  // 0-6
    s->set_bpc(s, 0);            // Black pixel correction
    s->set_wpc(s, 1);            // White pixel correction
    s->set_raw_gma(s, 1);        // Enable gamma correction
    s->set_lenc(s, 1);           // Enable lens correction
    s->set_hmirror(s, 0);        // Horizontal mirror
    s->set_vflip(s, 0);          // Vertical flip
  }
  
  Serial.println("Camera initialized successfully");
  return true;
}

// =========================
// WEB SERVER HANDLERS
// =========================

// Root page - info and links
void handleRoot() {
  String html = "<html><head><title>ESP32-CAM Stream</title></head><body>";
  html += "<h1>ESP32-CAM Pedestrian Navigation Stream</h1>";
  html += "<p>Camera is running and streaming MJPEG video.</p>";
  html += "<h2>Endpoints:</h2>";
  html += "<ul>";
  html += "<li><a href='/stream'>/stream</a> - MJPEG video stream</li>";
  html += "<li><a href='/capture'>/capture</a> - Single JPEG capture</li>";
  html += "<li><a href='/status'>/status</a> - Camera status</li>";
  html += "</ul>";
  html += "<h2>Stream URL for Python:</h2>";
  html += "<code>http://" + WiFi.localIP().toString() + ":81/stream</code>";
  html += "<h2>Live Preview:</h2>";
  html += "<img src='/stream' width='640' height='480' />";
  html += "</body></html>";
  server.send(200, "text/html", html);
}

// Status endpoint
void handleStatus() {
  String json = "{";
  json += "\"camera\":\"ESP32-CAM\",";
  json += "\"status\":\"online\",";
  json += "\"ip\":\"" + WiFi.localIP().toString() + "\",";
  json += "\"resolution\":\"" + String(FRAME_SIZE) + "\",";
  json += "\"quality\":" + String(JPEG_QUALITY) + ",";
  json += "\"uptime\":" + String(millis() / 1000);
  json += "}";
  server.send(200, "application/json", json);
}

// Single capture endpoint
void handleCapture() {
  camera_fb_t * fb = esp_camera_fb_get();
  if (!fb) {
    server.send(500, "text/plain", "Camera capture failed");
    return;
  }
  
  server.sendHeader("Content-Disposition", "inline; filename=capture.jpg");
  server.send_P(200, "image/jpeg", (const char *)fb->buf, fb->len);
  
  esp_camera_fb_return(fb);
}

// MJPEG stream endpoint - main video stream
void handleStream() {
  WiFiClient client = server.client();
  
  // MJPEG HTTP headers
  client.println("HTTP/1.1 200 OK");
  client.println("Content-Type: multipart/x-mixed-replace; boundary=frame");
  client.println("Access-Control-Allow-Origin: *");
  client.println();
  
  Serial.println("Stream started");
  
  while (client.connected()) {
    camera_fb_t * fb = esp_camera_fb_get();
    if (!fb) {
      Serial.println("Camera capture failed");
      break;
    }
    
    // Send MJPEG frame
    client.printf("--frame\r\n");
    client.printf("Content-Type: image/jpeg\r\n");
    client.printf("Content-Length: %d\r\n\r\n", fb->len);
    client.write(fb->buf, fb->len);
    client.printf("\r\n");
    
    esp_camera_fb_return(fb);
    
    // Small delay to prevent overwhelming the client
    delay(30);  // ~30 FPS max
  }
  
  Serial.println("Stream ended");
}

// 404 handler
void handleNotFound() {
  server.send(404, "text/plain", "Not Found");
}

// =========================
// SETUP & LOOP
// =========================

void setup() {
  Serial.begin(115200);
  Serial.println("\n\n=================================");
  Serial.println("ESP32-CAM Stream Server Starting");
  Serial.println("=================================\n");
  
  // Initialize camera
  Serial.println("Initializing camera...");
  if (!initCamera()) {
    Serial.println("ERROR: Camera initialization failed!");
    Serial.println("Check camera module connection and restart.");
    while (true) { delay(1000); }
  }
  
  // Connect to WiFi
  Serial.print("Connecting to WiFi: ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  WiFi.setSleep(false);  // Disable WiFi sleep for stable streaming
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("\nERROR: WiFi connection failed!");
    Serial.println("Check SSID and password in code.");
    while (true) { delay(1000); }
  }
  
  Serial.println("\nWiFi connected!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
  Serial.print("Stream URL: http://");
  Serial.print(WiFi.localIP());
  Serial.println(":81/stream");
  
  // Setup web server routes
  server.on("/", handleRoot);
  server.on("/stream", handleStream);
  server.on("/capture", handleCapture);
  server.on("/status", handleStatus);
  server.onNotFound(handleNotFound);
  
  // Start server
  server.begin();
  Serial.println("\nWeb server started!");
  Serial.println("=================================");
  Serial.println("Ready to stream video");
  Serial.println("=================================\n");
}

void loop() {
  server.handleClient();
  delay(1);  // Small delay to prevent watchdog issues
}
