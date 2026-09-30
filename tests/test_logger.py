"""Tests for Logging Module"""
import unittest
import time
import sys
import os
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from core.logger import AquaLogger, LogLevel

class TestAquaLogger(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.config = {"logging": {"directory": self.temp_dir, "level": "debug"}}
        self.logger = AquaLogger(self.config)

    def tearDown(self):
        try:
            import shutil
            shutil.rmtree(self.temp_dir)
        except OSError:
            pass

    def test_initialization(self):
        self.assertIsNotNone(self.logger)

    def test_log_levels(self):
        self.logger.debug("Test", "Debug message")
        self.logger.info("Test", "Info message")
        self.logger.warning("Test", "Warning message")
        self.logger.error("Test", "Error message")

    def test_get_recent_logs(self):
        self.logger.info("Test", "Test message")
        logs = self.logger.get_recent_logs(count=10)
        self.assertIsInstance(logs, list)

if __name__ == "__main__":
    unittest.main()
