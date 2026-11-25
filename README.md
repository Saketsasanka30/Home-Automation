# 🏡 Smart Home Automation System
### *Built with ESP32, Home Assistant, Python, Blynk IoT & the HAVEN Spatial Dashboard*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-Core%20%7C%20OS-brightgreen.svg)](https://www.home-assistant.io/)
[![Blynk IoT 2.0](https://img.shields.io/badge/Blynk-IoT%202.0%20Ready-00c853.svg)](docs/BLYNK_INTEGRATION_GUIDE.md)
[![Hardware](https://img.shields.io/badge/Hardware-ESP32%20%7C%20DHT11%20%7C%20PIR%20%7C%20Relays-orange.svg)](#-the-physical-toys-hardware)

---

## 🧸 Explain Like I'm 5 (ELI5): How Does This Work?

Imagine your house is a **magical kingdom** 🏰, and you want it to take care of itself like in the movies!

Here is how each friend in the kingdom works together:

```
    👀 Eyes & Skin                   🦾 The Messenger                 🧠 The Super Butler
   [Sensors: PIR & DHT11]  ───────>    [ESP32 Chip]     ───────>    [Home Assistant Hub]
                                            │                                │
                                            │ <────── Commands ──────────────┘
                                            ▼
                                  ⚡ Magic Switch Hands
                                    [Relay Modules]
                                            │
                                            ▼
                                   💡 Lights & 🌀 Fans
```

### 1. 🧠 The "Brain" (Home Assistant)
Think of **Home Assistant** as a super-friendly, tireless **Butler** who lives inside a tiny computer in your house. 
- The Butler has a big notebook full of rules.
- Whenever something happens, the Butler checks his notebook: *"Oh! Someone walked into the living room! The rule says I must turn on the lights!"*

### 2. 👀 The "Eyes and Skin" (Sensors)
- **The Motion Sensor (PIR):** It has little invisible spider-senses. When you walk into the room, it notices your body heat moving and shouts: *"Hey! Someone is here!"*
- **The Weather Sensor (DHT11):** It acts like sensitive skin. It constantly checks how warm the room feels and how humid the air is: *"Whew, it is getting toasty in here, 31°C!"*

### 3. 🦾 The "Messenger Boy" (ESP32 Microcontroller)
The **ESP32** is a tiny, powerful computer chip with Wi-Fi antenna ears. 
- It listens to the eyes and skin (sensors).
- It runs super-fast over invisible Wi-Fi airwaves to tell the Butler (Home Assistant) what is going on.
- When the Butler shouts: *"Flip the switch!"*, the ESP32 catches the message and flips it!

### 4. ⚡ The "Magic Clicking Hands" (Relays)
A **Relay** is like a tiny robotic finger inside a little plastic box. 
- Normal computer chips use baby voltages (3.3 Volts) and cannot touch big electrical appliances directly.
- The relay acts as a safe bridge: when told to turn on, it goes **CLICK!** and lets electricity flow to turn on the lamp or spin the fan.

### 5. 🥽 The "Magic Floating Window" (HAVEN Spatial Dashboard)
Instead of boring ugly buttons, we built **HAVEN** — an interactive, visionOS-inspired glass dashboard that floats right in front of a sunlit living room! 
- You can drag a glowing mint thermostat ring.
- You can slide a brightness pill that **actually dims the room video in real time**.
- You can play music, watch live camera feeds, and check on your robot vacuum cleaner.

---

## ⚡ The 5 Superpowers (Automations Explained Simply)

| Superpower | What Happens in Plain English? | Why Is It Awesome? |
|---|---|---|
| 🚶 **1. Magic Motion Lights** | You walk into the room $\rightarrow$ the light pops **ON**! When everyone leaves and no movement is seen for **30 seconds**, the light turns **OFF**. | No more yelling *"Who left the lights on?!"* Saves electricity! |
| ❄️ **2. Smart Cool-Down Fan** | If room temperature climbs over **30°C**, the fan turns **ON**. When the breeze cools the room below **28°C**, it turns **OFF**. | Keeps you cozy automatically. Because of the 2° gap (*hysteresis*), the fan doesn't annoyingly turn on and off every two seconds! |
| 🌙 **3. Bedtime Night Mode** | At 10:00 PM (or when you tap Night Mode), bright lights shut off and the house enters night-security mode. | Wind down easily for sleep without bright lights shining in your eyes. |
| 🛡️ **4. The Vacation Shield (Away Mode)** | Leaving home? Tap **Away Mode** once! All lights turn off, fans stop spinning, and power is conserved. | Never worry whether you forgot to switch off an appliance before heading out. |
| 🕹️ **5. Humans Always Win (Manual Override)** | Want the light on even without moving? Just flip the switch yourself! The Butler recognizes your choice and won't fight with you. | Smart homes should obey you, not boss you around! |

---

## 📁 What's Inside This Repository?

```text
Home-Automation/
├── haven.html                        # 🥽 VisionOS spatial 3D glass dashboard (Single-file)
├── index.html                        # 🌐 Main web entry point (HAVEN interactive UI)
│
├── esp32/
│   ├── esp32_blynk/
│   │   └── esp32_blynk.ino           # 📱 Blynk IoT 2.0 firmware with pre-configured credentials
│   ├── esphome_node.yaml             # ⚡ Plug-and-play ESPHome firmware for Home Assistant
│   └── esp32_arduino_mqtt/
│       └── esp32_arduino_mqtt.ino    # 🔌 Arduino C++ firmware with MQTT auto-discovery
│
├── homeassistant/
│   ├── configuration.yaml           # 🧠 Home Assistant core entities & helper booleans
│   ├── automations.yaml             # ⚙️ All 5 complete automation rules
│   ├── scripts.yaml                 # 📜 Helper routines (All-off, Reset-auto, Test-blink)
│   ├── scenes.yaml                  # 🎬 One-tap atmosphere presets
│   └── ui-lovelace.yaml             # 📊 Clean dark smart-home dashboard
│
├── python_backend/
│   ├── ha_controller.py             # 🐍 Python REST & WebSocket API brain
│   ├── mock_simulator.py            # 🎮 Terminal hardware simulator (Test without hardware!)
│   ├── test_automations.py          # 🧪 Automated unit tests (7/7 passing)
│   └── requirements.txt             # 📦 Python dependencies
│
└── docs/
    ├── BLYNK_INTEGRATION_GUIDE.md   # 📱 Complete Blynk 2.0 Template & Mobile App setup guide
    ├── CIRCUIT_AND_WIRING.md        # 📐 Breadboard pin connections & safety guide
    ├── SETUP_AND_INSTALLATION.md    # 🛠️ 10-step complete setup guide
    └── PROJECT_REPORT.md            # 🎓 15-section academic engineering project report & viva Q&A
```

---

## 🎮 Try It Right Now (No Hardware Needed!)

You don't even need physical wires or sensors plugged in to test this project!

### Option 1: Launch the Interactive Floating Dashboard
Just double click **`index.html`** or **`haven.html`** in your browser!
- Tilt your mouse to see the 3D room parallax!
- Drag the mint thermostat dial.
- Drag the brightness slider to watch the living room video dim live!
- Tap the **Morning** scene to start the sunrise routine.

### Option 2: Run the Python Interactive Simulator
Open your terminal inside this folder and run:

```bash
# 1. Run the test suite (Verifies all 5 automations)
python python_backend/test_automations.py

# 2. Run the standalone logic pipeline
python python_backend/ha_controller.py

# 3. Launch the interactive CLI game/simulator
python python_backend/mock_simulator.py
```

You can press `1` to trigger motion, `3` to heat up the room, `6` to turn on Away Mode, and watch the appliances react instantly!

---

## 📱 Mobile & Cloud Control via Blynk IoT App

This project features official **Blynk IoT 2.0 Cloud** support! Control your appliances and monitor temperature/humidity directly from your iOS or Android smartphone from anywhere in the world.

### Virtual Pin Datastreams Mapping
| Pin | Function | Hardware / Action |
|:---:|---|---|
| **V0** | Living Room Light | Relay 1 (GPIO 18, Active LOW) |
| **V1** | Bedroom Light | LED Indicator (GPIO 21) |
| **V2** | Smart DC Fan | Relay 2 (GPIO 19, Active LOW) |
| **V3** | Live Temperature | DHT11 Sensor (GPIO 4, °C) |
| **V4** | Live Humidity | DHT11 Sensor (GPIO 4, %) |
| **V5** | Motion Detection | PIR Motion Sensor (GPIO 13) |
| **V6** | Light Brightness | PWM / Atmosphere Dimmer (0-100%) |
| **V7** | Thermostat Setpoint | Climate Target (16-30°C) |
| **V9** | Away Security Mode | Disarm / Arm household |

👉 **For the complete step-by-step mobile dashboard & cloud setup guide, see [`docs/BLYNK_INTEGRATION_GUIDE.md`](./docs/BLYNK_INTEGRATION_GUIDE.md).**

---

## 🛠️ The Physical Hardware (For Real Setup)

When you're ready to wire the real breadboard:

| Component | What It Does | Connected to ESP32 Pin |
|---|---|---|
| **ESP32 DevKit V1** | The master Wi-Fi brain node | — |
| **DHT11 Sensor** | Reads temperature & humidity | **GPIO 4** |
| **PIR Motion Sensor** | Senses moving human presence | **GPIO 13** |
| **Relay Channel 1** | Controls Living Room Light (LED) | **GPIO 18** (Active LOW) |
| **Relay Channel 2** | Controls DC Fan | **GPIO 19** (Active LOW) |
| **Bedroom LED** | Secondary bedroom light | **GPIO 21** |
| **Status LED** | Wi-Fi connection indicator | **GPIO 2** (Onboard) |

*For complete wiring schematics, pull-up resistors, and safety notes, see [`docs/CIRCUIT_AND_WIRING.md`](./docs/CIRCUIT_AND_WIRING.md).*

---

## 🎓 Academic Documentation & Viva Preparation

This project was built to meet college engineering standards:
- **[Full Academic Project Report](docs/PROJECT_REPORT.md)**: Problem statement, objectives, system architecture diagrams, test cases table, limitations, and future scope.
- **[Viva-Voce Questions & Answers](docs/PROJECT_REPORT.md#-15-viva-voce-questions--model-answers)**: Ready-made answers explaining hysteresis, active-low relays, MQTT discovery, and local-first architecture.
- **[Installation Guide](docs/SETUP_AND_INSTALLATION.md)**: 10 step-by-step setup instructions for Docker, VirtualBox, and ESPHome.

---

## 📜 License
This project is open-source under the [MIT License](LICENSE). Feel free to learn from it, build on it, and use it in your own projects!
