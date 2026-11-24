# Complete Installation & Setup Guide
**Project:** Home Automation System | Python, IoT & Home Assistant

Follow this step-by-step beginner guide to deploy the complete home automation platform on your local workstation and hardware.

---

## 1. Installing Home Assistant Locally

Choose the easiest method for your environment:

### Method A: Home Assistant OS via VirtualBox (Recommended for Windows/Mac)
1. Download and install [VirtualBox](https://www.virtualbox.org/).
2. Download the official Home Assistant OS VirtualBox image (`.vdi` or `.ova`) from [home-assistant.io/installation/windows](https://www.home-assistant.io/installation/windows/).
3. In VirtualBox:
   - Create a new VM: Name: `HomeAssistant`, Type: `Linux`, Version: `Linux 2.6 / 3.x / 4.x / 5.x (64-bit)`.
   - Allocate **2 GB RAM** and **2 vCPUs**.
   - Attach the downloaded `.vdi` as the Primary Virtual Hard Disk.
   - Set Network Adapter to **Bridged Adapter** (so Home Assistant gets an IP on your home Wi-Fi subnet).
4. Start the VM. After 2–3 minutes, the terminal displays:
   ```text
   Home Assistant URL: http://homeassistant.local:8123 (or http://<LOCAL_IP>:8123)
   ```

### Method B: Home Assistant Container via Docker (Lightweight)
If you have Docker installed on Windows/Linux:
```bash
docker run -d \
  --name homeassistant \
  --privileged \
  --restart=unless-stopped \
  -e TZ=Asia/Kolkata \
  -v "C:/Users/chipp/Desktop/Home automation/homeassistant:/config" \
  --network=host \
  ghcr.io/home-assistant/home-assistant:stable
```

Access the web interface at `http://localhost:8123`.

---

## 2. Initial Home Assistant Onboarding
1. Open your browser and navigate to `http://localhost:8123` or `http://homeassistant.local:8123`.
2. Enter your Name, Username, and Password to create the owner account.
3. Set your Home Location and Time Zone.
4. Click **Finish**.

---

## 3. Configuring the ESP32

You have two simple options for flashing the ESP32:

### Option A: ESPHome (Zero-Code, Native Home Assistant)
1. In Home Assistant, navigate to **Settings** $\rightarrow$ **Add-ons** $\rightarrow$ **ESPHome** (or visit [web.esphome.io](https://web.esphome.io/) in Google Chrome or Edge).
2. Connect your ESP32 to your PC via a micro-USB / USB-C data cable.
3. Click **+ New Device** in ESPHome.
4. Name the device `home-automation-esp32`.
5. Copy the contents of [`esp32/esphome_node.yaml`](../esp32/esphome_node.yaml) into the ESPHome configuration editor.
6. Replace `YOUR_WIFI_SSID` and `YOUR_WIFI_PASSWORD` with your local Wi-Fi credentials.
7. Click **Install** $\rightarrow$ **Plug into this computer** to flash the ESP32 directly via Web Serial.

### Option B: Arduino IDE with MQTT
1. Open Arduino IDE.
2. Install the ESP32 board package via Boards Manager: `esp32 by Espressif Systems`.
3. Install required libraries via Library Manager:
   - `PubSubClient` by Nick O'Leary
   - `DHT sensor library` by Adafruit
   - `ArduinoJson` (v6.x) by Benoit Blanchon
4. Open [`esp32/esp32_arduino_mqtt/esp32_arduino_mqtt.ino`](../esp32/esp32_arduino_mqtt/esp32_arduino_mqtt.ino).
5. Update `WIFI_SSID`, `WIFI_PASSWORD`, and `MQTT_SERVER` (IP address of your PC / Home Assistant).
6. Select Board: **ESP32 Dev Module**, choose the correct COM port, and click **Upload**.

---

## 4. Connecting Sensors and Circuit Wiring

Connect the breadboard according to [`docs/CIRCUIT_AND_WIRING.md`](./CIRCUIT_AND_WIRING.md):
- **DHT11**: DATA $\rightarrow$ GPIO 4, VCC $\rightarrow$ 3.3V, GND $\rightarrow$ GND.
- **PIR Sensor**: OUT $\rightarrow$ GPIO 13, VCC $\rightarrow$ VIN (5V), GND $\rightarrow$ GND.
- **2-Channel Relay**:
  - IN1 $\rightarrow$ GPIO 18 (Living Room Light)
  - IN2 $\rightarrow$ GPIO 19 (DC Fan)
  - VCC $\rightarrow$ VIN (5V), GND $\rightarrow$ GND
- **Bedroom Light (LED)**: GPIO 21 $\rightarrow$ 220Ω Resistor $\rightarrow$ Anode (+), Cathode (-) $\rightarrow$ GND.

---

## 5. Integrating ESP32 with Home Assistant

### When using ESPHome:
- Home Assistant will automatically discover the node on your network via mDNS!
- A notification will pop up: *"Discovered ESPHome: home-automation-esp32"*.
- Click **Configure** $\rightarrow$ **Submit**.
- Assign entities to areas:
  - `Living Room Light` $\rightarrow$ **Living Room**
  - `Living Room Fan` $\rightarrow$ **Living Room**
  - `Living Room Motion Sensor` $\rightarrow$ **Living Room**
  - `Room Temperature & Humidity` $\rightarrow$ **Living Room**
  - `Bedroom Light` $\rightarrow$ **Bedroom**

### When using MQTT:
1. In Home Assistant, install the **Mosquitto Broker** add-on under **Settings $\rightarrow$ Add-ons**.
2. Start the broker and add the MQTT Integration (**Settings $\rightarrow$ Devices & Services $\rightarrow$ Add Integration $\rightarrow$ MQTT**).
3. The ESP32 Arduino firmware publishes auto-discovery payloads on boot, creating the entities immediately.

---

## 6. Copying Configuration Files

Copy the provided project configuration files into your Home Assistant configuration directory (`/config`):
- [`homeassistant/configuration.yaml`](../homeassistant/configuration.yaml)
- [`homeassistant/automations.yaml`](../homeassistant/automations.yaml)
- [`homeassistant/scripts.yaml`](../homeassistant/scripts.yaml)

In Home Assistant:
1. Go to **Developer Tools** $\rightarrow$ **YAML**.
2. Click **Check Configuration**.
3. If valid, click **Restart Home Assistant** (or reload Automations, Scripts, and Template Entities).

---

## 7. Configuring the Dashboard (Lovelace UI)

1. In Home Assistant, click on the **Overview** page.
2. In the top right corner, click the three dots ($\dots$) and select **Edit Dashboard**.
3. Click the three dots again and select **Raw configuration editor**.
4. Replace the default YAML with the contents of [`homeassistant/ui-lovelace.yaml`](../homeassistant/ui-lovelace.yaml).
5. Click **Save** and close the editor.
6. The dark smart-home dashboard is now active with room organization, climate gauges, device counts, and mode toggles!

---

## 8. Verifying Automations

Test all 5 workflows in sequence:

| Workflow | How to Trigger | Expected System Response |
|---|---|---|
| **1. Motion Lighting** | Wave hand in front of PIR sensor | Living Room Light turns ON immediately; turns OFF after 30 seconds of no motion. |
| **2. Temperature Fan** | Breathe warm air onto DHT11 (or simulate temp > 30°C) | Fan turns ON when temp exceeds 30°C; stays ON until cooling drops below 28°C. |
| **3. Night Mode** | Toggle `input_boolean.night_mode` on dashboard | Bedroom light and living room light turn off; night security rules engaged. |
| **4. Away Mode** | Toggle `input_boolean.away_mode` on dashboard | All lights and fans turn OFF immediately; status updates to "Away (Secured)". |
| **5. Manual Override** | Click switch toggle directly on dashboard | Sets `input_boolean.manual_override` to True, preserving user state. |

---

## 9. Running Python Integration & Simulator

If you are demonstrating the project in a classroom or lab without live hardware:

```bash
# Navigate to python_backend folder
cd python_backend

# Run automated unit test suite
python test_automations.py

# Run standalone logic verification
python ha_controller.py

# Run interactive CLI mock simulator
python mock_simulator.py
```

---

## 10. Troubleshooting Common Issues

### Issue 1: DHT11 returns NaN or failed readings
- **Cause**: Inadequate power supply or loose jumper wire.
- **Fix**: Connect DHT11 VCC to 5V (if module has onboard regulator) or 3.3V (bare sensor). If using a bare 4-pin DHT11, place a 10kΩ pull-up resistor between VCC and DATA.

### Issue 2: PIR sensor triggers constantly or false triggers
- **Cause**: PIR sensor sensitivity/time delay potentiometers not calibrated, or Wi-Fi RF interference.
- **Fix**: Turn the sensitivity potentiometer counter-clockwise. Add a 2–3 second debounce filter in firmware (already included in `esphome_node.yaml`). Keep PIR sensor at least 15 cm away from the ESP32 Wi-Fi antenna.

### Issue 3: Relay logic inverted (Light turns ON when HA shows OFF)
- **Cause**: Hobby relay boards use Active-LOW optocouplers.
- **Fix**: In `esphome_node.yaml`, verify `inverted: true` is set on GPIO 18 and GPIO 19.

### Issue 4: ESP32 fails to connect to Wi-Fi
- **Cause**: ESP32 only supports **2.4 GHz Wi-Fi** networks; 5 GHz networks are not supported.
- **Fix**: Connect your smartphone and ESP32 to the 2.4 GHz band of your router or smartphone mobile hotspot.
