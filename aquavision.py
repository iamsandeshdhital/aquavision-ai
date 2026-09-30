"""
AquaVision AI - Real-Time Water Quality Monitoring System
==========================================================
Uses computer vision to detect water pollution, algae blooms, oil spills,
and chemical contamination in real-time from camera feeds.

Usage:
    python aquavision.py              # Start with simulation
    python aquavision.py --demo       # Run demo with all scenarios
"""

import os
import sys
import time
import signal
import argparse
import threading
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent))

from core.water_analyzer import WaterQualityAnalyzer
from core.alert_system import AlertSystem, AlertLevel
from core.dashboard import Dashboard
from core.simulator import CameraSimulator


class AquaVision:
    """Main AquaVision AI application."""

    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        self.running = False
        self._shutdown_event = threading.Event()

        print("=" * 60)
        print("  AquaVision AI v1.0")
        print("  Real-Time Water Quality Monitoring System")
        print("=" * 60)

        self.water_analyzer = WaterQualityAnalyzer(self.config)
        self.alert_system = AlertSystem(self.config)
        self.dashboard = Dashboard(self.config)
        self.simulator = CameraSimulator(self.config)

        self.scan_count = 0
        self.alerts_triggered = 0
        self.start_time = None

    def _load_config(self, config_path: str) -> dict:
        if not os.path.exists(config_path):
            print(f"[AquaVision] Config not found: {config_path}, using defaults")
            return self._default_config()
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            print(f"[AquaVision] Loaded configuration from {config_path}")
            return config
        except Exception as e:
            print(f"[AquaVision] Error loading config: {e}, using defaults")
            return self._default_config()

    def _default_config(self) -> dict:
        return {
            "water_quality": {"color_ranges": {}},
            "detection": {"min_contour_area": 500, "confidence_threshold": 0.6},
            "cameras": [],
            "alerts": {"enabled": True, "recipients": []},
            "dashboard": {"refresh_rate_seconds": 5},
            "database": {"path": "data/aquavision.db"}
        }

    def start(self, demo_mode: bool = False):
        self.running = True
        self.start_time = time.time()

        self.water_analyzer.start()
        self.alert_system.start()
        self.dashboard.start()
        self.simulator.start()

        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        print("\n[AquaVision] All modules started. Monitoring active.")
        print("[AquaVision] Press Ctrl+C to stop.\n")

        if demo_mode:
            print("[AquaVision] DEMO MODE: Cycling through all scenarios\n")
            threading.Timer(10, self._cycle_scenarios).start()

        interval = self.config.get("dashboard", {}).get("refresh_rate_seconds", 5)

        try:
            while self.running and not self._shutdown_event.is_set():
                self._scan_cycle()
                self._shutdown_event.wait(interval)
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()

    def _scan_cycle(self):
        self.scan_count += 1

        for camera_id, camera in self.simulator.cameras.items():
            frame = self.simulator.get_frame(camera_id)
            if frame is None:
                continue

            reading = self.water_analyzer.analyze_frame(
                frame, camera_id, camera.location
            )
            self.dashboard.update_reading(reading)

            if reading.contamination_detected:
                self._check_alerts(reading)

        if self.scan_count % 6 == 0:
            self.dashboard.display_console()

    def _check_alerts(self, reading):
        if reading.severity == "critical":
            self._create_alert(AlertLevel.EMERGENCY, "CRITICAL WATER CONTAMINATION",
                f"{reading.contamination_type} detected at {reading.location}",
                reading.camera_id, reading.location)
        elif reading.severity == "high":
            self._create_alert(AlertLevel.CRITICAL, "HIGH Water Quality Alert",
                f"{reading.contamination_type} detected at {reading.location}",
                reading.camera_id, reading.location)
        elif reading.severity == "medium":
            self._create_alert(AlertLevel.WARNING, "Water Quality Warning",
                f"{reading.contamination_type} detected at {reading.location}",
                reading.camera_id, reading.location)

    def _create_alert(self, level, title, message, camera_id, location):
        alert = self.alert_system.create_alert(level, title, message, camera_id, location)
        self.alerts_triggered += 1

    def _cycle_scenarios(self):
        scenarios = ["clean", "algae", "sediment", "oil_spill", "chemical"]
        cameras = list(self.simulator.cameras.keys())
        for i, scenario in enumerate(scenarios):
            if i < len(cameras):
                self.simulator.set_scenario(cameras[i], scenario)
        if self.running:
            threading.Timer(30, self._cycle_scenarios).start()

    def _signal_handler(self, signum, frame):
        print("\n[AquaVision] Shutdown signal received...")
        self.running = False
        self._shutdown_event.set()

    def stop(self):
        print("\n[AquaVision] Stopping all modules...")
        self.water_analyzer.stop()
        self.alert_system.stop()
        self.dashboard.stop()
        self.simulator.stop()

        uptime = time.time() - self.start_time if self.start_time else 0
        stats = self.water_analyzer.get_statistics()
        print("\n" + "=" * 60)
        print("  AquaVision AI - Session Summary")
        print("=" * 60)
        print(f"  Uptime:            {uptime:.0f} seconds")
        print(f"  Scans completed:   {self.scan_count}")
        print(f"  Frames analyzed:   {stats['total_analyzed']}")
        print(f"  Contamination:     {stats['contamination_detected']} events")
        print(f"  Alerts triggered:  {self.alerts_triggered}")
        print("=" * 60)
        print("[AquaVision] Stay safe!")


def main():
    parser = argparse.ArgumentParser(description="AquaVision AI - Water Quality Monitoring")
    parser.add_argument("--config", "-c", default="config.yaml", help="Path to configuration file")
    parser.add_argument("--demo", "-d", action="store_true", help="Run in demo mode")
    args = parser.parse_args()

    app = AquaVision(config_path=args.config)
    if args.demo:
        app.start(demo_mode=True)
    else:
        app.start()


if __name__ == "__main__":
    main()
