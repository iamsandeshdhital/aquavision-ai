"""
Water Quality Analyzer Module
Uses computer vision to detect water pollution, algae blooms, oil spills, and sediment.
"""

import time
import threading
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import deque

import numpy as np
import cv2


@dataclass
class WaterQualityReading:
    """Represents a water quality analysis result."""
    timestamp: float
    camera_id: str
    location: str
    water_type: str  # "clean", "algae", "sediment", "oil_spill", "chemical"
    confidence: float
    turbidity_ntu: float
    dissolved_oxygen_mg_l: float
    ph_level: float
    temperature_c: float
    contamination_detected: bool
    contamination_type: Optional[str]
    severity: str  # "none", "low", "medium", "high", "critical"
    details: str


@dataclass
class ContaminationEvent:
    """Represents a detected contamination event."""
    timestamp: float
    camera_id: str
    location: str
    contamination_type: str
    severity: str
    confidence: float
    area_pixels: int
    recommended_action: str


class WaterQualityAnalyzer:
    """Analyzes water quality from camera feeds using computer vision."""

    def __init__(self, config: dict):
        self.config = config
        self._lock = threading.Lock()
        self._running = False

        # Color ranges for different water types (HSV)
        self.color_ranges = config.get("water_quality", {}).get("color_ranges", {})

        # Detection thresholds
        self.min_contour_area = config.get("detection", {}).get("min_contour_area", 500)
        self.confidence_threshold = config.get("detection", {}).get("confidence_threshold", 0.6)

        # Historical data
        self.readings_history: deque = deque(maxlen=10000)
        self.contamination_events: List[ContaminationEvent] = []

        # Statistics
        self.total_analyzed = 0
        self.contamination_detected = 0

    def start(self):
        """Start water quality analyzer."""
        self._running = True
        print("[WaterAnalyzer] Started. Monitoring water quality from camera feeds")

    def stop(self):
        """Stop water quality analyzer."""
        self._running = False
        print("[WaterAnalyzer] Stopped")

    def analyze_frame(self, frame: np.ndarray, camera_id: str = "unknown", location: str = "unknown") -> WaterQualityReading:
        """
        Analyze a single frame for water quality.
        Returns WaterQualityReading with analysis results.
        """
        if frame is None or frame.size == 0:
            return self._create_empty_reading(camera_id, location)

        # Convert to HSV for color analysis
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Analyze color distribution
        color_analysis = self._analyze_color_distribution(hsv)

        # Detect contamination
        contamination = self._detect_contamination(hsv, frame)

        # Estimate turbidity from image clarity
        turbidity = self._estimate_turbidity(frame)

        # Estimate dissolved oxygen (proxy from color and turbidity)
        dissolved_oxygen = self._estimate_dissolved_oxygen(color_analysis, turbidity)

        # Estimate pH (proxy from color)
        ph_level = self._estimate_ph(color_analysis)

        # Determine water type and severity
        water_type = self._classify_water_type(color_analysis, contamination)
        severity = self._determine_severity(turbidity, dissolved_oxygen, ph_level, contamination)

        # Create reading
        reading = WaterQualityReading(
            timestamp=time.time(),
            camera_id=camera_id,
            location=location,
            water_type=water_type,
            confidence=color_analysis.get("confidence", 0.0),
            turbidity_ntu=turbidity,
            dissolved_oxygen_mg_l=dissolved_oxygen,
            ph_level=ph_level,
            temperature_c=20.0,  # Placeholder - would need thermal camera
            contamination_detected=contamination is not None,
            contamination_type=contamination.get("type") if contamination else None,
            severity=severity,
            details=self._generate_details(color_analysis, contamination, turbidity)
        )

        with self._lock:
            self.readings_history.append(reading)
            self.total_analyzed += 1
            if contamination:
                self.contamination_detected += 1
                self._record_contamination_event(reading, contamination)

        return reading

    def _analyze_color_distribution(self, hsv: np.ndarray) -> dict:
        """Analyze the color distribution of the water."""
        total_pixels = hsv.shape[0] * hsv.shape[1]
        color_counts = {}

        for water_type, ranges in self.color_ranges.items():
            h_range = ranges.get("h", [0, 180])
            s_range = ranges.get("s", [0, 255])
            v_range = ranges.get("v", [0, 255])

            lower = np.array([h_range[0], s_range[0], v_range[0]])
            upper = np.array([h_range[1], s_range[1], v_range[1]])

            mask = cv2.inRange(hsv, lower, upper)
            count = cv2.countNonZero(mask)
            color_counts[water_type] = count / total_pixels

        # Determine dominant color
        dominant = max(color_counts, key=color_counts.get)
        confidence = color_counts[dominant]

        return {
            "dominant": dominant,
            "confidence": confidence,
            "distribution": color_counts
        }

    def _detect_contamination(self, hsv: np.ndarray, frame: np.ndarray) -> Optional[dict]:
        """Detect contamination in the water using contour analysis."""
        # Detect unusual colors that don't match clean water
        clean_range = self.color_ranges.get("clean", {})
        h_range = clean_range.get("h", [80, 130])
        s_range = clean_range.get("s", [20, 100])
        v_range = clean_range.get("v", [100, 255])

        clean_lower = np.array([h_range[0], s_range[0], v_range[0]])
        clean_upper = np.array([h_range[1], s_range[1], v_range[1]])

        clean_mask = cv2.inRange(hsv, clean_lower, clean_upper)
        contamination_mask = cv2.bitwise_not(clean_mask)

        # Find contours of contamination
        contours, _ = cv2.findContours(contamination_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            return None

        # Find largest contamination area
        largest_contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest_contour)

        if area < self.min_contour_area:
            return None

        # Classify contamination type
        contamination_type = self._classify_contamination(hsv, largest_contour)

        return {
            "type": contamination_type,
            "area": area,
            "confidence": min(1.0, area / 10000)
        }

    def _classify_contamination(self, hsv: np.ndarray, contour) -> str:
        """Classify the type of contamination."""
        mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
        cv2.drawContours(mask, [contour], -1, 255, -1)

        mean_color = cv2.mean(hsv, mask=mask)
        h, s, v = mean_color[:3]

        if 35 <= h <= 85 and s > 50:
            return "algae_bloom"
        elif 10 <= h <= 30 and s > 30:
            return "sediment"
        elif h <= 20 and s > 100 and v < 100:
            return "oil_spill"
        elif 130 <= h <= 180 and s > 50:
            return "chemical"
        else:
            return "unknown"

    def _estimate_turbidity(self, frame: np.ndarray) -> float:
        """Estimate turbidity from image clarity."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()

        # Lower variance = higher turbidity
        # Map variance to NTU (Nephelometric Turbidity Units)
        if laplacian_var > 500:
            return 5.0
        elif laplacian_var > 200:
            return 15.0
        elif laplacian_var > 100:
            return 35.0
        elif laplacian_var > 50:
            return 75.0
        else:
            return 150.0

    def _estimate_dissolved_oxygen(self, color_analysis: dict, turbidity: float) -> float:
        """Estimate dissolved oxygen from color and turbidity."""
        base_do = 8.0  # mg/L for clean water

        # Reduce DO based on turbidity
        turbidity_factor = max(0, 1 - (turbidity / 100))

        # Reduce DO based on contamination
        dominant = color_analysis.get("dominant", "clean")
        contamination_factor = {
            "clean": 1.0,
            "algae": 0.7,
            "sediment": 0.8,
            "oil_spill": 0.3,
            "chemical": 0.4
        }.get(dominant, 0.5)

        return base_do * turbidity_factor * contamination_factor

    def _estimate_ph(self, color_analysis: dict) -> float:
        """Estimate pH from color analysis."""
        dominant = color_analysis.get("dominant", "clean")

        ph_estimates = {
            "clean": 7.0,
            "algae": 8.5,
            "sediment": 6.8,
            "oil_spill": 6.5,
            "chemical": 5.0
        }

        return ph_estimates.get(dominant, 7.0)

    def _classify_water_type(self, color_analysis: dict, contamination: Optional[dict]) -> str:
        """Classify the overall water type."""
        if contamination:
            return contamination.get("type", "unknown")
        return color_analysis.get("dominant", "clean")

    def _determine_severity(self, turbidity: float, dissolved_oxygen: float, ph_level: float, contamination: Optional[dict]) -> str:
        """Determine the severity of water quality issues."""
        score = 0

        # Turbidity scoring
        if turbidity > 100:
            score += 3
        elif turbidity > 50:
            score += 2
        elif turbidity > 20:
            score += 1

        # Dissolved oxygen scoring
        if dissolved_oxygen < 2:
            score += 3
        elif dissolved_oxygen < 4:
            score += 2
        elif dissolved_oxygen < 6:
            score += 1

        # pH scoring
        if ph_level < 5 or ph_level > 9:
            score += 3
        elif ph_level < 6.5 or ph_level > 8.5:
            score += 2
        elif ph_level < 6.8 or ph_level > 7.5:
            score += 1

        # Contamination scoring
        if contamination:
            score += 2

        if score >= 6:
            return "critical"
        elif score >= 4:
            return "high"
        elif score >= 2:
            return "medium"
        elif score >= 1:
            return "low"
        else:
            return "none"

    def _generate_details(self, color_analysis: dict, contamination: Optional[dict], turbidity: float) -> str:
        """Generate human-readable details."""
        details = []

        dominant = color_analysis.get("dominant", "clean")
        confidence = color_analysis.get("confidence", 0)

        details.append(f"Dominant color: {dominant} ({confidence:.0%} confidence)")
        details.append(f"Estimated turbidity: {turbidity:.1f} NTU")

        if contamination:
            details.append(f"Contamination detected: {contamination.get('type', 'unknown')}")
            details.append(f"Contamination area: {contamination.get('area', 0):.0f} pixels")

        return "; ".join(details)

    def _create_empty_reading(self, camera_id: str, location: str) -> WaterQualityReading:
        """Create an empty reading for invalid frames."""
        return WaterQualityReading(
            timestamp=time.time(),
            camera_id=camera_id,
            location=location,
            water_type="unknown",
            confidence=0.0,
            turbidity_ntu=0.0,
            dissolved_oxygen_mg_l=0.0,
            ph_level=0.0,
            temperature_c=0.0,
            contamination_detected=False,
            contamination_type=None,
            severity="unknown",
            details="No frame data available"
        )

    def _record_contamination_event(self, reading: WaterQualityReading, contamination: dict):
        """Record a contamination event."""
        event = ContaminationEvent(
            timestamp=reading.timestamp,
            camera_id=reading.camera_id,
            location=reading.location,
            contamination_type=contamination.get("type", "unknown"),
            severity=reading.severity,
            confidence=contamination.get("confidence", 0.0),
            area_pixels=contamination.get("area", 0),
            recommended_action=self._get_recommended_action(reading.severity, contamination.get("type"))
        )
        self.contamination_events.append(event)

    def _get_recommended_action(self, severity: str, contamination_type: str) -> str:
        """Get recommended action based on severity and contamination type."""
        if severity == "critical":
            return f"IMMEDIATE: Evacuate water source, dispatch emergency response team for {contamination_type}"
        elif severity == "high":
            return f"URGENT: Increase monitoring frequency, prepare treatment for {contamination_type}"
        elif severity == "medium":
            return f"WARNING: Investigate source of {contamination_type}, schedule water testing"
        else:
            return f"Monitor {contamination_type}, continue normal operations"

    def get_statistics(self) -> dict:
        """Get analysis statistics."""
        with self._lock:
            return {
                "total_analyzed": self.total_analyzed,
                "contamination_detected": self.contamination_detected,
                "contamination_rate": self.contamination_detected / max(self.total_analyzed, 1),
                "recent_events": len(self.contamination_events[-100:])
            }
