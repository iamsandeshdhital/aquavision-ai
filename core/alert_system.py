"""
Alert System Module
Manages water quality alerts and notifications.
"""

import time
import threading
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class AlertLevel(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class WaterAlert:
    """Represents a water quality alert."""
    timestamp: float
    level: AlertLevel
    title: str
    message: str
    camera_id: str
    location: str
    acknowledged: bool = False


class AlertSystem:
    """Manages water quality alerts and notifications."""

    def __init__(self, config: dict):
        self.config = config
        self.alerts: List[WaterAlert] = []
        self._lock = threading.Lock()
        self._running = False
        self.recipients = config.get("alerts", {}).get("recipients", [])

    def start(self):
        self._running = True
        print("[AlertSystem] Started")

    def stop(self):
        self._running = False

    def create_alert(self, level: AlertLevel, title: str, message: str, camera_id: str, location: str) -> WaterAlert:
        alert = WaterAlert(
            timestamp=time.time(),
            level=level,
            title=title,
            message=message,
            camera_id=camera_id,
            location=location
        )
        with self._lock:
            self.alerts.append(alert)
        self._dispatch_notifications(alert)
        return alert

    def _dispatch_notifications(self, alert: WaterAlert):
        level_str = alert.level.value.upper()
        print(f"[ALERT:{level_str}] {alert.title} - {alert.location}")
        if alert.level in (AlertLevel.CRITICAL, AlertLevel.EMERGENCY):
            for recipient in self.recipients:
                print(f"[EMAIL] To: {recipient.get('email')} - {alert.title}")
                print(f"[SMS] To: {recipient.get('phone')} - {alert.title}")

    def get_active_alerts(self) -> List[WaterAlert]:
        with self._lock:
            return [a for a in self.alerts if not a.acknowledged]

    def acknowledge_alert(self, alert: WaterAlert):
        alert.acknowledged = True

    def get_alert_summary(self) -> dict:
        with self._lock:
            total = len(self.alerts)
            active = len(self.get_active_alerts())
            by_level = {}
            for alert in self.alerts:
                level = alert.level.value
                by_level[level] = by_level.get(level, 0) + 1
            return {"total_alerts": total, "active_alerts": active, "by_level": by_level}
