"""Tests for Database Module"""
import unittest
import time
import sys
import os
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from core.database import Database
from core.water_analyzer import WaterQualityReading

class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.config = {"database": {"path": self.db_path}}
        self.db = Database(self.config)

    def tearDown(self):
        try:
            os.remove(self.db_path)
            os.rmdir(self.temp_dir)
        except OSError:
            pass

    def test_initialization(self):
        self.assertTrue(os.path.exists(self.db_path))

    def test_save_reading(self):
        reading = WaterQualityReading(
            timestamp=time.time(), camera_id="cam_1", location="Test",
            water_type="clean", confidence=0.9, turbidity_ntu=5.0,
            dissolved_oxygen_mg_l=8.0, ph_level=7.0, temperature_c=20.0,
            contamination_detected=False, contamination_type=None,
            severity="none", details="Test"
        )
        self.db.save_reading(reading)
        readings = self.db.get_recent_readings(hours=1)
        self.assertEqual(len(readings), 1)

    def test_get_alerts(self):
        self.db.save_alert(type('Alert', (), {
            'timestamp': time.time(), 'level': type('Level', (), {'value': 'high'})(),
            'title': 'Test', 'message': 'Test', 'camera_id': 'cam_1',
            'location': 'Test', 'acknowledged': False
        })())
        alerts = self.db.get_alerts(hours=1)
        self.assertEqual(len(alerts), 1)

    def test_statistics(self):
        stats = self.db.get_statistics()
        self.assertIn("total_readings", stats)
        self.assertIn("contaminated", stats)
        self.assertIn("total_alerts", stats)

if __name__ == "__main__":
    unittest.main()
