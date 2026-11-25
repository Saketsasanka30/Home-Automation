/*
 * Project: Home Automation System | Blynk IoT 2.0 Integration
 * File: esp32_blynk.ino
 * Description: Complete ESP32 firmware connecting to Blynk Cloud & Mobile App
 *
 * Virtual Pin Datastreams Mapping:
 *   V0: Living Room Light (Integer: 0 = OFF, 1 = ON)
 *   V1: Bedroom Light (Integer: 0 = OFF, 1 = ON)
 *   V2: Smart DC Fan (Integer: 0 = OFF, 1 = ON)
 *   V3: Room Temperature (Double/Float, °C)
 *   V4: Room Humidity (Integer, %)
 *   V5: PIR Motion Status (Integer: 0 = Clear, 1 = Motion)
 *   V6: Lighting Brightness Slider (Integer: 0 - 100%)
 *   V7: Thermostat Target Temperature (Double, °C)
 *   V8: Master Automation Mode (Integer: 0 = Manual, 1 = Auto)
 *   V9: Away Mode (Integer: 0 = Home, 1 = Away)
 *
 * Hardware Connections:
 *   DHT11 Data    -> GPIO 4
 *   PIR Sensor    -> GPIO 13
 *   Relay 1 Light -> GPIO 18 (Active LOW)
 *   Relay 2 Fan   -> GPIO 19 (Active LOW)
 *   Bedroom LED   -> GPIO 21 (Active HIGH)
 *   Status LED    -> GPIO 2 (Onboard)
 */

// Fill in your Blynk Template details from the Blynk.Console:
#define BLYNK_TEMPLATE_ID   "TMPL3fBWGrDdY"
#define BLYNK_TEMPLATE_NAME "Home automation system"
#define BLYNK_AUTH_TOKEN    "uoGRAIK7HuhPRSeQQPfoN5p4yPTR2bq0"

#define BLYNK_PRINT Serial

#include <WiFi.h>
#include <WiFiClient.h>
#include <BlynkSimpleEsp32.h>
#include <DHT.h>

// Wi-Fi Credentials
char ssid[] = "YOUR_WIFI_SSID";
char pass[] = "YOUR_WIFI_PASSWORD";

// Hardware Pin Definitions
#define DHTPIN        4
#define DHTTYPE       DHT11
#define PIR_PIN       13
#define RELAY_LIGHT   18
#define RELAY_FAN     19
#define LED_BEDROOM   21
#define STATUS_LED    2

DHT dht(DHTPIN, DHTTYPE);
BlynkTimer timer;

// In-Memory Device States
bool lightState = false;
bool bedroomLightState = false;
bool fanState = false;
int brightnessValue = 72;
float targetTemperature = 22.0;
bool autoMode = true;
bool awayMode = false;

int lastMotionVal = -1;
unsigned long lastMotionTime = 0;
const unsigned long MOTION_TIMEOUT = 30000; // 30 seconds

// =========================================================================
// BLYNK VIRTUAL PIN WRITE HANDLERS (App/Web -> ESP32)
// =========================================================================

// V0: Living Room Light (Relay 1 - Active LOW)
BLYNK_WRITE(V0) {
  lightState = param.asInt();
  digitalWrite(RELAY_LIGHT, lightState ? LOW : HIGH);
  Serial.printf("[Blynk] Living Room Light -> %s\n", lightState ? "ON" : "OFF");
}

// V1: Bedroom Light (GPIO 21 - Active HIGH)
BLYNK_WRITE(V1) {
  bedroomLightState = param.asInt();
  digitalWrite(LED_BEDROOM, bedroomLightState ? HIGH : LOW);
  Serial.printf("[Blynk] Bedroom Light -> %s\n", bedroomLightState ? "ON" : "OFF");
}

// V2: Smart Fan (Relay 2 - Active LOW)
BLYNK_WRITE(V2) {
  fanState = param.asInt();
  digitalWrite(RELAY_FAN, fanState ? LOW : HIGH);
  Serial.printf("[Blynk] Smart Fan -> %s\n", fanState ? "ON" : "OFF");
}

// V6: Lighting Brightness (0 - 100%)
BLYNK_WRITE(V6) {
  brightnessValue = param.asInt();
  Serial.printf("[Blynk] Brightness set to %d%%\n", brightnessValue);
}

// V7: Target Thermostat Temperature
BLYNK_WRITE(V7) {
  targetTemperature = param.asFloat();
  Serial.printf("[Blynk] Target Temperature -> %.1f °C\n", targetTemperature);
}

// V8: Master Automation Mode Toggle
BLYNK_WRITE(V8) {
  autoMode = (param.asInt() == 1);
  Serial.printf("[Blynk] Automation Mode -> %s\n", autoMode ? "ENABLED" : "DISABLED");
}

