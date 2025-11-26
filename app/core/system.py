"""
שירותים משותפים לאיסוף נתוני מערכת
ניתן לשימוש חוזר במודולים שונים
"""

import platform
import os
import psutil
from typing import Dict, Optional, Tuple


def get_os_info() -> str:
    """
    מחזיר מידע על מערכת ההפעלה
    דוגמה: "Debian GNU/Linux 13 (bookworm)"
    """
    try:
        with open('/etc/os-release', 'r') as f:
            os_info = {}
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    os_info[key] = value.strip('"')
            
            # דוגמה: "Debian GNU/Linux 13 (bookworm)"
            return os_info.get('PRETTY_NAME', f"{platform.system()} {platform.release()}")
    except Exception:
        # fallback ל-platform
        return f"{platform.system()} {platform.release()}"


def get_cpu_info() -> str:
    """
    מחזיר מידע על המעבד
    דוגמה: "Sony UK BCM2837 (4 cores)"
    """
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpu_info = {}
            for line in f:
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    if key not in cpu_info:
                        cpu_info[key] = value
            
            # דוגמה: "Sony UK BCM2837"
            model = cpu_info.get('Model', cpu_info.get('Hardware', platform.processor()))
            cpu_count = os.cpu_count() or 1
            
            return f"{model} ({cpu_count} cores)"
    except Exception:
        return f"{platform.processor()} ({os.cpu_count() or 1} cores)"


