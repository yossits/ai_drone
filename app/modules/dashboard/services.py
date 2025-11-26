"""
לוגיקה ונתוני דמו למודול Dashboard
"""

from datetime import datetime
from app.core.system import get_system_info, get_storage_info


def get_dashboard_data():
    """מחזיר נתוני דמו ל-Dashboard"""
    # איסוף נתוני מערכת אמיתיים
    system_data = get_system_info()
    storage_data = get_storage_info()
    
    return {
        # נתוני מערכת אמיתיים
        "os_name": system_data["os_name"],
        "hardware": system_data["hardware"],
        "uptime": system_data["uptime"],
        "cpu_temp": system_data["cpu_temp"],
        "cpu_temp_percent": system_data["cpu_temp_percent"],
        "temp_class": system_data["temp_class"],
        "cpu_usage": system_data["cpu_usage"],
        "ram_used": system_data["ram_used"],
        "ram_total": system_data["ram_total"],
        "ram_percent": system_data["ram_percent"],
        # נתוני Storage
        "storage_boot": storage_data["boot"],
        "storage_root": storage_data["root"],
        # נתוני דמו (לעתיד)
        "system_status": "Online",
        "battery_level": 85,
        "connection_status": "Connected",
        "flight_time": "00:15:32",
        "altitude": 45.2,
        "speed": 12.5,
        "gps_satellites": 12,
        "signal_strength": 95,
        "last_update": datetime.now().strftime("%H:%M:%S"),
    }
