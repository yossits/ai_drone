"""
לוגיקה ונתוני דמו למודול Ground Control Station
"""
import json
import os
from datetime import datetime
from pathlib import Path

# נתיב לקובץ הנתונים
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = BASE_DIR / "data"
DESTINATIONS_FILE = DATA_DIR / "ground_control_station.json"


def ensure_data_dir():
    """יוצר את תיקיית data אם היא לא קיימת"""
    DATA_DIR.mkdir(exist_ok=True)


def load_destinations():
    """טוען destinations מקובץ JSON"""
    ensure_data_dir()
    
    if not DESTINATIONS_FILE.exists():
        return []
    
    try:
        with open(DESTINATIONS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('destinations', [])
    except (json.JSONDecodeError, IOError):
        return []


def save_destinations(destinations):
    """שומר destinations לקובץ JSON"""
    ensure_data_dir()
    
    data = {
        "destinations": destinations
    }
    
    try:
        with open(DESTINATIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except IOError:
        return False


def get_gcs_data():
    """מחזיר נתוני דמו ל-Ground Control Station"""
    destinations = load_destinations()
    
    return {
        "destinations": destinations,
        "logs": [
            {"time": "10:15:32", "level": "INFO", "message": "System initialized"},
            {"time": "10:15:35", "level": "INFO", "message": "Flight controller connected"},
            {"time": "10:15:40", "level": "WARNING", "message": "GPS signal weak"},
            {"time": "10:15:45", "level": "INFO", "message": "GPS signal restored"},
            {"time": "10:16:00", "level": "INFO", "message": "Ready for takeoff"},
        ],
        "commands": [
            "ARM",
            "DISARM",
            "TAKEOFF",
            "LAND",
            "RTL",
            "GUIDED",
            "AUTO"
        ]
    }

