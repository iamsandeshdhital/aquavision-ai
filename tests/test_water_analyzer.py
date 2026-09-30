"""Tests for Water Quality Analyzer Module"""
import unittest
import time
import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))
from core.water_analyzer import WaterQualityAnalyzer, WaterQualityReading

class TestWaterQualityAnalyzer(unittest.TestCase):
    def setUp(self):
        self.config = {
            "water_quality": {"color_ranges": {"clean": {"h": [80, 130], "s": [20, 100], "v": [100, 255]}}},
            "detection": {"min_contour_area": 500, "confidence_threshold": 0.6}
        }
        self.analyzer = WaterQualityAnalyzer(self.config)

    def test_initialization(self):
        self.assertIsNotNone(self.analyzer)

    def test_analyze_clean_water(self):
        frame = np.full((480, 640, 3), [100, 150, 80], dtype=np.uint8)
        reading = self.analyzer.analyze_frame(frame, "cam_1", "Test Location")
        self.assertIsInstance(reading, WaterQualityReading)
        self.assertEqual(reading.camera_id, "cam_1")

    def test_analyze_empty_frame(self):
        reading = self.analyzer.analyze_frame(None, "cam_1", "Test")
        self.assertEqual(reading.water_type, "unknown")

    def test_statistics(self):
        frame = np.full((480, 640, 3), [100, 150, 80], dtype=np.uint8)
        self.analyzer.analyze_frame(frame, "cam_1", "Test")
        stats = self.analyzer.get_statistics()
        self.assertEqual(stats["total_analyzed"], 1)

if __name__ == "__main__":
    unittest.main()
