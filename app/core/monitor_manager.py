"""
Monitor Manager - ניהול 3 monitors לפי תדירות
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Optional, Callable, Any

from app.core.websocket import websocket_manager

logger = logging.getLogger(__name__)


class MonitorManager:
    """
    מנהל 3 monitors: fast (5s), slow (60s), static (once)
    """
    
    def __init__(self):
        """אתחול המנהל"""
        self.monitors: Dict[str, Dict] = {}  # topic -> {task, interval, data_function}
        self.static_sent: set = set()  # topics סטטיים שכבר נשלחו
    
    def register_monitor(
        self,
        topic: str,
        data_function: Callable[[], Dict[str, Any]],
        interval: Optional[float] = None
    ) -> bool:
        """
        רישום monitor חדש
        Args:
            topic: שם ה-topic (למשל: "fast_info")
            data_function: פונקציה שמחזירה dict עם הנתונים
            interval: מרווח זמן בשניות (None = חד פעמי)
        Returns:
            True אם הרישום הצליח, False אם כבר קיים
        """
        if topic in self.monitors:
            logger.warning(f"Monitor '{topic}' already registered")
            return False
        
        self.monitors[topic] = {
            "data_function": data_function,
            "interval": interval,
            "task": None
        }
        logger.info(f"Registered monitor '{topic}' with interval: {interval}")
        return True
    
    async def start_all(self) -> None:
        """
        הפעלת כל ה-monitors
        """
        for topic, monitor_info in self.monitors.items():
            if monitor_info["task"] is not None:
                continue  # כבר רץ
            
            interval = monitor_info["interval"]
            
            if interval is None:
                # עדכון חד פעמי
                task = asyncio.create_task(self._send_one_time(topic))
            else:
                # עדכון תקופתי
                task = asyncio.create_task(self._monitor_loop(topic, interval))
            
            monitor_info["task"] = task
            logger.info(f"Started monitor '{topic}' with interval: {interval}")
    
    async def stop_all(self) -> None:
        """
        עצירת כל ה-monitors
        """
        for topic, monitor_info in self.monitors.items():
            task = monitor_info["task"]
            if task is not None and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                monitor_info["task"] = None
                logger.info(f"Stopped monitor '{topic}'")
    
    async def _send_one_time(self, topic: str) -> None:
        """
        שליחת עדכון חד פעמי
        """
        if topic in self.static_sent:
            return  # כבר נשלח
        
        try:
            monitor_info = self.monitors[topic]
            data_function = monitor_info["data_function"]
            
            data = data_function()
            data["timestamp"] = datetime.now().isoformat()
            
            # המתנה קצרה כדי שה-clients יספיקו לעשות subscribe
            await asyncio.sleep(1)
            
            sent_count = await websocket_manager.broadcast(topic, data)
            self.static_sent.add(topic)
            
            logger.info(f"Sent one-time update for '{topic}' to {sent_count} connections")
        except Exception as e:
            logger.error(f"Error sending one-time update for '{topic}': {e}")
    
    async def _monitor_loop(self, topic: str, interval: float) -> None:
        """
        לולאת monitoring תקופתי
        """
        logger.info(f"Starting monitor loop for '{topic}' with interval: {interval}s")
        
        # שליחה מיד בהתחלה (לפני ה-sleep הראשון)
        try:
            monitor_info = self.monitors[topic]
            data_function = monitor_info["data_function"]
            
            data = data_function()
            data["timestamp"] = datetime.now().isoformat()
            
            # המתנה קצרה כדי שה-clients יספיקו לעשות subscribe
            await asyncio.sleep(1)
            
            sent_count = await websocket_manager.broadcast(topic, data)
            
            if sent_count > 0:
                logger.debug(f"Broadcasted '{topic}' to {sent_count} connections (initial)")
            else:
                logger.debug(f"No connections for topic '{topic}' (initial)")
        except Exception as e:
            logger.error(f"Error in initial broadcast for '{topic}': {e}")
        
        # עכשיו הלולאה הרגילה
        while True:
            try:
                monitor_info = self.monitors[topic]
                data_function = monitor_info["data_function"]
                
                # איסוף נתונים
                data = data_function()
                data["timestamp"] = datetime.now().isoformat()
                
                # המתנה לפני העדכון הבא
                await asyncio.sleep(interval)
                
                # שליחה דרך WebSocket
                sent_count = await websocket_manager.broadcast(topic, data)
                
                if sent_count > 0:
                    logger.debug(f"Broadcasted '{topic}' to {sent_count} connections")
                else:
                    logger.debug(f"No connections for topic '{topic}'")
            
            except asyncio.CancelledError:
                logger.info(f"Monitor '{topic}' cancelled")
                break
            except Exception as e:
                logger.error(f"Error in monitor loop for '{topic}': {e}")
                await asyncio.sleep(interval)


# יצירת instance גלובלי
monitor_manager = MonitorManager()

