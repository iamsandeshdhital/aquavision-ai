"""Tests for Alert System Module"""
import unittest
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from core.alert_system import AlertSystem, AlertLevel

class TestAlertSystem(unittest.TestCase):
    def setUp(self):
        self.config = {"alerts": {"enabled": True, "recipients": [{"name": "Test", "email": "test@test.com"}]}}
        self.system = AlertSystem(self.config)

    def test_initialization(self):
        self.assertIsNotNone(self.system)

    def test_create_alert(self):
        alert = self.system.create_alert(AlertLevel.HIGH, "Test Alert", "Test message", "cam_1", "Test")
        self.assertIsNotNone(alert)
        self.assertEqual(alert.level, AlertLevel.HIGH)

    def test_get_active_alerts(self):
        self.system.create_alert(AlertLevel.WARNING, "Test", "Msg", "cam_1", "Test")
        active = self.system.get_active_alerts()
        self.assertEqual(len(active), 1)

    def test_acknowledge_alert(self):
        alert = self.system.create_alert(AlertLevel.WARNING, "Test", "Msg", "cam_1", "Test")
        self.system.acknowledge_alert(alert)
        self.assertTrue(alert.acknowledged)

if __name__ == "__main__":
    unittest.main()
