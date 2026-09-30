"""
Camera Feed Simulator Module
Simulates water quality camera feeds for testing and demonstration.
"""

import time
import threading
from typing import Dict, List, Optional
from dataclasses import dataclass, field

import numpy as np
import cv2


@dataclass
class SimulatedCamera:
    """Configuration for a simulated camera."""
    camera_id: str
    location: str
    scenario: str  # "clean", "algae", "sediment", "oil_spill", "chemical", "mixed"
    frame_width: int = 640
    frame_height: int = 480


class CameraSimulator:
    """Simulates water quality camera feeds."""

    def __init__(self, config: dict):
        self.config = config
        self.cameras: Dict[str, SimulatedCamera] = {}
        self._running = False
        self._lock = threading.Lock()

        # Initialize cameras from config
        camera_configs = config.get("cameras", [])
        for cam_config in camera_configs:
            camera = SimulatedCamera(
                camera_id=cam_config.get("name", "unknown"),
                location=cam_config.get("location", "unknown"),
                scenario="clean"
            )
            self.cameras[camera.camera_id] = camera

        # If no cameras configured, add defaults
        if not self.cameras:
            self.cameras["cam_1"] = SimulatedCamera("cam_1", "River Monitor 1", "clean")
            self.cameras["cam_2"] = SimulatedCamera("cam_2", "Reservoir Camera", "algae")
            self.cameras["cam_3"] = SimulatedCamera("cam_3", "Treatment Plant", "sediment")

    def start(self):
        """Start camera simulator."""
        self._running = True
        print(f"[Simulator] Started. {len(self.cameras)} cameras simulated")

    def stop(self):
        """Stop camera simulator."""
        self._running = False
        print("[Simulator] Stopped")

    def set_scenario(self, camera_id: str, scenario: str):
        """Set the simulation scenario for a camera."""
        if camera_id in self.cameras:
            self.cameras[camera_id].scenario = scenario

    def get_frame(self, camera_id: str) -> Optional[np.ndarray]:
        """Get a simulated frame from a camera."""
        if camera_id not in self.cameras:
            return None

        camera = self.cameras[camera_id]
        return self._generate_frame(camera)

    def _generate_frame(self, camera: SimulatedCamera) -> np.ndarray:
        """Generate a simulated water frame based on scenario."""
        width = camera.frame_width
        height = camera.frame_height

        if camera.scenario == "clean":
            return self._generate_clean_water(width, height)
        elif camera.scenario == "algae":
            return self._generate_algae_water(width, height)
        elif camera.scenario == "sediment":
            return self._generate_sediment_water(width, height)
        elif camera.scenario == "oil_spill":
            return self._generate_oil_spill(width, height)
        elif camera.scenario == "chemical":
            return self._generate_chemical_water(width, height)
        else:
            return self._generate_clean_water(width, height)

    def _generate_clean_water(self, width: int, height: int) -> np.ndarray:
        """Generate clean water frame."""
        # Blue-green water with natural variation
        frame = np.zeros((height, width, 3), dtype=np.uint8)

        # Base water color (blue-green)
        base_color = np.array([100, 150, 80])  # BGR

        # Add natural variation
        noise = np.random.normal(0, 10, (height, width, 3))
        frame = np.clip(base_color + noise, 0, 255).astype(np.uint8)

        # Add subtle wave patterns
        for i in range(0, height, 20):
            wave = np.sin(np.linspace(0, 4 * np.pi, width)) * 5
            frame[i:i+5, :, 0] = np.clip(frame[i:i+5, :, 0] + wave, 0, 255)
            frame[i:i+5, :, 1] = np.clip(frame[i:i+5, :, 1] + wave, 0, 255)

        return frame

    def _generate_algae_water(self, width: int, height: int) -> np.ndarray:
        """Generate algae bloom water frame."""
        frame = np.zeros((height, width, 3), dtype=np.uint8)

        # Green water (algae)
        base_color = np.array([50, 180, 50])  # BGR - green

        noise = np.random.normal(0, 15, (height, width, 3))
        frame = np.clip(base_color + noise, 0, 255).astype(np.uint8)

        # Add algae patches
        for _ in range(20):
            x = np.random.randint(0, width)
            y = np.random.randint(0, height)
            radius = np.random.randint(20, 80)
            color = (30, 150, 30)  # Darker green
            cv2.circle(frame, (x, y), radius, color, -1)

        return frame

    def _generate_sediment_water(self, width: int, height: int) -> np.ndarray:
        """Generate sediment-heavy water frame."""
        frame = np.zeros((height, width, 3), dtype=np.uint8)

        # Brownish water (sediment)
        base_color = np.array([80, 100, 120])  # BGR - brown

        noise = np.random.normal(0, 20, (height, width, 3))
        frame = np.clip(base_color + noise, 0, 255).astype(np.uint8)

        # Add sediment clouds
        for _ in range(10):
            x = np.random.randint(0, width)
            y = np.random.randint(0, height)
            radius = np.random.randint(50, 150)
            color = (60, 80, 100)  # Darker brown
            cv2.circle(frame, (x, y), radius, color, -1)

        return frame

    def _generate_oil_spill(self, width: int, height: int) -> np.ndarray:
        """Generate oil spill water frame."""
        frame = np.zeros((height, width, 3), dtype=np.uint8)

        # Dark water with oil sheen
        base_color = np.array([40, 40, 40])  # BGR - dark

        noise = np.random.normal(0, 5, (height, width, 3))
        frame = np.clip(base_color + noise, 0, 255).astype(np.uint8)

        # Add oil slick (rainbow sheen)
        for _ in range(5):
            x = np.random.randint(0, width)
            y = np.random.randint(0, height)
            w = np.random.randint(100, 300)
            h = np.random.randint(20, 60)
            color = (20, 20, 60)  # Dark with blue tint
            cv2.ellipse(frame, (x, y), (w, h), 0, 0, 360, color, -1)

        return frame

    def _generate_chemical_water(self, width: int, height: int) -> np.ndarray:
        """Generate chemical contamination water frame."""
        frame = np.zeros((height, width, 3), dtype=np.uint8)

        # Unnatural purple/pink water
        base_color = np.array([150, 50, 150])  # BGR - purple

        noise = np.random.normal(0, 15, (height, width, 3))
        frame = np.clip(base_color + noise, 0, 255).astype(np.uint8)

        # Add chemical streaks
        for _ in range(15):
            x1 = np.random.randint(0, width)
            y1 = np.random.randint(0, height)
            x2 = x1 + np.random.randint(-100, 100)
            y2 = y1 + np.random.randint(-50, 50)
            color = (120, 30, 120)  # Darker purple
            cv2.line(frame, (x1, y1), (x2, y2), color, 3)

        return frame

    def get_camera_list(self) -> List[dict]:
        """Get list of simulated cameras."""
        return [
            {
                "id": cam.camera_id,
                "location": cam.location,
                "scenario": cam.scenario
            }
            for cam in self.cameras.values()
        ]
