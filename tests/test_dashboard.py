"""Tests for Dashboard Module"""
import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from core.dashboard import Dashboard

class TestDashboard(unittest.TestCase):
    def setUp(self):
        self.config = {"dashboard": {"refresh_rate_seconds": 5}}
        self.dashboard = Dashboard(self.config)

    def test_initialization(self):
        self.assertIsNotNone(self.dashboard)

    def test_get_current_status_initial(self):
        status = self.dashboard.get_current_status()
        self.assertEqual(status.get("status"), "initializing")

if __name__ == "__main__":
    unittest.main()
