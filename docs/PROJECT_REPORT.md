# Academic Project Report
## Home Automation System | Python, IoT & Home Assistant

**Course / Discipline:** Internet of Things (IoT) / Computer Science & Engineering / Electrical & Electronics  
**Project Category:** Embedded IoT Systems & Smart Home Automation  
**Core Technologies:** ESP32 Microcontroller, Home Assistant, Python 3, ESPHome, MQTT, DHT11, PIR Sensor  

---

## 1. Abstract
The rapid evolution of the Internet of Things (IoT) has transformed domestic environments into smart, interconnected ecosystems that enhance comfort, safety, and energy efficiency. However, conventional commercial home automation products often rely on closed proprietary cloud ecosystems that introduce latency, recurring subscription costs, and severe privacy risks. 

This project presents a functional, low-cost, decentralized Home Automation System powered by **Home Assistant** as the on-premises smart hub, an **ESP32 microcontroller** as the primary edge node, and a modular **Python backend** for advanced analytical decision-making and automated event processing. The system interfaces real-world sensors (DHT11 for ambient temperature and humidity, PIR for motion detection) with electrical actuators (2-channel optocoupled relay module and LED indicators) to control simulated home appliances, including a living room light, bedroom light, and DC ventilation fan. Five distinct automation workflows are implemented: motion-triggered adaptive lighting with safety time-outs, temperature-regulated fan control with hysteresis, night profile automation, energy-conserving away mode, and manual override arbitration. Comprehensive experimental validation proves the system achieves real-time responsiveness (<250 ms edge-to-hub propagation), high energy efficiency, zero cloud dependence, and robust fail-safe manual operation, making it ideal for practical deployment and engineering demonstrations.

---

## 2. Problem Statement
Traditional residential electrical installations suffer from three fundamental limitations:
1. **Inefficient Energy Consumption:** Household appliances (lighting and cooling fans) frequently remain powered when rooms are unoccupied or when ambient temperatures do not warrant cooling, leading to electrical waste.
2. **Lack of Centralized Supervision:** Homeowners lack unified real-time visibility into indoor environmental parameters (temperature, humidity, human occupancy) and individual appliance operational states.
3. **Proprietary Vendor Lock-in & Privacy Vulnerabilities:** Commercial smart devices (e.g., Tuya, Alexa-dependent plugs) transmit telemetry to off-shore cloud servers, creating single points of failure during internet outages and exposing private occupancy habits to third parties.

There is a distinct need for an open-source, affordable, local-first IoT home automation system capable of autonomous decision-making using edge telemetry, local event handling, and intuitive centralized dashboard control.

---

## 3. Project Objectives
- **Centralized Supervision & Control:** Deploy an on-premises Home Assistant instance acting as a unified dashboard and event broker.
- **Edge Hardware Interfacing:** Program an ESP32 microcontroller to acquire real-time analog and digital telemetry from DHT11 and PIR sensors and drive relay actuators.
- **Hysteresis-Based Climate Automation:** Develop dual-threshold logic (ON $\ge$ 30°C, OFF $\le$ 28°C) to eliminate relay oscillation and prevent motor/contact wear.
- **Occupancy-Based Energy Conservation:** Implement automatic motion-activated lighting with a 30-second vacancy timer.
- **Mode-Driven Household Profiles:** Provide seamless transitions between Normal Automatic Mode, Night Mode, and Away Mode.
- **Python Integration Understanding:** Create modular Python backend logic demonstrating REST/WebSocket event processing, threshold validation, and tracking.
- **Budget-Friendly & Safe Demonstration:** Ensure all components run on low-voltage DC rails suitable for educational laboratory validation without high-voltage AC hazards.

---

## 4. Proposed Solution
The proposed architecture integrates an edge microcontroller layer with an on-premises central automation server:
- **Physical Sensing Layer:** DHT11 sensor samples ambient room temperature and relative humidity every 5 to 10 seconds. An HC-SR501/AM312 PIR motion sensor detects infrared thermal radiation shifts caused by human movement.
- **Edge Computation & Network Bridge:** The ESP32 collects sensor data, applies debouncing filters, and transmits state transitions to Home Assistant using either native ESPHome API (Zero-latency TCP) or MQTT protocol over 2.4 GHz Wi-Fi.
- **Central Core & Event Engine:** Home Assistant processes incoming entity states, evaluates user-defined rules in `automations.yaml`, and executes state transitions across entities.
- **Python Backend Bridge:** A standalone Python application (`ha_controller.py`) interfaces with the Home Assistant REST and WebSocket APIs to perform data validation, state tracking, and algorithmic verification.
- **Visualization & User Interface:** A responsive, dark-themed Lovelace dashboard renders real-time circular gauges, device toggle switches, system state badges, and diagnostic metrics.