// V9: Away Mode Toggle
BLYNK_WRITE(V9) {
  awayMode = (param.asInt() == 1);
  Serial.printf("[Blynk] Away Mode -> %s\n", awayMode ? "ARMED" : "DISARMED");

  if (awayMode) {
    // Power down all appliances
    lightState = false;
    bedroomLightState = false;
    fanState = false;

    digitalWrite(RELAY_LIGHT, HIGH);
    digitalWrite(RELAY_FAN, HIGH);
    digitalWrite(LED_BEDROOM, LOW);

    // Sync back to Blynk app
    Blynk.virtualWrite(V0, 0);
    Blynk.virtualWrite(V1, 0);
    Blynk.virtualWrite(V2, 0);
  }
}

// =========================================================================
// SENSOR TELEMETRY & AUTOMATION ROUTINE (Runs every 2.5 seconds)
// =========================================================================
void sendTelemetryAndRunAutomations() {
  // 1. Read DHT11 Temperature & Humidity
  float temp = dht.readTemperature();
  float hum = dht.readHumidity();

  if (!isnan(temp) && !isnan(hum)) {
    Blynk.virtualWrite(V3, temp);
    Blynk.virtualWrite(V4, hum);
    Serial.printf("[DHT11] Temp: %.1f °C | Humidity: %.0f %%\n", temp, hum);

    // Automation 2: Temperature-Based Fan Control (Hysteresis)
    if (autoMode && !awayMode) {
      if (temp >= 30.0 && !fanState) {
        fanState = true;
        digitalWrite(RELAY_FAN, LOW);
        Blynk.virtualWrite(V2, 1);
        Serial.println("[Auto-2A] Temp >= 30°C! Fan turned ON.");
      } else if (temp <= 28.0 && fanState) {
        fanState = false;
        digitalWrite(RELAY_FAN, HIGH);
        Blynk.virtualWrite(V2, 0);
        Serial.println("[Auto-2B] Temp <= 28°C! Fan turned OFF (Hysteresis cleared).");
      }
    }
  }

  // 2. Read PIR Motion Sensor
  int motionVal = digitalRead(PIR_PIN);
  if (motionVal != lastMotionVal) {
    lastMotionVal = motionVal;
    Blynk.virtualWrite(V5, motionVal);
    Serial.printf("[PIR] Motion state: %s\n", motionVal ? "DETECTED" : "CLEAR");

    // Automation 1A: Motion detected -> Turn ON Living Room Light
    if (autoMode && !awayMode && motionVal == HIGH) {
      lastMotionTime = millis();
      if (!lightState) {
        lightState = true;
        digitalWrite(RELAY_LIGHT, LOW);
        Blynk.virtualWrite(V0, 1);
        Serial.println("[Auto-1A] Motion detected! Living room light turned ON.");
      }
    }
  }

  // Automation 1B: Motion timeout (30 seconds of no motion) -> Turn OFF Light
  if (autoMode && !awayMode && lightState && motionVal == LOW) {
    if (millis() - lastMotionTime >= MOTION_TIMEOUT) {
      lightState = false;
      digitalWrite(RELAY_LIGHT, HIGH);
      Blynk.virtualWrite(V0, 0);
      Serial.println("[Auto-1B] 30 seconds vacancy expired. Light turned OFF.");
    }
  }
}

// Synchronize state when ESP32 reconnects to Blynk Cloud
BLYNK_CONNECTED() {
  Serial.println("[Blynk] Connected to Blynk Cloud! Synchronizing pins...");
  Blynk.syncVirtual(V0, V1, V2, V6, V7, V8, V9);
  digitalWrite(STATUS_LED, HIGH);
}

void setup() {
  Serial.begin(115200);

  // Configure hardware pins
  pinMode(STATUS_LED, OUTPUT);
  pinMode(PIR_PIN, INPUT_PULLDOWN);

  pinMode(RELAY_LIGHT, OUTPUT);
  digitalWrite(RELAY_LIGHT, HIGH); // Default OFF (active LOW)

  pinMode(RELAY_FAN, OUTPUT);
  digitalWrite(RELAY_FAN, HIGH);   // Default OFF (active LOW)

  pinMode(LED_BEDROOM, OUTPUT);
  digitalWrite(LED_BEDROOM, LOW);  // Default OFF (active HIGH)

  dht.begin();

  // Connect to Wi-Fi & Blynk Cloud
  Serial.println("\nConnecting to Blynk...");
  Blynk.begin(BLYNK_AUTH_TOKEN, ssid, pass);

  // Setup periodic telemetry timer (every 2.5s)
  timer.setInterval(2500L, sendTelemetryAndRunAutomations);
}

void loop() {
  Blynk.run();
  timer.run();
}
