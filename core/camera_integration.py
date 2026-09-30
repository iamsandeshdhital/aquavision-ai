"""
Real Camera Integration Module
Supports RTSP, HTTP, and USB camera feeds.
"""

import time
import threading
from typing import Dict, Optional, Callable
from dataclasses import dataclass, field

import numpy as np

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False


@dataclass
class CameraConnection:
    """Represents a camera connection."""
    camera_id: str
    name: str
    location: str
    url: str
    camera_type: str  # "rtsp", "http", "usb"
    status: str  # "connected", "disconnected", "error"
    last_frame: Optional[np.ndarray] = None
    last_frame_time: float = 0
    error_count: int = 0
    total_frames: int = 0


class CameraIntegration:
    """Manages real camera connections."""

    def __init__(self, config: dict):
        self.config = config
        self._lock = threading.Lock()
        self._running = False

        # Camera connections
        self.cameras: Dict[str, CameraConnection] = {}
        self._capture_threads: Dict[str, threading.Thread] = {}

        # Frame callbacks
        self._frame_callbacks: list = []

        # Initialize cameras from config
        self._init_cameras()

    def _init_cameras(self):
        """Initialize cameras from config."""
        camera_configs = self.config.get("cameras", [])
        for cam_config in camera_configs:
            camera = CameraConnection(
                camera_id=cam_config.get("name", "unknown"),
                name=cam_config.get("name", "unknown"),
                location=cam_config.get("location", "unknown"),
                url=cam_config.get("url", ""),
                camera_type=cam_config.get("type", "rtsp"),
                status="disconnected"
            )
            self.cameras[camera.camera_id] = camera

    def start(self):
        """Start camera integration."""
        self._running = True
        print(f"[CameraIntegration] Started. {len(self.cameras)} cameras configured")

        # Start capture threads for each camera
        for camera_id in self.cameras:
            self._start_capture(camera_id)

    def stop(self):
        """Stop camera integration."""
        self._running = False
        for camera_id in self._capture_threads:
            self._capture_threads[camera_id].join(timeout=5)
        print("[CameraIntegration] Stopped")

    def _start_capture(self, camera_id: str):
        """Start capture thread for a camera."""
        if not HAS_CV2:
            print(f"[CameraIntegration] OpenCV not available, cannot capture from {camera_id}")
            return

        thread = threading.Thread(target=self._capture_loop, args=(camera_id,), daemon=True)
        self._capture_threads[camera_id] = thread
        thread.start()

    def _capture_loop(self, camera_id: str):
        """Capture loop for a single camera."""
        camera = self.cameras[camera_id]

        while self._running:
            try:
                if camera.camera_type == "usb":
                    cap = cv2.VideoCapture(0)
                else:
                    cap = cv2.VideoCapture(camera.url)

                if not cap.isOpened():
                    camera.status = "error"
                    camera.error_count += 1
                    time.sleep(5)
                    continue

                camera.status = "connected"

                while self._running:
                    ret, frame = cap.read()
                    if ret:
                        camera.last_frame = frame
                        camera.last_frame_time = time.time()
                        camera.total_frames += 1

                        # Notify callbacks
                        for callback in self._frame_callbacks:
                            callback(camera_id, frame)
                    else:
                        camera.error_count += 1
                        break

                cap.release()

            except Exception as e:
                camera.status = "error"
                camera.error_count += 1
                print(f"[CameraIntegration] Error capturing from {camera_id}: {e}")
                time.sleep(5)

    def get_frame(self, camera_id: str) -> Optional[np.ndarray]:
        """Get the latest frame from a camera."""
        if camera_id in self.cameras:
            return self.cameras[camera_id].last_frame
        return None

    def register_frame_callback(self, callback: Callable):
        """Register a callback for new frames."""
        self._frame_callbacks.append(callback)

    def get_camera_status(self, camera_id: str) -> Optional[dict]:
        """Get status of a camera."""
        if camera_id not in self.cameras:
            return None

        camera = self.cameras[camera_id]
        return {
            "camera_id": camera.camera_id,
            "name": camera.name,
            "location": camera.location,
            "status": camera.status,
            "total_frames": camera.total_frames,
            "error_count": camera.error_count,
            "last_frame_time": camera.last_frame_time
        }

    def get_all_statuses(self) -> list:
        """Get status of all cameras."""
        return [self.get_camera_status(cid) for cid in self.cameras]
