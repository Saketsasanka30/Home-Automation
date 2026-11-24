#!/usr/bin/env python3
"""
Home Automation Controller & Integration Bridge
Project: Home Automation System | Python, IoT & Home Assistant
Description:
    Demonstrates Python-based event processing, sensor data analytics,
    temperature hysteresis decision-making, and Home Assistant REST/WebSocket API interfacing.
"""

import os
import sys
import time
import json
import logging
from typing import Dict, Any, Optional
import urllib.request
import urllib.error

# Optional requests library
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("HAController")


class SensorDataProcessor:
    """Processes, filters, and validates incoming IoT sensor telemetry."""

    @staticmethod
    def validate_temperature(value: float) -> Optional[float]:
        """Validates that ambient room temperature is within realistic bounds (-10°C to 60°C)."""
        if -10.0 <= value <= 60.0:
            return round(value, 1)
        logger.warning(f"Rejecting anomalous temperature reading: {value}°C")
        return None

    @staticmethod
    def validate_humidity(value: float) -> Optional[float]:
        """Validates humidity is within physical range (0% to 100%)."""
        if 0.0 <= value <= 100.0:
            return round(value, 1)
        logger.warning(f"Rejecting anomalous humidity reading: {value}%")
        return None


class AutomationDecisionEngine:
    """
    Core rule evaluation engine.
    Encapsulates hysteresis logic, state checks, and control decisions.
    """

    def __init__(self, fan_on_threshold: float = 30.0, fan_off_threshold: float = 28.0, motion_timeout: int = 30):
        self.fan_on_threshold = fan_on_threshold
        self.fan_off_threshold = fan_off_threshold
        self.motion_timeout = motion_timeout
        self.last_motion_timestamp = 0.0

    def evaluate_fan_state(self, current_temp: float, current_fan_state: str, auto_mode: bool) -> Optional[str]:
        """
        Determines target fan state using hysteresis:
        - If Temp > 30.0°C and Fan is OFF -> return 'turn_on'
        - If Temp < 28.0°C and Fan is ON -> return 'turn_off'
        - In between 28°C and 30°C -> maintain current state (avoids chatter)
        """
        if not auto_mode:
            logger.debug("Automatic mode is OFF; fan decision engine bypassed.")
            return None

        if current_temp >= self.fan_on_threshold and current_fan_state.lower() != "on":
            return "turn_on"
        elif current_temp <= self.fan_off_threshold and current_fan_state.lower() != "off":
            return "turn_off"

        return None  # No state change required (hysteresis zone)

    def register_motion_event(self, motion_detected: bool):
        """Updates internal timestamp when motion is detected."""
        if motion_detected:
            self.last_motion_timestamp = time.time()

    def evaluate_motion_lighting(self, motion_detected: bool, current_light_state: str,
                                 auto_mode: bool, away_mode: bool, manual_override: bool) -> Optional[str]:
        """
        Evaluates motion lighting:
        - Motion detected + Auto ON + Away OFF + Override OFF -> 'turn_on'
        - No motion for >= timeout + Light ON -> 'turn_off'
        """
        if not auto_mode or away_mode or manual_override:
            return None

        now = time.time()
        if motion_detected and current_light_state.lower() != "on":
            self.last_motion_timestamp = now
            return "turn_on"

        if not motion_detected and current_light_state.lower() == "on":
            elapsed = now - self.last_motion_timestamp
            if elapsed >= self.motion_timeout:
                return "turn_off"

        return None


