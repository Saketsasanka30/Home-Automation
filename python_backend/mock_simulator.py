#!/usr/bin/env python3
"""
Interactive IoT & Home Assistant Hardware Simulator
Project: Home Automation System | Python, IoT & Home Assistant
Description:
    Simulates ESP32 sensors (DHT11, PIR) and relays with an interactive CLI
    dashboard. Allows college students and examiners to test all 5 automation
    scenarios interactively without needing physical hardware connected.
"""

import os
import sys
import time

# Ensure current directory is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ha_controller import SensorDataProcessor, AutomationDecisionEngine, DeviceTracker

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    CYAN = Fore.CYAN
    GREEN = Fore.GREEN
    YELLOW = Fore.YELLOW
    RED = Fore.RED
    RESET = Style.RESET_ALL
    BOLD = Style.BRIGHT
except ImportError:
    CYAN = GREEN = YELLOW = RED = RESET = BOLD = ""


class IoTSimulator:
    def __init__(self):
        self.tracker = DeviceTracker()
        self.engine = AutomationDecisionEngine(fan_on_threshold=30.0, fan_off_threshold=28.0, motion_timeout=10)
        self.processor = SensorDataProcessor()

    def print_dashboard(self):
        summary = self.tracker.get_summary()
        temp = summary["temperature"]
        humid = summary["humidity"]
        motion = summary["motion"]
        mode = summary["mode"]
        active = summary["active_appliances"]

        lr_light = self.tracker.devices["switch.living_room_light"].upper()
        br_light = self.tracker.devices["switch.bedroom_light"].upper()
        fan = self.tracker.devices["switch.living_room_fan"].upper()

        lr_color = GREEN if lr_light == "ON" else RED
        br_color = GREEN if br_light == "ON" else RED
        fan_color = GREEN if fan == "ON" else RED
        mot_color = GREEN if motion == "on" else YELLOW

        print("\n" + "=" * 60)
        print(f"{BOLD}{CYAN}      SMART HOME DASHBOARD (SIMULATOR MODE){RESET}")
        print("=" * 60)
        print(f" System Status: {BOLD}{mode.upper()}{RESET} | Active Devices: {active}/3")
        print("-" * 60)
        print(f"  🌡️  Room Temp: {temp:.1f} °C   |  💧 Humidity: {humid:.0f} %")
        print(f"  🚶 Motion: {mot_color}{motion.upper()}{RESET}      |  🌐 Node: Connected")
        print("-" * 60)
        print(" Appliances Status:")
        print(f"  [1] Living Room Light (Relay 1): {lr_color}{lr_light}{RESET}")
        print(f"  [2] Bedroom Light (GPIO 21):     {br_color}{br_light}{RESET}")
        print(f"  [3] Smart Fan (Relay 2):         {fan_color}{fan}{RESET}")
        print("-" * 60)
        print(" Modes:")
        print(f"  Auto Mode: {self.tracker.devices['input_boolean.automation_mode'].upper()} | "
              f"Night Mode: {self.tracker.devices['input_boolean.night_mode'].upper()} | "
              f"Away Mode: {self.tracker.devices['input_boolean.away_mode'].upper()}")
        print("=" * 60)

    def trigger_motion(self, detected: bool):
        state = "on" if detected else "off"
        self.tracker.update("binary_sensor.living_room_motion", state)
        print(f"\n[EVENT] PIR Motion changed to: {state.upper()}")

        # Check automation rule 1
        action = self.engine.evaluate_motion_lighting(
            motion_detected=detected,
            current_light_state=self.tracker.devices["switch.living_room_light"],
            auto_mode=(self.tracker.devices["input_boolean.automation_mode"] == "on"),
            away_mode=(self.tracker.devices["input_boolean.away_mode"] == "on"),
            manual_override=(self.tracker.devices["input_boolean.manual_override"] == "on")
        )
        if action == "turn_on":
            self.tracker.update("switch.living_room_light", "on")
            print(f"{GREEN}[AUTOMATION 1A] Motion detected! Living Room Light turned ON.{RESET}")
        elif action == "turn_off":
            self.tracker.update("switch.living_room_light", "off")
            print(f"{YELLOW}[AUTOMATION 1B] Motion timeout expired. Living Room Light turned OFF.{RESET}")

    def update_temperature(self, temp: float):
        valid = self.processor.validate_temperature(temp)
        if valid is not None:
            self.tracker.update("sensor.room_temperature", valid)
            print(f"\n[EVENT] Temperature changed to: {valid}°C")

            # Check automation rule 2
            action = self.engine.evaluate_fan_state(
                current_temp=valid,
                current_fan_state=self.tracker.devices["switch.living_room_fan"],
                auto_mode=(self.tracker.devices["input_boolean.automation_mode"] == "on")
            )
            if action == "turn_on":
                self.tracker.update("switch.living_room_fan", "on")
                print(f"{GREEN}[AUTOMATION 2A] Temp >= 30°C! Smart Fan switched ON.{RESET}")
            elif action == "turn_off":
                self.tracker.update("switch.living_room_fan", "off")
                print(f"{YELLOW}[AUTOMATION 2B] Temp <= 28°C! Smart Fan switched OFF (Hysteresis cleared).{RESET}")
            else:
                print(f"[AUTOMATION 2] Temperature inside band or no change required. Fan state unchanged.")

    def toggle_away_mode(self):
        curr = self.tracker.devices["input_boolean.away_mode"]
        new_state = "off" if curr == "on" else "on"
        self.tracker.update("input_boolean.away_mode", new_state)
        print(f"\n[EVENT] Away Mode set to: {new_state.upper()}")

        if new_state == "on":
            self.tracker.update("switch.living_room_light", "off")
            self.tracker.update("switch.bedroom_light", "off")
            self.tracker.update("switch.living_room_fan", "off")
            print(f"{RED}[AUTOMATION 4] Away Mode activated! All appliances powered OFF.{RESET}")

    def toggle_night_mode(self):
        curr = self.tracker.devices["input_boolean.night_mode"]
        new_state = "off" if curr == "on" else "on"
        self.tracker.update("input_boolean.night_mode", new_state)
        print(f"\n[EVENT] Night Mode set to: {new_state.upper()}")

        if new_state == "on":
            self.tracker.update("switch.bedroom_light", "off")
            print(f"{CYAN}[AUTOMATION 3] Night Mode engaged. Bedroom light powered off.{RESET}")

    def manual_toggle(self, device_key: str):
        curr = self.tracker.devices[device_key]
        new_state = "off" if curr == "on" else "on"
        self.tracker.update(device_key, new_state)
        self.tracker.update("input_boolean.manual_override", "on")
        print(f"\n[MANUAL] User manually toggled {device_key} -> {new_state.upper()}")
        print(f"{YELLOW}[AUTOMATION 5] Manual override activated to prevent conflict.{RESET}")


