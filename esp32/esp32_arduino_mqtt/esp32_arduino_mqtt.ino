/*
 * Project: Home Automation System | Python, IoT & Home Assistant
 * File: esp32_arduino_mqtt.ino
 * Description: Arduino C++ firmware for ESP32 connecting to Home Assistant via MQTT
 * Hardware:
 *   - ESP32 Dev Module
 *   - DHT11 on GPIO 4
 *   - PIR Motion Sensor on GPIO 13
 *   - Relay 1 (Living Room Light) on GPIO 18 (Active LOW)
 *   - Relay 2 (DC Fan) on GPIO 19 (Active LOW)
 *   - LED (Bedroom Light) on GPIO 21 (Active HIGH)
 *   - Onboard Status LED on GPIO 2
 */

#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <ArduinoJson.h>

// --- Network & MQTT Settings ---
const char* WIFI_SSID       = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD   = "YOUR_WIFI_PASSWORD";
const char* MQTT_SERVER     = "192.168.1.100"; // IP of Home Assistant / Mosquitto
const int   MQTT_PORT       = 1883;
const char* MQTT_USER       = "mqtt_user";     // Or leave blank if anonymous
const char* MQTT_PASSWORD   = "mqtt_password";
const char* CLIENT_ID       = "ESP32_SmartHome_Controller";

// --- Pin Definitions ---
#define DHTPIN        4
#define DHTTYPE       DHT11
#define PIR_PIN       13
#define RELAY_LIGHT   18
#define RELAY_FAN     19
#define LED_BEDROOM   21
#define STATUS_LED    2

// --- MQTT Topics ---
// State telemetry topics
const char* TOPIC_TEMP_STATE       = "home/sensors/temperature";
const char* TOPIC_HUMID_STATE      = "home/sensors/humidity";
const char* TOPIC_MOTION_STATE     = "home/sensors/motion";
const char* TOPIC_STATUS           = "home/system/status";

// Command & feedback topics
const char* TOPIC_LIGHT_LIVING_CMD   = "home/living_room/light/set";
const char* TOPIC_LIGHT_LIVING_STATE = "home/living_room/light/state";

const char* TOPIC_LIGHT_BED_CMD      = "home/bedroom/light/set";
const char* TOPIC_LIGHT_BED_STATE    = "home/bedroom/light/state";

const char* TOPIC_FAN_CMD            = "home/climate/fan/set";
const char* TOPIC_FAN_STATE          = "home/climate/fan/state";

// Home Assistant MQTT Auto-Discovery Topics
const char* DISCOVERY_TEMP_TOPIC     = "homeassistant/sensor/smart_temp/config";
const char* DISCOVERY_HUMID_TOPIC    = "homeassistant/sensor/smart_humidity/config";
const char* DISCOVERY_MOTION_TOPIC   = "homeassistant/binary_sensor/smart_motion/config";
const char* DISCOVERY_LIGHT_LIV_TOPIC= "homeassistant/switch/smart_living_light/config";
const char* DISCOVERY_LIGHT_BED_TOPIC= "homeassistant/switch/smart_bed_light/config";
const char* DISCOVERY_FAN_TOPIC      = "homeassistant/switch/smart_fan/config";

// --- Global Objects & Variables ---
WiFiClient espClient;
PubSubClient mqttClient(espClient);
DHT dht(DHTPIN, DHTTYPE);

unsigned long lastSensorRead = 0;
const unsigned long SENSOR_INTERVAL = 5000; // Read sensors every 5s
int lastMotionState = -1;