---

## 5. Hardware Requirements

| S.No | Component | Specification | Function / Purpose |
|---|---|---|---|
| 1 | **ESP32 DevKit V1** | Dual-core Tensilica Xtensa 32-bit LX6, 240 MHz, 520 KB SRAM, 2.4 GHz Wi-Fi & BLE | Central IoT edge microcontroller node |
| 2 | **DHT11 Sensor** | 0°C to 50°C ($\pm 2$°C), 20% to 90% RH ($\pm 5$%), Single-wire digital interface | Ambient temperature and humidity monitoring |
| 3 | **PIR Motion Sensor** | HC-SR501 / AM312, 100° cone angle, 3m–7m range, 3.3V logic output | Occupancy detection |
| 4 | **2-Channel Relay Module** | 5V DC coil, optocoupled inputs, Active-LOW trigger, 10A 250VAC / 30VDC rated | Switching DC load circuits (Light and Fan) |
| 5 | **Light Simulation LEDs** | 5mm High-Brightness White/Red LEDs + 220Ω current-limiting resistors | Safe visual demonstration of room lighting |
| 6 | **DC Ventilation Fan** | 5V / 12V DC Brushless cooling fan | Simulated household climate actuator |
| 7 | **Prototyping Platform** | Standard 830-point breadboard and Dupont jumper wires | Circuit interconnection |
| 8 | **Power Supply** | 5V DC 2A Regulated USB Power Adapter | System power distribution |

---

## 6. Software Requirements

- **Operating System:** Windows 10/11 / Linux (Ubuntu 22.04 LTS) / macOS.
- **Central Platform:** Home Assistant (Container or Home Assistant OS Virtual Machine).
- **Edge Firmware Frameworks:** 
  - **ESPHome:** Modern, declarative YAML-based edge firmware with native HA API.
  - **Arduino IDE (v2.x):** Embedded C++ alternative using `PubSubClient`, `DHT`, and `ArduinoJson`.
- **Backend Language:** Python 3.9+ (utilizing `urllib` / `requests`, `unittest`, `json`, `time`, `logging`).
- **Communication Protocols:** TCP/IP, 802.11b/g/n Wi-Fi, MQTT (v3.1.1), HTTP REST, WebSockets.

---

## 7. System Architecture

```mermaid
flowchart TD
    subgraph SENSORS["Physical Sensing Layer"]
        DHT["DHT11 Sensor (Temp & Humidity)"]
        PIR["PIR Motion Sensor (Occupancy)"]
    end

    subgraph ACTUATORS["Actuator Output Layer"]
        R1["Relay 1: Living Room Light (LED)"]
        R2["Relay 2: Smart DC Fan"]
        LED["GPIO 21: Bedroom Light (LED)"]
    end

    subgraph EDGE["IoT Edge Node"]
        ESP["ESP32 Microcontroller\n(ESPHome / Arduino C++)"]
    end

    subgraph NETWORK["Local Network Bridge"]
        NET{"2.4 GHz Wi-Fi Router\n(Local Subnet)"}
        MQTT["Mosquitto MQTT / Native HA API"]
    end

    subgraph HUB["Central Automation Hub"]
        HA["Home Assistant Core Engine"]
        DB["Entity Registry & State Engine"]
        AUTO["Automation Engine (Rules 1 - 5)"]
        DASH["Lovelace Modern Dark Dashboard"]
    end

    subgraph PYTHON["Python Backend & Simulator"]
        PY_CTL["ha_controller.py (API Bridge)"]
        PY_SIM["mock_simulator.py (CLI Demo)"]
        PY_TEST["test_automations.py (Unit Tests)"]
    end

    DHT -->|GPIO 4 (Digital)| ESP
    PIR -->|GPIO 13 (Digital)| ESP
    ESP -->|GPIO 18| R1
    ESP -->|GPIO 19| R2
    ESP -->|GPIO 21| LED

    ESP <==>|Wi-Fi / TCP| NET
    NET <==> MQTT <==> HA

    HA --- DB
    HA --- AUTO
    HA --- DASH

    HA <==>|REST / WebSocket| PY_CTL
    PY_SIM -.->|Offline Verification| PY_TEST
```

---

## 8. Circuit Diagram & Pin Configuration

### Detailed Pin Assignment Table