class HomeAssistantClient:
    """Handles communication with the Home Assistant REST API."""

    def __init__(self, base_url: str = "http://localhost:8123", token: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.token = token or os.getenv("HA_TOKEN", "")
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def _http_get(self, path: str) -> Optional[Dict[str, Any]]:
        """Makes an HTTP GET request using requests if available, or urllib otherwise."""
        url = f"{self.base_url}{path}"
        try:
            if HAS_REQUESTS:
                resp = requests.get(url, headers=self.headers, timeout=5)
                if resp.status_code == 200:
                    return resp.json()
                logger.warning(f"GET {url} failed: HTTP {resp.status_code}")
                return None
            else:
                req = urllib.request.Request(url, headers=self.headers, method="GET")
                with urllib.request.urlopen(req, timeout=5) as response:
                    if response.status == 200:
                        return json.loads(response.read().decode("utf-8"))
        except Exception as e:
            logger.warning(f"HTTP GET error for {url}: {e}")
        return None

    def _http_post(self, path: str, payload: Dict[str, Any]) -> bool:
        """Makes an HTTP POST request using requests if available, or urllib otherwise."""
        url = f"{self.base_url}{path}"
        try:
            if HAS_REQUESTS:
                resp = requests.post(url, headers=self.headers, json=payload, timeout=5)
                return resp.status_code == 200
            else:
                data = json.dumps(payload).encode("utf-8")
                req = urllib.request.Request(url, data=data, headers=self.headers, method="POST")
                with urllib.request.urlopen(req, timeout=5) as response:
                    return response.status in (200, 201)
        except Exception as e:
            logger.error(f"HTTP POST error for {url}: {e}")
            return False

    def check_connection(self) -> bool:
        """Verifies API connectivity to Home Assistant."""
        res = self._http_get("/api/")
        if res and "message" in res:
            logger.info(f"Connected to Home Assistant API: {res.get('message')}")
            return True
        logger.warning(f"Home Assistant not reachable at {self.base_url}")
        return False

    def get_entity_state(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Fetches the state object for a given entity."""
        return self._http_get(f"/api/states/{entity_id}")

    def call_service(self, domain: str, service: str, entity_id: str) -> bool:
        """Invokes a Home Assistant service (e.g. switch.turn_on)."""
        success = self._http_post(f"/api/services/{domain}/{service}", {"entity_id": entity_id})
        if success:
            logger.info(f"Service called successfully: {domain}.{service} -> {entity_id}")
        else:
            logger.error(f"Failed to call {domain}.{service} for {entity_id}")
        return success


class DeviceTracker:
    """Maintains an in-memory snapshot of all managed entities."""

    def __init__(self):
        self.devices = {
            "switch.living_room_light": "off",
            "switch.bedroom_light": "off",
            "switch.living_room_fan": "off",
            "binary_sensor.living_room_motion": "off",
            "sensor.room_temperature": 25.0,
            "sensor.room_humidity": 50.0,
            "input_boolean.automation_mode": "on",
            "input_boolean.night_mode": "off",
            "input_boolean.away_mode": "off",
            "input_boolean.manual_override": "off"
        }

    def update(self, entity_id: str, state: Any):
        self.devices[entity_id] = state
        logger.debug(f"[DeviceTracker] {entity_id} -> {state}")

    def get_summary(self) -> Dict[str, Any]:
        active_appliances = sum(
            1 for k, v in self.devices.items()
            if k.startswith("switch.") and str(v).lower() == "on"
        )
        return {
            "total_appliances": 3,
            "active_appliances": active_appliances,
            "temperature": self.devices.get("sensor.room_temperature"),
            "humidity": self.devices.get("sensor.room_humidity"),
            "motion": self.devices.get("binary_sensor.living_room_motion"),
            "mode": "Away" if self.devices.get("input_boolean.away_mode") == "on"
                    else "Night" if self.devices.get("input_boolean.night_mode") == "on"
                    else "Auto" if self.devices.get("input_boolean.automation_mode") == "on"
                    else "Manual"
        }


def run_standalone_demo():
    """Demonstrates Python backend execution without requiring a live HA instance."""
    print("=" * 65)
    print(" Home Automation Controller (Standalone Logic Verification)")
    print("=" * 65)

    tracker = DeviceTracker()
    engine = AutomationDecisionEngine(fan_on_threshold=30.0, fan_off_threshold=28.0, motion_timeout=3)
    processor = SensorDataProcessor()

    print("\n[Step 1] Initial State:")
    print(json.dumps(tracker.get_summary(), indent=2))

    # Scenario 1: Temperature Rises to 31.5°C
    print("\n[Step 2] Sensor Update: Temperature climbs to 31.5°C (Threshold > 30°C)")
    valid_temp = processor.validate_temperature(31.5)
    tracker.update("sensor.room_temperature", valid_temp)

    action = engine.evaluate_fan_state(
        current_temp=valid_temp,
        current_fan_state=tracker.devices["switch.living_room_fan"],
        auto_mode=(tracker.devices["input_boolean.automation_mode"] == "on")
    )
    print(f" -> Decision Engine Result: {action}")
    if action == "turn_on":
        tracker.update("switch.living_room_fan", "on")
        print(" -> Fan switched ON successfully.")

    # Scenario 2: Temperature drops to 29.0°C (In Hysteresis Zone 28-30°C)
    print("\n[Step 3] Sensor Update: Temperature cools to 29.0°C (Hysteresis Zone 28°C - 30°C)")
    valid_temp = processor.validate_temperature(29.0)
    tracker.update("sensor.room_temperature", valid_temp)

    action = engine.evaluate_fan_state(
        current_temp=valid_temp,
        current_fan_state=tracker.devices["switch.living_room_fan"],
        auto_mode=(tracker.devices["input_boolean.automation_mode"] == "on")
    )
    print(f" -> Decision Engine Result: {action} (Fan remains ON, prevents relay chatter)")

    # Scenario 3: Temperature drops to 27.5°C (Below 28°C Threshold)
    print("\n[Step 4] Sensor Update: Temperature cools to 27.5°C (Below 28°C)")
    valid_temp = processor.validate_temperature(27.5)
    tracker.update("sensor.room_temperature", valid_temp)

    action = engine.evaluate_fan_state(
        current_temp=valid_temp,
        current_fan_state=tracker.devices["switch.living_room_fan"],
        auto_mode=(tracker.devices["input_boolean.automation_mode"] == "on")
    )
    print(f" -> Decision Engine Result: {action}")
    if action == "turn_off":
        tracker.update("switch.living_room_fan", "off")
        print(" -> Fan switched OFF successfully.")

    # Scenario 4: Motion Detected
    print("\n[Step 5] Sensor Update: Motion detected in Living Room")
    tracker.update("binary_sensor.living_room_motion", "on")
    light_action = engine.evaluate_motion_lighting(
        motion_detected=True,
        current_light_state=tracker.devices["switch.living_room_light"],
        auto_mode=True,
        away_mode=False,
        manual_override=False
    )
    print(f" -> Decision Engine Result: {light_action}")
    if light_action == "turn_on":
        tracker.update("switch.living_room_light", "on")
        print(" -> Living Room Light switched ON.")

    # Scenario 5: Away Mode Activated
    print("\n[Step 6] User activates Away Mode:")
    tracker.update("input_boolean.away_mode", "on")
    tracker.update("switch.living_room_light", "off")
    tracker.update("switch.bedroom_light", "off")
    tracker.update("switch.living_room_fan", "off")
    print(" -> All appliances turned OFF.")
    print("\n[Final System Summary]:")
    print(json.dumps(tracker.get_summary(), indent=2))
    print("=" * 65)


if __name__ == "__main__":
    run_standalone_demo()