void setupWiFi() {
  delay(10);
  Serial.print("Connecting to Wi-Fi: ");
  Serial.println(WIFI_SSID);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    digitalWrite(STATUS_LED, !digitalRead(STATUS_LED));
  }

  Serial.println("\nWiFi connected! IP address: ");
  Serial.println(WiFi.localIP());
  digitalWrite(STATUS_LED, HIGH);
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
  String message = "";
  for (unsigned int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  message.trim();
  Serial.printf("[MQTT RX] Topic: %s | Payload: %s\n", topic, message.c_str());

  // 1. Living Room Light (Active LOW relay: LOW = ON, HIGH = OFF)
  if (String(topic) == TOPIC_LIGHT_LIVING_CMD) {
    if (message.equalsIgnoreCase("ON")) {
      digitalWrite(RELAY_LIGHT, LOW);
      mqttClient.publish(TOPIC_LIGHT_LIVING_STATE, "ON", true);
    } else if (message.equalsIgnoreCase("OFF")) {
      digitalWrite(RELAY_LIGHT, HIGH);
      mqttClient.publish(TOPIC_LIGHT_LIVING_STATE, "OFF", true);
    }
  }

  // 2. Bedroom Light (Active HIGH LED: HIGH = ON, LOW = OFF)
  if (String(topic) == TOPIC_LIGHT_BED_CMD) {
    if (message.equalsIgnoreCase("ON")) {
      digitalWrite(LED_BEDROOM, HIGH);
      mqttClient.publish(TOPIC_LIGHT_BED_STATE, "ON", true);
    } else if (message.equalsIgnoreCase("OFF")) {
      digitalWrite(LED_BEDROOM, LOW);
      mqttClient.publish(TOPIC_LIGHT_BED_STATE, "OFF", true);
    }
  }

  // 3. DC Fan (Active LOW relay: LOW = ON, HIGH = OFF)
  if (String(topic) == TOPIC_FAN_CMD) {
    if (message.equalsIgnoreCase("ON")) {
      digitalWrite(RELAY_FAN, LOW);
      mqttClient.publish(TOPIC_FAN_STATE, "ON", true);
    } else if (message.equalsIgnoreCase("OFF")) {
      digitalWrite(RELAY_FAN, HIGH);
      mqttClient.publish(TOPIC_FAN_STATE, "OFF", true);
    }
  }
}

void publishAutoDiscovery() {
  StaticJsonDocument<512> doc;

  // Temperature Discovery
  doc.clear();
  doc["name"] = "Living Room Temperature";
  doc["stat_t"] = TOPIC_TEMP_STATE;
  doc["unit_of_meas"] = "°C";
  doc["dev_cla"] = "temperature";
  doc["uniq_id"] = "esp32_smart_temp";
  char buffer[512];
  serializeJson(doc, buffer);
  mqttClient.publish(DISCOVERY_TEMP_TOPIC, buffer, true);

  // Humidity Discovery
  doc.clear();
  doc["name"] = "Living Room Humidity";
  doc["stat_t"] = TOPIC_HUMID_STATE;
  doc["unit_of_meas"] = "%";
  doc["dev_cla"] = "humidity";
  doc["uniq_id"] = "esp32_smart_humidity";
  serializeJson(doc, buffer);
  mqttClient.publish(DISCOVERY_HUMID_TOPIC, buffer, true);

  // Motion Sensor Discovery
  doc.clear();
  doc["name"] = "Living Room Motion";
  doc["stat_t"] = TOPIC_MOTION_STATE;
  doc["dev_cla"] = "motion";
  doc["pl_on"] = "ON";
  doc["pl_off"] = "OFF";
  doc["uniq_id"] = "esp32_smart_motion";
  serializeJson(doc, buffer);
  mqttClient.publish(DISCOVERY_MOTION_TOPIC, buffer, true);

  // Living Room Light Switch Discovery
  doc.clear();
  doc["name"] = "Living Room Light";
  doc["cmd_t"] = TOPIC_LIGHT_LIVING_CMD;
  doc["stat_t"] = TOPIC_LIGHT_LIVING_STATE;
  doc["pl_on"] = "ON";
  doc["pl_off"] = "OFF";
  doc["icon"] = "mdi:lightbulb";
  doc["uniq_id"] = "esp32_living_light";
  serializeJson(doc, buffer);
  mqttClient.publish(DISCOVERY_LIGHT_LIV_TOPIC, buffer, true);

  // Bedroom Light Switch Discovery
  doc.clear();
  doc["name"] = "Bedroom Light";
  doc["cmd_t"] = TOPIC_LIGHT_BED_CMD;
  doc["stat_t"] = TOPIC_LIGHT_BED_STATE;
  doc["pl_on"] = "ON";
  doc["pl_off"] = "OFF";
  doc["icon"] = "mdi:ceiling-light";
  doc["uniq_id"] = "esp32_bed_light";
  serializeJson(doc, buffer);
  mqttClient.publish(DISCOVERY_LIGHT_BED_TOPIC, buffer, true);

  // Fan Switch Discovery
  doc.clear();
  doc["name"] = "Smart Fan";
  doc["cmd_t"] = TOPIC_FAN_CMD;
  doc["stat_t"] = TOPIC_FAN_STATE;
  doc["pl_on"] = "ON";
  doc["pl_off"] = "OFF";
  doc["icon"] = "mdi:fan";
  doc["uniq_id"] = "esp32_fan";
  serializeJson(doc, buffer);
  mqttClient.publish(DISCOVERY_FAN_TOPIC, buffer, true);

  Serial.println("Published Home Assistant MQTT Auto-Discovery payloads.");
}