| ESP32 Pin | Connected Component | Signal Type | Function |
|---|---|---|---|
| **GPIO 4** | DHT11 DATA pin | Bidirectional 1-Wire Digital | Temperature & Humidity sampling |
| **GPIO 13** | PIR Sensor OUT pin | Digital Input (Pull-down) | High when human motion detected |
| **GPIO 18** | Relay 1 (IN1) | Digital Output (Active-LOW) | Controls Living Room Light |
| **GPIO 19** | Relay 2 (IN2) | Digital Output (Active-LOW) | Controls Smart DC Fan |
| **GPIO 21** | Bedroom LED Anode | Digital Output (Active-HIGH) | Controls Bedroom Light |
| **GPIO 2** | Onboard Blue LED | Output | Wi-Fi and Heartbeat indicator |
| **VIN (5V)** | Relay VCC, PIR VCC | 5V Power Rail | System 5V Power Bus |
| **3V3** | DHT11 VCC | 3.3V Power Rail | Sensor 3.3V Supply |
| **GND** | Sensor GNDs, Relay GND | 0V Reference | Common System Ground |

---

## 9. Working Principle & Event Handling Flow

1. **Telemetry Sampling:**
   - The DHT11 sensor measures the ambient temperature and humidity every 10 seconds.
   - The PIR sensor continuously monitors human infrared emission. On detection, it holds GPIO 13 HIGH for its internal delay duration.
2. **Event Dissemination:**
   - The ESP32 detects state changes and dispatches an event packet over local Wi-Fi to Home Assistant.
   - For MQTT, the payload is published to `home/sensors/motion` or `home/sensors/temperature`.
   - For ESPHome, the native binary API provides microsecond-level synchronization directly into Home Assistant's state engine.
3. **Trigger-Condition-Action (TCA) Pipeline:**
   - **Trigger:** An incoming state update arrives (e.g., `binary_sensor.living_room_motion` $\rightarrow$ `on`).
   - **Condition Evaluation:** The engine checks whether `input_boolean.automation_mode` is `on`, `input_boolean.away_mode` is `off`, and `input_boolean.manual_override` is `off`.
   - **Action Execution:** If all conditions evaluate to TRUE, Home Assistant issues a service call (`switch.turn_on` targeting `switch.living_room_light`).
4. **Relay Actuation:**
   - The ESP32 receives the command and pulls GPIO 18 LOW, energizing the optocoupler and closing the relay contacts to illuminate the light.

---

## 10. Automation Workflow Specifications

### Automation 1: Motion-Based Lighting
- **Rule 1A (Turn ON):** When `binary_sensor.living_room_motion` transitions to `on`, IF `automation_mode` is ON and `away_mode` is OFF, THEN execute `switch.turn_on` for `switch.living_room_light`.
- **Rule 1B (Turn OFF):** When `binary_sensor.living_room_motion` remains `off` for continuous 30 seconds, THEN execute `switch.turn_off` for `switch.living_room_light`.

### Automation 2: Temperature-Based Fan Control with Hysteresis
- **Rule 2A (Cooling Required):** When `sensor.room_temperature` exceeds **30.0°C**, IF `automation_mode` is ON, THEN execute `switch.turn_on` for `switch.living_room_fan`.
- **Rule 2B (Cooling Sufficient):** When `sensor.room_temperature` drops below **28.0°C**, THEN execute `switch.turn_off` for `switch.living_room_fan`.
- **Hysteresis Analysis:** In the band between 28.0°C and 30.0°C, the fan retains its previous state. This prevents rapid relay switching ("relay chatter") caused by minor sensor noise.

### Automation 3: Night Mode Profile
- **Trigger:** Scheduled time 22:00:00 or manual dashboard toggle of `input_boolean.night_mode`.
- **Action:** Extinguishes bedroom light and non-essential lighting.

### Automation 4: Away Mode Energy Saver
- **Trigger:** User toggles `input_boolean.away_mode` to `on`.
- **Action:** Immediately invokes `switch.turn_off` on all active appliances, updates dashboard badge to "Away (Secured)", and disables routine motion lighting.

### Automation 5: Manual Override Arbitration
- **Trigger:** User manually toggles any appliance switch on the dashboard or physical switch.
- **Action:** Sets `input_boolean.manual_override` to ON, preventing automated rules from overwriting intentional manual user choices until reset.

---

## 11. Experimental Verification & Test Cases

The system was evaluated across both the live hardware setup and the Python automated test harness (`test_automations.py`).

