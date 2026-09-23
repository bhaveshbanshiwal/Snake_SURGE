#include <WiFi.h>
#include <WebServer.h>
#include <Wire.h>
#include <DHT.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BMP280.h>
#include <Adafruit_ADXL345_U.h>
#include <esp_wifi.h>

// --- HOTSPOT SETTINGS ---
const char* ssid = "NF-07-STATS";
const char* password = "zaybxc09@";

WebServer server(80); 

// --- PIN MAPPING ---
const int trigPin = 32; 
const int echoPin = 34; 
#define DHTPIN 22     
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

const int I2C_SDA = 21;
const int I2C_SCL = 19;

Adafruit_BMP280 bmp; 
Adafruit_ADXL345_Unified accel = Adafruit_ADXL345_Unified(12345);

// --- GLOBAL VARIABLES ---
float dhtTemp = 0.0, dhtHum = 0.0;
float bmpTemp = 25.0, bmpPressure = 0.0, bmpAltitude = 0.0;
float currentDistance = 0.0;
float accelX = 0.0, accelY = 0.0, accelZ = 0.0;

unsigned long lastFastRead = 0;
unsigned long lastSlowRead = 0;

// --- PRECISION ULTRASONIC READ ---
float getAccurateDistance(float tempC) {
  float soundSpeed_cm_us = (331.3 + 0.606 * tempC) / 10000.0;
  float samples[3];
  int validCount = 0;

  for (int i = 0; i < 3; i++) {
    digitalWrite(trigPin, LOW);
    delayMicroseconds(2);
    digitalWrite(trigPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(trigPin, LOW);
    
    long duration = pulseIn(echoPin, HIGH, 15000); // Tight 15ms timeout to prevent lag
    if (duration > 0) samples[validCount++] = (duration * soundSpeed_cm_us) / 2.0;
    delayMicroseconds(500); 
  }

  if (validCount == 0) return 0.0;
  if (validCount == 1) return samples[0];
  if (validCount == 2) return (samples[0] + samples[1]) / 2.0;

  if (samples[0] > samples[1]) { float t = samples[0]; samples[0] = samples[1]; samples[1] = t; }
  if (samples[1] > samples[2]) { float t = samples[1]; samples[1] = samples[2]; samples[2] = t; }
  if (samples[0] > samples[1]) { float t = samples[0]; samples[0] = samples[1]; samples[1] = t; }

  return samples[1]; 
}

// --- FRONTEND UI (Chat Removed, 100ms Refresh) ---
const char INDEX_HTML[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Precision Scale & Sentry</title>
  <style>
    body { font-family: Arial, sans-serif; text-align: center; background-color: #121212; color: #ffffff; margin: 0; padding: 20px; }
    .card { background: #1e1e1e; padding: 20px; margin: 0 auto 20px auto; width: 100%; max-width: 450px; border-radius: 12px; box-shadow: 0 8px 16px rgba(0,0,0,0.6); }
    h1 { color: #00ffcc; font-size: 22px; margin-bottom: 20px; text-transform: uppercase; letter-spacing: 1px; }
    h2 { color: #fff; font-size: 15px; margin-bottom: 10px; border-bottom: 1px solid #333; padding-bottom: 5px; text-align: left; text-transform: uppercase; color: #888; margin-top: 25px; }
    .row { display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid #2a2a2a; }
    .row:last-child { border-bottom: none; }
    .label-group { text-align: left; }
    .label { font-size: 15px; color: #dddddd; }
    .sensor { font-size: 11px; color: #777777; margin-left: 5px; }
    .value { font-size: 18px; font-weight: bold; color: #00ffcc; }
    .highlight .value { color: #ffd32a; font-size: 24px; }
  </style>
</head>
<body>
  <div class="card">
    <h1>Precision Sentry Node</h1>
    
    <h2>Live High-Speed Data (100ms)</h2>
    <div class="row highlight"><div class="label-group"><span class="label">Compensated Distance</span><span class="sensor">(HC-SR04)</span></div><div class="value"><span id="dist">--</span> cm</div></div>
    <div class="row"><div class="label-group"><span class="label">X-Axis Tilt</span><span class="sensor">(ADXL345)</span></div><div class="value"><span id="tiltX">--</span> g</div></div>
    <div class="row"><div class="label-group"><span class="label">Y-Axis Tilt</span><span class="sensor">(ADXL345)</span></div><div class="value"><span id="tiltY">--</span> g</div></div>
    <div class="row"><div class="label-group"><span class="label">Z-Axis Gravity</span><span class="sensor">(ADXL345)</span></div><div class="value"><span id="tiltZ">--</span> g</div></div>
    
    <div class="row"><div class="label-group"><span class="label">Micro-Temp</span><span class="sensor">(BMP280)</span></div><div class="value"><span id="bmpT">--</span> &deg;C</div></div>
    <div class="row"><div class="label-group"><span class="label">Pressure</span><span class="sensor">(BMP280)</span></div><div class="value"><span id="bmpP">--</span> hPa</div></div>
    <div class="row"><div class="label-group"><span class="label">Altitude</span><span class="sensor">(BMP280)</span></div><div class="value"><span id="bmpA">--</span> m</div></div>

    <h2>Ambient Climate (2000ms)</h2>
    <div class="row"><div class="label-group"><span class="label">Room Temp</span><span class="sensor">(DHT11)</span></div><div class="value"><span id="dhtT">--</span> &deg;C</div></div>
    <div class="row"><div class="label-group"><span class="label">Humidity</span><span class="sensor">(DHT11)</span></div><div class="value"><span id="dhtH">--</span> %</div></div>
  </div>

  <script>
    // Max-Speed AJAX fetching at 100ms (10 FPS)
    setInterval(function() {
      fetch('/data')
        .then(response => response.json())
        .then(data => {
          document.getElementById('dist').innerText = data.dist.toFixed(1);
          document.getElementById('tiltX').innerText = data.tiltX.toFixed(2);
          document.getElementById('tiltY').innerText = data.tiltY.toFixed(2);
          document.getElementById('tiltZ').innerText = data.tiltZ.toFixed(2);
          
          document.getElementById('bmpT').innerText = data.bmpT.toFixed(2); // Higher precision for fast updates
          document.getElementById('bmpP').innerText = data.bmpP.toFixed(1);
          document.getElementById('bmpA').innerText = data.bmpA.toFixed(0);

          document.getElementById('dhtT').innerText = data.dhtT.toFixed(1);
          document.getElementById('dhtH').innerText = data.dhtH.toFixed(0);
        }).catch(err => {});
    }, 100); 
  </script>
</body>
</html>
)rawliteral";

void handleRoot() { server.send(200, "text/html", INDEX_HTML); }

void handleData() {
  String json = "{";
  json += "\"dist\":" + String(currentDistance, 1) + ",";
  json += "\"tiltX\":" + String(accelX) + ",";
  json += "\"tiltY\":" + String(accelY) + ",";
  json += "\"tiltZ\":" + String(accelZ) + ",";
  json += "\"bmpT\":" + String(bmpTemp) + ",";
  json += "\"dhtT\":" + String(dhtTemp) + ",";
  json += "\"dhtH\":" + String(dhtHum) + ",";
  json += "\"bmpP\":" + String(bmpPressure) + ",";
  json += "\"bmpA\":" + String(bmpAltitude);
  json += "}";
  server.send(200, "application/json", json);
}

void setup() {
  setCpuFrequencyMhz(240); // Max Processor Speed

  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  dht.begin();
  
  Wire.begin(I2C_SDA, I2C_SCL); 
  Wire.setClock(400000); // I2C Fast Mode
  
  if (bmp.begin(0x76) || bmp.begin(0x77)) {
    // Drop standby time to 63ms to allow the BMP280 to update faster than our 100ms loop
    bmp.setSampling(Adafruit_BMP280::MODE_NORMAL, Adafruit_BMP280::SAMPLING_X2, Adafruit_BMP280::SAMPLING_X16, Adafruit_BMP280::FILTER_X16, Adafruit_BMP280::STANDBY_MS_63);
  }
  if (accel.begin()) accel.setRange(ADXL345_RANGE_16_G);
  
  WiFi.softAP(ssid, password); 
  WiFi.setSleep(false); // No Wi-Fi Sleep
  esp_wifi_set_ps(WIFI_PS_NONE);
  WiFi.setTxPower(WIFI_POWER_19_5dBm); // Max Range

  server.on("/", handleRoot);
  server.on("/data", handleData);
  server.begin();
}

void loop() {
  server.handleClient(); 
  unsigned long currentMillis = millis();

  // --- MAX SPEED LOOP (100ms) ---
  if (currentMillis - lastFastRead >= 100) {
    // 1. Compensated Ultrasonic Read
    currentDistance = getAccurateDistance(bmpTemp);

    // 2. Accelerometer Read
    sensors_event_t event; 
    accel.getEvent(&event);
    accelX = event.acceleration.x;
    accelY = event.acceleration.y;
    accelZ = event.acceleration.z;

    // 3. BMP280 Fast Read (Moved to high-speed loop)
    bmpTemp = bmp.readTemperature();
    bmpPressure = bmp.readPressure() / 100.0;
    bmpAltitude = bmp.readAltitude(1013.25); 

    lastFastRead = currentMillis;
  }

  // --- HARDWARE LIMITED LOOP (2000ms) ---
  // DHT11 hardware will lock up and fail if polled faster than 1-2 seconds
  if (currentMillis - lastSlowRead >= 2000) {
    float t = dht.readTemperature();
    float h = dht.readHumidity();
    if (!isnan(t)) dhtTemp = t;
    if (!isnan(h)) dhtHum = h;

    lastSlowRead = currentMillis;
  }
}