def interactive_menu():
    sim = IoTSimulator()
    while True:
        sim.print_dashboard()
        print("\nSelect an action to simulate:")
        print("  1. Trigger Motion Detected (PIR = ON)")
        print("  2. Trigger Motion Cleared (PIR = OFF)")
        print("  3. Set High Temperature (31.5°C -> Fan should turn ON)")
        print("  4. Set Medium Temperature (29.0°C -> Fan should STAY ON / Hysteresis)")
        print("  5. Set Low Temperature (27.0°C -> Fan should turn OFF)")
        print("  6. Toggle Away Mode (Shuts everything OFF)")
        print("  7. Toggle Night Mode")
        print("  8. Manually toggle Living Room Light")
        print("  9. Manually toggle Fan")
        print(" 10. Reset System to Auto Standby")
        print("  0. Exit Simulator")

        try:
            choice = input(f"{BOLD}Enter choice [0-10]: {RESET}").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting simulator.")
            break

        if choice == "1":
            sim.trigger_motion(True)
        elif choice == "2":
            sim.trigger_motion(False)
        elif choice == "3":
            sim.update_temperature(31.5)
        elif choice == "4":
            sim.update_temperature(29.0)
        elif choice == "5":
            sim.update_temperature(27.0)
        elif choice == "6":
            sim.toggle_away_mode()
        elif choice == "7":
            sim.toggle_night_mode()
        elif choice == "8":
            sim.manual_toggle("switch.living_room_light")
        elif choice == "9":
            sim.manual_toggle("switch.living_room_fan")
        elif choice == "10":
            sim.tracker.update("input_boolean.automation_mode", "on")
            sim.tracker.update("input_boolean.away_mode", "off")
            sim.tracker.update("input_boolean.night_mode", "off")
            sim.tracker.update("input_boolean.manual_override", "off")
            sim.tracker.update("binary_sensor.living_room_motion", "off")
            print("\n[SYSTEM] System reset to default Auto Mode.")
        elif choice == "0":
            print("\nExiting simulator.")
            break
        else:
            print("Invalid choice, please try again.")
        time.sleep(1)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        # Quick non-interactive batch demonstration
        sim = IoTSimulator()
        sim.print_dashboard()
        sim.trigger_motion(True)
        sim.update_temperature(32.0)
        sim.update_temperature(29.0)
        sim.update_temperature(26.5)
        sim.toggle_away_mode()
        sim.print_dashboard()
    else:
        interactive_menu()