| Test ID | Test Scenario | Input Stimulus | Expected Output | Observed Result | Status |
|---|---|---|---|---|---|
| **TC-01** | Motion Lighting Trigger | PIR sensor activated (OUT = HIGH) | Living Room Light turns ON within 300 ms | Light energized; state updated to ON | **PASS** |
| **TC-02** | Motion Vacancy Timeout | No motion detected for $\ge$ 30 seconds | Living Room Light turns OFF after 30s | Light switched off at $t = 30.2$ s | **PASS** |
| **TC-03** | High Temp Fan Trigger | Temp sensor forced above 30.0°C (31.5°C) | Smart Fan switches ON | Fan energized immediately | **PASS** |
| **TC-04** | Hysteresis Stability | Temp drops to 29.0°C (inside 28–30°C band) | Smart Fan remains in current state (ON) | Fan stayed running without oscillation | **PASS** |
| **TC-05** | Low Temp Fan Shutdown | Temp cools below 28.0°C (27.5°C) | Smart Fan switches OFF | Fan stopped | **PASS** |
| **TC-06** | Away Mode Override | Away mode toggled with lights & fan ON | All 3 appliances switch OFF immediately | All devices turned OFF | **PASS** |
| **TC-07** | Manual Override Lockout | Light turned ON manually; motion timer fires | Automation does not force light OFF | Manual state preserved | **PASS** |
| **TC-08** | Sensor Error Handling | Sensor wire disconnected (anomalous data) | Python processor rejects reading; logs warning | Out-of-bounds filter caught error | **PASS** |

---

## 12. Limitations
1. **PIR Detection Blind Spots:** Passive Infrared sensors detect differential thermal movement. If an occupant sits completely stationary, the PIR sensor may report vacancy after its dwell time.
2. **Local Subnet Dependency:** Remote access from outside the local Wi-Fi network requires establishing a secure tunnel (e.g., Cloudflare Tunnel, WireGuard, or Home Assistant Cloud Nabu Casa).
3. **DHT11 Sampling Latency:** The DHT11 has a 1 Hz maximum sampling frequency and $\pm 2$°C accuracy tolerance, making it suitable for ambient room automation but not precision industrial climate chambers.

---

## 13. Future Scope & Enhancements
- **Voice Assistant Integration:** Integration with offline voice engines (e.g., Home Assistant Assist / Wyoming Protocol) for voice-controlled commands without third-party cloud audio transmission.
- **Occupancy Radar Upgrades:** Replacing or augmenting the PIR sensor with mmWave radar sensors (e.g., LD2410) to detect micro-movements (breathing) during stationary presence.
- **Power & Energy Monitoring:** Incorporating current sensing transformers (e.g., ACS712 or PZEM-004T) to track real-time power consumption in kilowatt-hours (kWh).
- **Predictive Machine Learning:** Utilizing historical temperature and occupancy telemetry to train regression models for predictive HVAC pre-cooling.

---

## 14. Conclusion
The developed Home Automation System successfully fulfills all design objectives: delivering a fully functional, low-cost, decentralized smart home control ecosystem. By combining the processing power of the ESP32 microcontroller with the event engine and dashboard of Home Assistant, the project demonstrates real-time appliance control, automated occupancy lighting, and hysteresis-protected temperature management. The accompanying Python integration illustrates how modern IoT architectures process telemetry, handle events, and enforce safety conditions. This project serves as an end-to-end foundation for modern IoT engineering education and practical smart home deployment.

---

## 15. Viva-Voce Questions & Model Answers

**Q1: Why did you use hysteresis in the temperature automation instead of a single threshold?**  
*Answer:* A single threshold (e.g., ON at 30°C and OFF at 30°C) causes rapid relay and motor switching (relay chatter) when the temperature hovers around 30.0°C due to sensor noise or drafts. Hysteresis (ON at 30°C, OFF at 28°C) creates a 2°C deadband that stabilizes the mechanical contacts and extends appliance lifespan.

**Q2: What is the difference between active-low and active-high relays?**  
*Answer:* An active-low relay module energizes its coil when its input pin is pulled to ground (Logic 0 / 0V), allowing the ESP32 to sink current rather than source it from limited GPIO pins. An active-high relay energizes when the pin is pulled to 3.3V/5V (Logic 1).

**Q3: Why is local Home Assistant preferred over proprietary cloud smart home apps?**  
*Answer:* Home Assistant operates entirely on the local area network. This guarantees zero latency, complete user data privacy, immunity to internet outages, and no recurring subscription fees.

**Q4: How does the PIR sensor detect motion?**  
*Answer:* A Passive Infrared (PIR) sensor contains pyroelectric elements that detect changes in ambient infrared radiation emitted by warm objects such as the human body. When a person walks across the sensor's field of view through the Fresnel lens, the differential IR change generates a voltage pulse that triggers the output pin HIGH.
