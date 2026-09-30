"""Tests for Camera Simulator Module"""
import unittest
import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))
from core.simulator import CameraSimulator

class TestCameraSimulator(unittest.TestCase):
    def setUp(self):
        self.config = {"cameras": [{"name": "cam_1", "location": "Test", "type": "rtsp", "url": "test"}]}
        self.simulator = CameraSimulator(self.config)

    def test_initialization(self):
        self.assertIsNotNone(self.simulator)
        self.assertGreater(len(self.simulator.cameras), 0)

    def test_get_frame(self):
        frame = self.simulator.get_frame("cam_1")
        self.assertIsNotNone(frame)
        self.assertEqual(frame.shape, (480, 640, 3))

    def test_set_scenario(self):
        self.simulator.set_scenario("cam_1", "algae")
        self.assertEqual(self.simulator.cameras["cam_1"].scenario, "algae")

    def test_camera_list(self):
        cameras = self.simulator.get_camera_list()
        self.assertIsInstance(cameras, list)
        self.assertGreater(len(cameras), 0)

if __name__ == "__main__":
    unittest.main()
