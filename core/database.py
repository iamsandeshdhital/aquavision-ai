"""
Database Module
Stores all water quality readings, alerts, and camera data.
"""

import os
import json
import time
import sqlite3
import threading
from typing import Dict, List, Optional
from pathlib import Path


class Database:
    """SQLite database for water quality data."""

    def __init__(self, config: dict):
        self.db_path = config.get("database", {}).get("path", "data/aquavision.db")
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._init_database()

    def _init_database(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS readings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    camera_id TEXT NOT NULL,
                    location TEXT,
                    water_type TEXT,
                    confidence REAL,
                    turbidity_ntu REAL,
                    dissolved_oxygen_mg_l REAL,
                    ph_level REAL,
                    temperature_c REAL,
                    contamination_detected INTEGER,
                    contamination_type TEXT,
                    severity TEXT,
                    details TEXT
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    level TEXT NOT NULL,
                    title TEXT NOT NULL,
                    message TEXT,
                    camera_id TEXT,
                    location TEXT,
                    acknowledged INTEGER DEFAULT 0
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cameras (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    location TEXT,
                    type TEXT,
                    url TEXT,
                    status TEXT DEFAULT 'active'
                )
            ''')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_readings_time ON readings(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_time ON alerts(timestamp)')
            conn.commit()

    def save_reading(self, reading):
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO readings (timestamp, camera_id, location, water_type, confidence,
                        turbidity_ntu, dissolved_oxygen_mg_l, ph_level, temperature_c,
                        contamination_detected, contamination_type, severity, details)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    reading.timestamp, reading.camera_id, reading.location,
                    reading.water_type, reading.confidence, reading.turbidity_ntu,
                    reading.dissolved_oxygen_mg_l, reading.ph_level, reading.temperature_c,
                    1 if reading.contamination_detected else 0,
                    reading.contamination_type, reading.severity, reading.details
                ))
                conn.commit()

    def save_alert(self, alert):
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO alerts (timestamp, level, title, message, camera_id, location, acknowledged)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    alert.timestamp, alert.level.value, alert.title,
                    alert.message, alert.camera_id, alert.location,
                    1 if alert.acknowledged else 0
                ))
                conn.commit()

    def get_recent_readings(self, hours=24):
        cutoff = time.time() - (hours * 3600)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM readings WHERE timestamp > ? ORDER BY timestamp DESC', (cutoff,))
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def get_alerts(self, acknowledged=None, hours=24):
        cutoff = time.time() - (hours * 3600)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if acknowledged is None:
                cursor.execute('SELECT * FROM alerts WHERE timestamp > ? ORDER BY timestamp DESC', (cutoff,))
            else:
                cursor.execute('SELECT * FROM alerts WHERE timestamp > ? AND acknowledged = ? ORDER BY timestamp DESC',
                             (cutoff, 1 if acknowledged else 0))
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def get_statistics(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM readings')
            total = cursor.fetchone()[0]
            cursor.execute('SELECT COUNT(*) FROM readings WHERE contamination_detected = 1')
            contaminated = cursor.fetchone()[0]
            cursor.execute('SELECT COUNT(*) FROM alerts')
            alerts = cursor.fetchone()[0]
            return {"total_readings": total, "contaminated": contaminated, "total_alerts": alerts}
