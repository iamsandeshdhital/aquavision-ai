"""
Dashboard Module
Real-time water quality monitoring dashboard.
"""

import time
import threading
from typing import Dict, List, Optional
from collections import deque

import numpy as np


class Dashboard:
    """Real-time water quality dashboard."""

    def __init__(self, config: dict):
        self.config = config
        self.refresh_rate = config.get("dashboard", {}).get("refresh_rate_seconds", 5)
        self.readings_history: deque = deque(maxlen=1000)
        self.alerts: List[dict] = []
        self._lock = threading.Lock()
        self._running = False

    def start(self):
        self._running = True
        print("[Dashboard] Started")

    def stop(self):
        self._running = False

    def update_reading(self, reading):
        with self._lock:
            self.readings_history.append(reading)

    def add_alert(self, alert: dict):
        with self._lock:
            self.alerts.append(alert)

    def get_current_status(self) -> dict:
        with self._lock:
            if not self.readings_history:
                return {"status": "initializing"}
            latest = self.readings_history[-1]
            return {
                "water_type": latest.water_type,
                "severity": latest.severity,
                "turbidity": latest.turbidity_ntu,
                "dissolved_oxygen": latest.dissolved_oxygen_mg_l,
                "ph": latest.ph_level,
                "contamination": latest.contamination_detected,
                "timestamp": latest.timestamp
            }

    def display_console(self):
        status = self.get_current_status()
        print("\n" + "=" * 60)
        print("  AquaVision AI - Water Quality Dashboard")
        print("=" * 60)
        if status.get("status") == "initializing":
            print("  Status: Initializing...")
            return
        print(f"  Water Type: {status['water_type']}")
        print(f"  Severity:   {status['severity'].upper()}")
        print(f"  Turbidity:  {status['turbidity']:.1f} NTU")
        print(f"  Dissolved O2: {status['dissolved_oxygen']:.1f} mg/L")
        print(f"  pH:         {status['ph']:.1f}")
        print(f"  Contamination: {'YES' if status['contamination'] else 'NO'}")
        print("=" * 60 + "\n")
