"""Tests for Camera Integration Module"""
import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from core.camera_integration import CameraIntegration

class TestCameraIntegration(unittest.TestCase):
    def setUp(self):
        self.config = {"cameras": [{"name": "cam_1", "location": "Test", "type": "rtsp", "url": "test"}]}
        self.integration = CameraIntegration(self.config)

    def test_initialization(self):
        self.assertIsNotNone(self.integration)

    def test_get_camera_status(self):
        status = self.integration.get_camera_status("cam_1")
        self.assertIsNotNone(status)
        self.assertEqual(status["camera_id"], "cam_1")

    def test_get_all_statuses(self):
        statuses = self.integration.get_all_statuses()
        self.assertIsInstance(statuses, list)
        self.assertGreater(len(statuses), 0)

    def test_get_frame(self):
        frame = self.integration.get_frame("cam_1")
        self.assertIsNone(frame)

if __name__ == "__main__":
    unittest.main()