def get_uptime() -> str:
    """
    מחזיר זמן פעילות של המערכת
    דוגמה: "0 days 9 hours 12 minutes"
    """
    try:
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.read().split()[0])
            days = int(uptime_seconds // 86400)
            hours = int((uptime_seconds % 86400) // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            
            return f"{days} days {hours} hours {minutes} minutes"
    except Exception:
        return "N/A"


def get_cpu_temperature() -> Optional[float]:
    """
    מחזיר טמפרטורת CPU ב-°C
    None אם לא ניתן לקרוא
    """
    try:
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            temp = int(f.read().strip()) / 1000.0
            return round(temp, 1)
    except Exception:
        return None


def get_temperature_class(temperature: Optional[float]) -> str:
    """
    מחזיר את ה-CSS class לפי טמפרטורה
    cold: < 40°C
    normal: 40-55°C
    warm: 55-70°C
    hot: > 70°C
    """
    if temperature is None:
        return "normal"
    
    if temperature < 40:
        return "cold"
    elif temperature < 55:
        return "normal"
    elif temperature < 70:
        return "warm"
    else:
        return "hot"


def get_cpu_usage() -> float:
    """
    מחזיר אחוז שימוש ב-CPU
    """
    try:
        return round(psutil.cpu_percent(interval=1), 1)
    except Exception:
        return 0.0


def get_ram_usage() -> Tuple[str, str, float]:
    """
    מחזיר נתוני RAM: (used, total, percent)
    דוגמה: ("1.2GB", "4.0GB", 30.0)
    """
    try:
        ram = psutil.virtual_memory()
        ram_total_gb = round(ram.total / (1024**3), 2)
        ram_used_gb = round(ram.used / (1024**3), 2)
        ram_percent = round(ram.percent, 1)
        
        return (f"{ram_used_gb}GB", f"{ram_total_gb}GB", ram_percent)
    except Exception:
        return ("0GB", "0GB", 0.0)


def get_static_info() -> Dict:
    """
    נתונים סטטיים שלא משתנים
    לשימוש בעדכון חד פעמי
    """
    ram_used, ram_total, _ = get_ram_usage()
    
    return {
        "os_name": get_os_info(),
        "hardware": get_cpu_info(),
        "ram_total": ram_total,
    }


def get_storage_info() -> Dict:
    """
    מחזיר נתוני Storage עבור Boot ו-Root partitions
    Returns:
        dict עם boot ו-root storage info
    """
    try:
        boot_info = None
        root_info = None
        
        # איסוף נתונים על כל ה-partitions
        partitions = psutil.disk_partitions()
        
        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                
                total_gb = round(usage.total / (1024**3), 2)
                used_gb = round(usage.used / (1024**3), 2)
                free_gb = round(usage.free / (1024**3), 2)
                percent = round(usage.percent, 2)
                
                partition_info = {
                    "device": partition.device,
                    "mountpoint": partition.mountpoint,
                    "total": f"{total_gb} GB",
                    "used": f"{used_gb} GB",
                    "free": f"{free_gb} GB",
                    "percent": percent
                }
                
                # Boot partition
                if partition.mountpoint == '/boot/firmware' or 'boot' in partition.mountpoint.lower():
                    boot_info = partition_info
                
                # Root partition
                if partition.mountpoint == '/':
                    root_info = partition_info
                    
            except PermissionError:
                # חלק מה-partitions לא נגישים
                continue
        
        return {
            "boot": boot_info or {
                "device": "N/A",
                "mountpoint": "/boot/firmware",
                "total": "0 GB",
                "used": "0 GB",
                "free": "0 GB",
                "percent": 0.0
            },
            "root": root_info or {
                "device": "N/A",
                "mountpoint": "/",
                "total": "0 GB",
                "used": "0 GB",
                "free": "0 GB",
                "percent": 0.0
            }
        }
    except Exception as e:
        return {
            "boot": {
                "device": "N/A",
                "mountpoint": "/boot/firmware",
                "total": "0 GB",
                "used": "0 GB",
                "free": "0 GB",
                "percent": 0.0
            },
            "root": {
                "device": "N/A",
                "mountpoint": "/",
                "total": "0 GB",
                "used": "0 GB",
                "free": "0 GB",
                "percent": 0.0
            }
        }


def get_slow_dynamic_info() -> Dict:
    """
    נתונים דינמיים שמשתנים לאט
    לשימוש בעדכון כל 60 שניות
    """
    storage_data = get_storage_info()
    
    return {
        "uptime": get_uptime(),
        "storage_boot": storage_data["boot"],
        "storage_root": storage_data["root"],
    }


def get_fast_dynamic_info() -> Dict:
    """
    נתונים דינמיים שמשתנים במהירות
    לשימוש בעדכון כל 5 שניות
    """
    cpu_temp = get_cpu_temperature()
    cpu_temp_percent = min(100, int((cpu_temp / 85) * 100)) if cpu_temp else 0  # 85°C = 100%
    temp_class = get_temperature_class(cpu_temp)
    
    ram_used, _, ram_percent = get_ram_usage()
    
    return {
        "cpu_temp": cpu_temp or 0.0,
        "cpu_temp_percent": cpu_temp_percent,
        "temp_class": temp_class,
        "cpu_usage": get_cpu_usage(),
        "ram_used": ram_used,
        "ram_percent": ram_percent,
    }


def get_system_info() -> Dict:
    """
    פונקציה מרכזית שמחזירה dict עם כל נתוני המערכת
    לשימוש ב-WebSocket ו-services
    שמורה לתאימות לאחור
    """
    cpu_temp = get_cpu_temperature()
    cpu_temp_percent = min(100, int((cpu_temp / 85) * 100)) if cpu_temp else 0  # 85°C = 100%
    temp_class = get_temperature_class(cpu_temp)
    
    ram_used, ram_total, ram_percent = get_ram_usage()
    
    return {
        "os_name": get_os_info(),
        "hardware": get_cpu_info(),
        "uptime": get_uptime(),
        "cpu_temp": cpu_temp or 0.0,
        "cpu_temp_percent": cpu_temp_percent,
        "temp_class": temp_class,
        "cpu_usage": get_cpu_usage(),
        "ram_used": ram_used,
        "ram_total": ram_total,
        "ram_percent": ram_percent,
    }

