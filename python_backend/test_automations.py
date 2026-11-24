#!/usr/bin/env python3
"""
Unit and Integration Test Suite for Home Automation System
Project: Home Automation System | Python, IoT & Home Assistant
"""

import unittest
import time
import os
import sys

# Ensure current directory is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ha_controller import SensorDataProcessor, AutomationDecisionEngine, DeviceTracker


class TestSensorDataProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = SensorDataProcessor()

    def test_temperature_validation_valid(self):
        self.assertEqual(self.processor.validate_temperature(24.56), 24.6)
        self.assertEqual(self.processor.validate_temperature(0.0), 0.0)
        self.assertEqual(self.processor.validate_temperature(50.0), 50.0)

    def test_temperature_validation_out_of_bounds(self):
        self.assertIsNone(self.processor.validate_temperature(-25.0))
        self.assertIsNone(self.processor.validate_temperature(120.0))

    def test_humidity_validation(self):
        self.assertEqual(self.processor.validate_humidity(45.2), 45.2)
        self.assertIsNone(self.processor.validate_humidity(-5.0))
        self.assertIsNone(self.processor.validate_humidity(105.0))


class TestAutomationDecisionEngine(unittest.TestCase):
    def setUp(self):
        self.engine = AutomationDecisionEngine(fan_on_threshold=30.0, fan_off_threshold=28.0, motion_timeout=2)

    def test_automation_2_fan_hysteresis(self):
        # Temp rises above 30.0 -> Should turn ON
        decision = self.engine.evaluate_fan_state(current_temp=30.5, current_fan_state="off", auto_mode=True)
        self.assertEqual(decision, "turn_on")

        # Temp already above 30 and fan is ON -> No change needed
        decision = self.engine.evaluate_fan_state(current_temp=30.5, current_fan_state="on", auto_mode=True)
        self.assertIsNone(decision)

        # Temp cools into hysteresis band (e.g. 29.2°C) while fan is ON -> Must remain ON (no chatter)
        decision = self.engine.evaluate_fan_state(current_temp=29.2, current_fan_state="on", auto_mode=True)
        self.assertIsNone(decision)

        # Temp cools below 28.0 -> Should turn OFF
        decision = self.engine.evaluate_fan_state(current_temp=27.8, current_fan_state="on", auto_mode=True)
        self.assertEqual(decision, "turn_off")

        # If Auto mode is disabled, no decision is produced
        decision = self.engine.evaluate_fan_state(current_temp=35.0, current_fan_state="off", auto_mode=False)
        self.assertIsNone(decision)

    def test_automation_1_motion_lighting(self):
        # Motion detected with auto mode ON, away OFF, override OFF -> Turn ON
        decision = self.engine.evaluate_motion_lighting(
            motion_detected=True,
            current_light_state="off",
            auto_mode=True,
            away_mode=False,
            manual_override=False
        )
        self.assertEqual(decision, "turn_on")

        # Away mode active -> Motion should NOT turn light ON
        decision = self.engine.evaluate_motion_lighting(
            motion_detected=True,
            current_light_state="off",
            auto_mode=True,
            away_mode=True,
            manual_override=False
        )
        self.assertIsNone(decision)

        # Manual override active -> Motion should NOT turn light ON
        decision = self.engine.evaluate_motion_lighting(
            motion_detected=True,
            current_light_state="off",
            auto_mode=True,
            away_mode=False,
            manual_override=True
        )
        self.assertIsNone(decision)

    def test_automation_1b_motion_timeout(self):
        # Register motion now
        self.engine.register_motion_event(True)

        # Immediate check with no motion -> Should not turn off yet
        decision = self.engine.evaluate_motion_lighting(
            motion_detected=False,
            current_light_state="on",
            auto_mode=True,
            away_mode=False,
            manual_override=False
        )
        self.assertIsNone(decision)

        # Sleep longer than the 2-second test timeout
        time.sleep(2.1)

        # Now check again -> Should signal 'turn_off'
        decision = self.engine.evaluate_motion_lighting(
            motion_detected=False,
            current_light_state="on",
            auto_mode=True,
            away_mode=False,
            manual_override=False
        )
        self.assertEqual(decision, "turn_off")


class TestDeviceTracker(unittest.TestCase):
    def test_device_tracker_summary(self):
        tracker = DeviceTracker()
        tracker.update("switch.living_room_light", "on")
        tracker.update("switch.bedroom_light", "on")
        tracker.update("switch.living_room_fan", "off")

        summary = tracker.get_summary()
        self.assertEqual(summary["total_appliances"], 3)
        self.assertEqual(summary["active_appliances"], 2)
        self.assertEqual(summary["mode"], "Auto")


if __name__ == "__main__":
    unittest.main()
