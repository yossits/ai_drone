"""
Background Task לעדכונים אוטומטיים של נתוני מערכת
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional

from app.core.system import get_system_info
from app.core.websocket import websocket_manager

logger = logging.getLogger(__name__)

# משתנה גלובלי לניהול המשימה
_monitoring_task: Optional[asyncio.Task] = None
_monitoring_interval: int = 5  # שניות


async def monitor_loop(interval: int = 5):
    """
    לולאה ששולחת עדכונים כל X שניות
    Args:
        interval: מרווח זמן בין עדכונים בשניות
    """
    logger.info(f"Starting system monitor with interval: {interval} seconds")
    
    while True:
        try:
            # איסוף נתוני מערכת
            system_data = get_system_info()
            
            # הוספת timestamp
            system_data["timestamp"] = datetime.now().isoformat()
            
            # שליחת עדכון דרך WebSocket
            sent_count = await websocket_manager.broadcast("system_info", system_data)
            
            if sent_count > 0:
                logger.debug(f"Broadcasted system info to {sent_count} connections")
            
            # המתנה לפני העדכון הבא
            await asyncio.sleep(interval)
        
        except asyncio.CancelledError:
            logger.info("System monitor cancelled")
            break
        except Exception as e:
            logger.error(f"Error in monitor loop: {e}")
            # המתנה קצרה לפני ניסיון חוזר
            await asyncio.sleep(interval)


def start_monitoring(interval: int = 5) -> bool:
    """
    התחלת monitoring
    Args:
        interval: מרווח זמן בין עדכונים בשניות (ברירת מחדל: 5)
    Returns:
        True אם ההתחלה הצליחה, False אם כבר רץ
    """
    global _monitoring_task, _monitoring_interval
    
    if _monitoring_task is not None and not _monitoring_task.done():
        logger.warning("System monitor is already running")
        return False
    
    _monitoring_interval = interval
    
    try:
        # יצירת task חדש
        loop = asyncio.get_event_loop()
        _monitoring_task = loop.create_task(monitor_loop(interval))
        logger.info(f"System monitor started with interval: {interval} seconds")
        return True
    except Exception as e:
        logger.error(f"Error starting system monitor: {e}")
        return False


async def stop_monitoring() -> bool:
    """
    עצירת monitoring
    Returns:
        True אם העצירה הצליחה, False אם לא רץ
    """
    global _monitoring_task
    
    if _monitoring_task is None or _monitoring_task.done():
        logger.warning("System monitor is not running")
        return False
    
    try:
        _monitoring_task.cancel()
        await _monitoring_task
        _monitoring_task = None
        logger.info("System monitor stopped")
        return True
    except Exception as e:
        logger.error(f"Error stopping system monitor: {e}")
        return False


def is_monitoring() -> bool:
    """
    בדיקה אם monitoring רץ
    Returns:
        True אם monitoring רץ, False אחרת
    """
    return _monitoring_task is not None and not _monitoring_task.done()


def get_monitoring_interval() -> int:
    """
    מחזיר את מרווח הזמן הנוכחי
    Returns:
        מרווח זמן בשניות
    """
    return _monitoring_interval


async def send_single_update():
    """
    שליחת עדכון בודד (ללא לולאה)
    שימושי לבדיקות או עדכונים ידניים
    """
    try:
        system_data = get_system_info()
        system_data["timestamp"] = datetime.now().isoformat()
        sent_count = await websocket_manager.broadcast("system_info", system_data)
        logger.info(f"Sent single system info update to {sent_count} connections")
        return sent_count
    except Exception as e:
        logger.error(f"Error sending single update: {e}")
        return 0