void reconnectMQTT() {
  while (!mqttClient.connected()) {
    Serial.print("Attempting MQTT connection to ");
    Serial.print(MQTT_SERVER);
    Serial.print("...");

    if (mqttClient.connect(CLIENT_ID, MQTT_USER, MQTT_PASSWORD, TOPIC_STATUS, 1, true, "offline")) {
      Serial.println("connected!");
      mqttClient.publish(TOPIC_STATUS, "online", true);

      // Subscribe to command topics
      mqttClient.subscribe(TOPIC_LIGHT_LIVING_CMD);
      mqttClient.subscribe(TOPIC_LIGHT_BED_CMD);
      mqttClient.subscribe(TOPIC_FAN_CMD);

      // Publish initial state values
      mqttClient.publish(TOPIC_LIGHT_LIVING_STATE, "OFF", true);
      mqttClient.publish(TOPIC_LIGHT_BED_STATE, "OFF", true);
      mqttClient.publish(TOPIC_FAN_STATE, "OFF", true);

      // Publish discovery configuration so Home Assistant registers entities automatically
      publishAutoDiscovery();
    } else {
      Serial.print("failed, rc=");
      Serial.print(mqttClient.state());
      Serial.println(" retrying in 5 seconds...");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);

  // Pin modes
  pinMode(STATUS_LED, OUTPUT);
  pinMode(PIR_PIN, INPUT_PULLDOWN);

  pinMode(RELAY_LIGHT, OUTPUT);
  digitalWrite(RELAY_LIGHT, HIGH); // Default OFF for active-low relay

  pinMode(RELAY_FAN, OUTPUT);
  digitalWrite(RELAY_FAN, HIGH);   // Default OFF for active-low relay

  pinMode(LED_BEDROOM, OUTPUT);
  digitalWrite(LED_BEDROOM, LOW);  // Default OFF for active-high LED

  dht.begin();
  setupWiFi();

  mqttClient.setServer(MQTT_SERVER, MQTT_PORT);
  mqttClient.setCallback(mqttCallback);
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    setupWiFi();
  }

  if (!mqttClient.connected()) {
    reconnectMQTT();
  }
  mqttClient.loop();

  // Read PIR Motion Sensor with instant state-change reporting
  int currentMotion = digitalRead(PIR_PIN);
  if (currentMotion != lastMotionState) {
    lastMotionState = currentMotion;
    const char* motionPayload = (currentMotion == HIGH) ? "ON" : "OFF";
    mqttClient.publish(TOPIC_MOTION_STATE, motionPayload, true);
    Serial.printf("[PIR] Motion state changed: %s\n", motionPayload);
  }

  // Periodic DHT11 Sensor Read
  unsigned long now = millis();
  if (now - lastSensorRead > SENSOR_INTERVAL) {
    lastSensorRead = now;

    float temp = dht.readTemperature();
    float hum = dht.readHumidity();

    if (!isnan(temp) && !isnan(hum)) {
      char tempStr[8];
      char humStr[8];
      dtostrf(temp, 1, 1, tempStr);
      dtostrf(hum, 1, 0, humStr);

      mqttClient.publish(TOPIC_TEMP_STATE, tempStr, true);
      mqttClient.publish(TOPIC_HUMID_STATE, humStr, true);
      Serial.printf("[DHT11] Temp: %s °C | Humidity: %s %%\n", tempStr, humStr);
    } else {
      Serial.println("[DHT11] Warning: Failed to read from DHT sensor!");
    }
  }
}
