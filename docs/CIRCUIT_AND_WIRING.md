# Circuit Diagram & Wiring Guide
**Project:** Home Automation System | Python, IoT & Home Assistant  
**Hardware:** ESP32 Development Board, DHT11, PIR Motion Sensor, 2-Channel Relay Module, LEDs, 5V DC Fan

---

## 1. Master Pin Configuration Table

| Component | Component Pin / Wire | ESP32 Pin | Logic Level | Operating Voltage | Notes |
|---|---|---|---|---|---|
| **DHT11 Sensor** | VCC (+) | 3V3 (or 5V for module) | — | 3.3V – 5V | Use 3.3V for standard 3-pin module |
| | GND (-) | GND | — | 0V | Common Ground Rail |
| | DATA (Out) | **GPIO 4** | 3.3V | — | 10kΩ pull-up required if using bare 4-pin DHT11 |
| **PIR Motion Sensor** | VCC (+) | **VIN (5V)** | — | 5V DC | HC-SR501 requires 5V to onboard regulator |
| (HC-SR501 / AM312) | GND (-) | GND | — | 0V | Common Ground Rail |
| | OUT | **GPIO 13** | 3.3V logic | — | Output is 3.3V High when motion detected |
| **2-Channel Relay** | VCC | **VIN (5V)** | — | 5V DC | Powers optocoupler LEDs & coil drivers |
| | GND | GND | — | 0V | Common Ground Rail |
| | IN1 (Relay 1: Light) | **GPIO 18** | 3.3V | — | Active LOW (LOW = Relay ON, HIGH = OFF) |
| | IN2 (Relay 2: Fan) | **GPIO 19** | 3.3V | — | Active LOW (LOW = Relay ON, HIGH = OFF) |
| **Bedroom Light LED** | Anode (+) | **GPIO 21** | 3.3V | — | In series with 220Ω resistor |
| | Cathode (-) | GND | — | 0V | Common Ground Rail |
| **Onboard Status LED** | Onboard | **GPIO 2** | 3.3V | — | Blinks during Wi-Fi connect, solid ON when synced |

---

## 2. Power Supply Distribution & Rails

```
                +5V USB / External 5V Power Supply
                               │
               ┌───────────────┴───────────────┐
               │                               │
        ESP32 VIN Pin                   Breadboard +5V Rail
                                               │
                       ┌───────────────────────┼───────────────────────┐
                       │                       │                       │
                  PIR VCC Pin             Relay VCC Pin         External DC Fan
                                                                (via Relay COM)

               Common Ground (GND) Rail
                               │
       ┌───────────────┬───────┴───────┬───────────────┬───────────────┐
       │               │               │               │               │
   ESP32 GND        PIR GND        DHT11 GND       Relay GND       Fan (-) GND
```

> [!IMPORTANT]
> **Common Ground Rule**: Always connect the ESP32 GND, sensor GNDs, relay GND, and external load power supply GND together to form a common reference ground. Failing to do so causes erratic sensor readings and floating logic states.

---

## 3. High-Level Circuit Schematic (ASCII)

```
                       +-----------------------------------+
                       |        ESP32 DEV MODULE           |
                       |                                   |
    [DHT11 DATA] ----> | GPIO 4                     GPIO 18| ----> [Relay 1: IN1 (Light)]
                       |                                   |
      [PIR OUT] -----> | GPIO 13                    GPIO 19| ----> [Relay 2: IN2 (Fan)]
                       |                                   |
                       | GPIO 21 (Bed Light)        GPIO 2 | ----> [Onboard Status LED]
                       |    |                              |
                       |   [220Ω]                          |
                       |    |                              |
                       |   (LED+)                          |
                       |   (LED-)                          |
                       |    |                              |
                       |   GND                             |
                       |                                   |
           3V3 ------- | 3V3                           VIN | <---- +5V Power Supply
           GND ------- | GND                           GND | <---- Ground Power Rail
                       +-----------------------------------+

 RELAY 1 CONNECTIONS (Simulated Living Room Light):
  [Relay 1 COM] ---------> +5V DC Rail
  [Relay 1 NO]  ---------> [220Ω Resistor] -> [LED Anode (+)]
  [LED Cathode (-)] -----> GND Rail

 RELAY 2 CONNECTIONS (DC Fan Control):
  [Relay 2 COM] ---------> +5V / +12V DC External Fan Supply (+)
  [Relay 2 NO]  ---------> DC Fan Positive (+) Terminal
  [DC Fan Negative (-)] -> External Power Supply Ground (-) Rail
```

---

## 4. Relay Module & Actuator Wiring Details

### Optocoupled 2-Channel Relay Module
Most standard hobby relay modules feature **Active-LOW logic**:
- **Logic LOW (0V / False on GPIO)**: Current flows through internal optocoupler LED $\rightarrow$ Relay coil energizes $\rightarrow$ NO (Normally Open) contact closes $\rightarrow$ Connected appliance turns **ON**.
- **Logic HIGH (3.3V / True on GPIO)**: Optocoupler off $\rightarrow$ Coil de-energizes $\rightarrow$ NO contact opens $\rightarrow$ Connected appliance turns **OFF**.

*Note: In ESPHome, this is handled via `inverted: true`. In Arduino code, `digitalWrite(RELAY_PIN, LOW)` is used to turn the device ON.*

### Relay Terminal Wiring
- **COM (Common)**: Connects to the incoming positive supply wire.
- **NO (Normally Open)**: Connects to the positive wire of the load (LED/Fan).
- **NC (Normally Closed)**: Leave unconnected.

---

## 5. Electrical Safety & Prototype Guidelines

> [!CAUTION]
> **Prototype Safety for College Labs**:
> Direct connection to 230V AC mains electricity presents severe electric shock, short-circuit, and fire hazards. For laboratory demonstrations, evaluation, and viva presentations:
> 1. Use **5V or 12V DC LEDs** to simulate living room and bedroom lights.
> 2. Use a **5V / 12V DC brushless fan** (e.g., 40mm PC cooling fan) to demonstrate temperature-triggered climate control.
> 3. Power the prototype via a regulated 5V USB wall adapter (2A minimum) or desktop USB port.
