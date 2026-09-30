"""Tests for REST API Module"""
import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from core.api import AquaVisionAPI

class TestAquaVisionAPI(unittest.TestCase):
    def setUp(self):
        self.config = {"api": {"host": "0.0.0.0", "port": 8050}}
        self.api = AquaVisionAPI(None, self.config)

    def test_initialization(self):
        self.assertIsNotNone(self.api)

if __name__ == "__main__":
    unittest.main()
