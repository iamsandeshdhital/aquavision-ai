"""
Logging Module
Centralized logging for all AquaVision AI components.
"""

import os
import time
import json
import threading
from typing import Optional
from pathlib import Path
from enum import Enum


class LogLevel(Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AquaLogger:
    """Centralized logger for AquaVision AI."""

    def __init__(self, config: dict):
        self.config = config
        self._lock = threading.Lock()
        self._running = False

        # Log configuration
        self.log_dir = config.get("logging", {}).get("directory", "logs")
        self.log_level = config.get("logging", {}).get("level", "info")
        self.max_file_size_mb = config.get("logging", {}).get("max_file_size_mb", 10)
        self.max_files = config.get("logging", {}).get("max_files", 5)

        # Ensure log directory exists
        Path(self.log_dir).mkdir(parents=True, exist_ok=True)

        # Log file path
        self.log_file = os.path.join(self.log_dir, "aquavision.log")

        # In-memory log buffer
        self.log_buffer = []
        self.max_buffer_size = 1000

    def start(self):
        self._running = True
        self.info("Logger", "Logging system started")

    def stop(self):
        self._running = False
        self._flush_buffer()

    def debug(self, component: str, message: str):
        self._log(LogLevel.DEBUG, component, message)

    def info(self, component: str, message: str):
        self._log(LogLevel.INFO, component, message)

    def warning(self, component: str, message: str):
        self._log(LogLevel.WARNING, component, message)

    def error(self, component: str, message: str):
        self._log(LogLevel.ERROR, component, message)

    def critical(self, component: str, message: str):
        self._log(LogLevel.CRITICAL, component, message)

    def _log(self, level: LogLevel, component: str, message: str):
        """Internal logging method."""
        if not self._should_log(level):
            return

        log_entry = {
            "timestamp": time.time(),
            "level": level.value,
            "component": component,
            "message": message
        }

        with self._lock:
            self.log_buffer.append(log_entry)

            # Write to file if buffer is full
            if len(self.log_buffer) >= self.max_buffer_size:
                self._flush_buffer()

            # Also print to console for important messages
            if level in (LogLevel.WARNING, LogLevel.ERROR, LogLevel.CRITICAL):
                print(f"[{level.value.upper()}] [{component}] {message}")

    def _should_log(self, level: LogLevel) -> bool:
        """Check if a log level should be logged."""
        levels = {
            LogLevel.DEBUG: 0,
            LogLevel.INFO: 1,
            LogLevel.WARNING: 2,
            LogLevel.ERROR: 3,
            LogLevel.CRITICAL: 4
        }
        return levels.get(level, 0) >= levels.get(LogLevel(self.log_level), 1)

    def _flush_buffer(self):
        """Write buffered logs to file."""
        if not self.log_buffer:
            return

        try:
            with open(self.log_file, 'a') as f:
                for entry in self.log_buffer:
                    f.write(json.dumps(entry) + '\n')

            self.log_buffer.clear()

            # Rotate log file if too large
            self._rotate_if_needed()
        except Exception as e:
            print(f"[LOGGER ERROR] Failed to write logs: {e}")

    def _rotate_if_needed(self):
        """Rotate log file if it exceeds max size."""
        try:
            if os.path.exists(self.log_file):
                size_mb = os.path.getsize(self.log_file) / (1024 * 1024)
                if size_mb > self.max_file_size_mb:
                    # Rotate files
                    for i in range(self.max_files - 1, 0, -1):
                        old_file = f"{self.log_file}.{i}"
                        new_file = f"{self.log_file}.{i + 1}"
                        if os.path.exists(old_file):
                            os.rename(old_file, new_file)

                    # Move current file to .1
                    os.rename(self.log_file, f"{self.log_file}.1")
        except Exception as e:
            print(f"[LOGGER ERROR] Failed to rotate logs: {e}")

    def get_recent_logs(self, count: int = 100, level: Optional[LogLevel] = None) -> list:
        """Get recent log entries."""
        with self._lock:
            logs = self.log_buffer[-count:] if count < len(self.log_buffer) else self.log_buffer[:]

        if level:
            logs = [l for l in logs if l["level"] == level.value]

        return logs
