# 📱 Blynk IoT 2.0 Integration & Setup Guide

This guide provides the complete, step-by-step setup to connect your **ESP32 microcontroller**, **Blynk Mobile App / Web Console**, and the **HAVEN 3D Spatial Web Dashboard** into a unified smart-home ecosystem.

---

## 🔑 Your Pre-Configured Credentials

Your ESP32 firmware (`esp32/esp32_blynk/esp32_blynk.ino`) and web app have been pre-loaded with your exact template details:

```c
#define BLYNK_TEMPLATE_ID   "TMPL3fBWGrDdY"
#define BLYNK_TEMPLATE_NAME "Home automation system"
#define BLYNK_AUTH_TOKEN    "uoGRAIK7HuhPRSeQQPfoN5p4yPTR2bq0"
```

---

## 📊 STEP 1: Configure Virtual Pin Datastreams in Blynk Console

1. Log in to [blynk.cloud](https://blynk.cloud/).
2. On the left navigation bar, click **Developer Zone** (wrench icon 🛠️) $\rightarrow$ **Templates**.
3. Select your template: **`Home automation system`** (ID: `TMPL3fBWGrDdY`).
4. Click on the **Datastreams** tab $\rightarrow$ click **+ New Datastream** $\rightarrow$ choose **Virtual Pin**.
5. Create each of the **10 Virtual Pins (V0 to V9)** according to the table below:

| Datastream Name | Pin | Data Type | Min | Max | Default | Unit | Hardware Component |
|---|---|---|---|---|---|---|---|
| **Living Room Light** | `V0` | Integer | `0` | `1` | `0` | None | Relay Channel 1 (GPIO 18) |
| **Bedroom Light** | `V1` | Integer | `0` | `1` | `0` | None | LED Module (GPIO 21) |
| **Smart DC Fan** | `V2` | Integer | `0` | `1` | `0` | None | Relay Channel 2 (GPIO 19) |
| **Room Temperature** | `V3` | Double | `0.0` | `50.0` | `24.0` | °C (Celsius) | DHT11 Sensor (GPIO 4) |
| **Room Humidity** | `V4` | Integer | `0` | `100` | `50` | % (Percentage) | DHT11 Sensor (GPIO 4) |
| **PIR Motion Sensor** | `V5` | Integer | `0` | `1` | `0` | None | PIR Sensor (GPIO 13) |
| **Light Brightness** | `V6` | Integer | `0` | `100` | `72` | % (Percentage) | PWM / Atmosphere Dimmer |
| **Thermostat Setpoint**| `V7` | Double | `16.0` | `30.0` | `22.0` | °C (Celsius) | Target Climate Temp |
| **Master Auto Mode** | `V8` | Integer | `0` | `1` | `1` | None | 0=Manual, 1=Auto |
| **Away Security Mode** | `V9` | Integer | `0` | `1` | `0` | None | 0=Home, 1=Away |

6. Click **Save Changes** in the top right corner.

---

## 🖥️ STEP 2: Configure Web Dashboard in Blynk Console

1. In the same Template (`Home automation system`), click the **Web Dashboard** tab.
2. Drag and drop the following widgets from the left widget drawer:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        BLYNK WEB DASHBOARD                             │
├─────────────────────────┬───────────────────────┬──────────────────────┤
│ 💡 [Switch: V0]         │ 💡 [Switch: V1]       │ 🌀 [Switch: V2]      │
│ Living Room Light       │ Bedroom Light         │ Smart DC Fan         │
├─────────────────────────┼───────────────────────┼──────────────────────┤
│ 🌡️ [Gauge: V3]          │ 💧 [Radial Gauge: V4] │ 🚶 [LED / State: V5] │
│ Temperature (0-50 °C)   │ Humidity (0-100 %)    │ PIR Motion (Clear/ON)│
├─────────────────────────┴───────────────────────┼──────────────────────┤
│ ☀️ [Slider: V6] Light Brightness (0-100%)       │ 🛡️ [Switch: V9]      │
├─────────────────────────────────────────────────┤ Away Security Mode   │
│ 🎯 [Slider / Step: V7] Thermostat Setpoint      │                      │
└─────────────────────────────────────────────────┴──────────────────────┘
```

3. **Widget Settings:**
   - **Switch 1:** Title: *Living Room Light* $\rightarrow$ Datastream: `V0`.
   - **Switch 2:** Title: *Bedroom Light* $\rightarrow$ Datastream: `V1`.
   - **Switch 3:** Title: *Smart DC Fan* $\rightarrow$ Datastream: `V2`.
   - **Gauge 1:** Title: *Temperature* $\rightarrow$ Datastream: `V3` (Color: Emerald/Mint).
   - **Gauge 2:** Title: *Humidity* $\rightarrow$ Datastream: `V4` (Color: Sky Blue).
   - **LED Widget:** Title: *Motion Sensor* $\rightarrow$ Datastream: `V5` (Color: Coral/Orange).
   - **Slider 1:** Title: *Ceiling Brightness* $\rightarrow$ Datastream: `V6`.
   - **Slider 2:** Title: *Thermostat Target* $\rightarrow$ Datastream: `V7`.
   - **Switch 4:** Title: *Away Mode* $\rightarrow$ Datastream: `V9`.
4. Click **Save And Apply**.

---

## 📱 STEP 3: Configure Mobile Dashboard (Android / iOS App)

1. Open the **Blynk IoT** app on your phone.
2. Open your device: **Home automation system**.
3. Tap the **Wrench icon** 🔧 in the top right to enter **Edit Mode**.
4. Tap **+** to add widgets:
   - **Button 1:** Set to `V0` (Mode: Switch, Label: "Living Room Light").
   - **Button 2:** Set to `V1` (Mode: Switch, Label: "Bedroom Light").
   - **Button 3:** Set to `V2` (Mode: Switch, Label: "Smart DC Fan").
   - **Value Display / Gauge 1:** Set to `V3` (Title: "Temperature").
   - **Value Display / Gauge 2:** Set to `V4` (Title: "Humidity").
   - **LED Widget:** Set to `V5` (Title: "Motion Alert").
   - **Slider 1:** Set to `V6` (Title: "Brightness", Min: 0, Max: 100).
   - **Step / Slider 2:** Set to `V7` (Title: "Target °C", Min: 16, Max: 30).
   - **Styled Button:** Set to `V9` (Title: "Away Mode", Mode: Switch).
5. Exit Edit Mode.

---

## ⚡ STEP 4: Flash the ESP32 Hardware

### 1. Arduino IDE Prerequisites
1. Install [Arduino IDE](https://www.arduino.cc/en/software) (version 2.x recommended).
2. Go to **Tools** $\rightarrow$ **Manage Libraries...** and install:
   - **Blynk** by *Volodymyr Shymanskyy* (version `1.3.2` or later).
   - **DHT sensor library** by *Adafruit* (version `1.4.6` or later).
   - **Adafruit Unified Sensor** by *Adafruit*.

### 2. Configure Wi-Fi in the Code
Open [`esp32/esp32_blynk/esp32_blynk.ino`](file:///c:/Users/chipp/Desktop/Home%20automation/esp32/esp32_blynk/esp32_blynk.ino) and update your Wi-Fi credentials around line 40:

```cpp
char ssid[] = "YOUR_WIFI_NAME";        // Your 2.4GHz Wi-Fi SSID
char pass[] = "YOUR_WIFI_PASSWORD";    // Your Wi-Fi Password
```

*(Note: The Blynk Template ID, Name, and Auth Token are already filled in!)*

### 3. Upload Code to ESP32
1. Connect your ESP32 to your computer via USB.
2. In Arduino IDE:
   - Select Board: **ESP32 Dev Module** (or your specific ESP32 variant).
   - Select Port: **COMx** (e.g., `COM3`, `COM4`).
3. Click the **Upload** arrow button (Ctrl+U).
4. Open the **Serial Monitor** at **115200 baud**.
5. You will see:
   ```text
   Connecting to YOUR_WIFI_NAME...
   WiFi connected. IP: 192.168.1.xxx
   Connecting to blynk.cloud...
   Ready (ping: 42ms)!
   [Blynk] Home Automation IoT Firmware Active
   ```

---

## 🌐 STEP 5: Connect the HAVEN 3D Web Dashboard

1. Open the HAVEN Web Dashboard (locally at `http://localhost:8000` or on your deployed Vercel URL).
2. Notice the top-bar status pill:
   - When ESP32 is running: **`BLYNK ONLINE`** with a pulsing green indicator.
   - When ESP32 is off: **`BLYNK READY`** with an amber indicator.
3. Click on **`BLYNK IOT`** (or the Blynk layer icon in the left rail):
   - Opens the **Blynk IoT Cloud Sync** spatial modal.
   - Displays live ping latency, hardware connection status, and datastream mapping.
   - Allows testing ping latency with 1-click.

### Bidirectional Real-Time Interaction
- **Turn On Lights on the Web:** Instantly turns on Relay 1 (GPIO 18) and flips the switch in your mobile Blynk app.
- **Flip Switch in Blynk Mobile App:** Instantly turns on/off the light card on the web and updates the room lighting!
- **Motion Trigger (PIR Sensor):** Detects movement $\rightarrow$ illuminates the live camera motion HUD on the web and lights up the LED widget in your mobile app!
- **Temperature & Fan Automation:** DHT11 sends real-time temp to `V3`. If temperature exceeds 30°C, the ESP32 automatically triggers the fan (`V2`) and syncs across web and mobile.

---

## 🛠️ Verification & Troubleshooting Checklist

| Issue | Root Cause | Solution |
|---|---|---|
| Serial monitor says `[Blynk] Invalid auth token` | Token mismatch | Verify token is `uoGRAIK7HuhPRSeQQPfoN5p4yPTR2bq0` in `esp32_blynk.ino`. |
| Web app says `BLYNK READY` but hardware offline | ESP32 not powered | Plug in ESP32 via USB and ensure it connects to your 2.4GHz Wi-Fi network. |
| Datastreams show `Bad Request (400)` | Datastreams not created | Go to `blynk.cloud` and create virtual pins V0 through V9 in your template. |
| Relay does not click | Relay polarity inverted | Modules use Active LOW logic: `LOW = ON`, `HIGH = OFF` (already handled in firmware). |
