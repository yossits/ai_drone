"""
WebSocket Manager לניהול connections ו-topics
מאפשר ניהול מרכזי של כל ה-WebSocket connections באפליקציה
"""

from typing import Set, Dict, Optional
from fastapi import WebSocket
import json
import logging

logger = logging.getLogger(__name__)


class WebSocketManager:
    """
    מנהל WebSocket connections ו-topics
    """
    
    def __init__(self):
        """אתחול המנהל"""
        self.connections: Set[WebSocket] = set()
        self.topics: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, topic: Optional[str] = None) -> bool:
        """
        חיבור client ל-WebSocket
        Args:
            websocket: WebSocket connection
            topic: Topic ספציפי (אופציונלי)
        Returns:
            True אם החיבור הצליח, False אחרת
        """
        try:
            await websocket.accept()
            self.connections.add(websocket)
            
            if topic:
                await self.subscribe(websocket, topic)
            
            logger.info(f"WebSocket connected. Total connections: {len(self.connections)}")
            return True
        except Exception as e:
            logger.error(f"Error connecting WebSocket: {e}")
            return False
    
    def disconnect(self, websocket: WebSocket) -> None:
        """
        ניתוק client
        Args:
            websocket: WebSocket connection לניתוק
        """
        if websocket in self.connections:
            self.connections.remove(websocket)
        
        # הסרת ה-connection מכל ה-topics
        for topic in list(self.topics.keys()):
            self.topics[topic].discard(websocket)
            # הסרת topics ריקים
            if not self.topics[topic]:
                del self.topics[topic]
        
        logger.info(f"WebSocket disconnected. Total connections: {len(self.connections)}")
    
    async def subscribe(self, websocket: WebSocket, topic: str) -> bool:
        """
        הרשמה ל-topic
        Args:
            websocket: WebSocket connection
            topic: שם ה-topic
        Returns:
            True אם ההרשמה הצליחה
        """
        try:
            if topic not in self.topics:
                self.topics[topic] = set()
            
            self.topics[topic].add(websocket)
            logger.debug(f"WebSocket subscribed to topic: {topic}")
            return True
        except Exception as e:
            logger.error(f"Error subscribing to topic {topic}: {e}")
            return False
    
    def unsubscribe(self, websocket: WebSocket, topic: str) -> None:
        """
        ביטול הרשמה ל-topic
        Args:
            websocket: WebSocket connection
            topic: שם ה-topic
        """
        if topic in self.topics:
            self.topics[topic].discard(websocket)
            # הסרת topic ריק
            if not self.topics[topic]:
                del self.topics[topic]
            logger.debug(f"WebSocket unsubscribed from topic: {topic}")
    
    async def send_personal_message(self, websocket: WebSocket, message: dict) -> bool:
        """
        שליחת הודעה ל-connection ספציפי
        Args:
            websocket: WebSocket connection
            message: הודעה לשליחה (dict)
        Returns:
            True אם השליחה הצליחה, False אחרת
        """
        try:
            await websocket.send_json(message)
            return True
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            return False
    
    async def broadcast(self, topic: str, data: dict) -> int:
        """
        שליחת עדכון לכל ה-subscribers של topic
        Args:
            topic: שם ה-topic
            data: נתונים לשליחה
        Returns:
            מספר ה-connections שקיבלו את ההודעה
        """
        if topic not in self.topics:
            logger.debug(f"No subscribers for topic: {topic}")
            return 0
        
        message = {
            "topic": topic,
            "data": data
        }
        
        disconnected = set()
        sent_count = 0
        
        for websocket in self.topics[topic].copy():
            try:
                await websocket.send_json(message)
                sent_count += 1
            except Exception as e:
                logger.warning(f"Error broadcasting to WebSocket: {e}")
                disconnected.add(websocket)
        
        # ניקוי connections מנותקים
        for ws in disconnected:
            self.disconnect(ws)
        
        logger.debug(f"Broadcasted to {sent_count} connections for topic: {topic}")
        return sent_count
    
    async def broadcast_to_all(self, data: dict) -> int:
        """
        שליחת הודעה לכל ה-connections
        Args:
            data: נתונים לשליחה
        Returns:
            מספר ה-connections שקיבלו את ההודעה
        """
        message = {
            "topic": "broadcast",
            "data": data
        }
        
        disconnected = set()
        sent_count = 0
        
        for websocket in self.connections.copy():
            try:
                await websocket.send_json(message)
                sent_count += 1
            except Exception as e:
                logger.warning(f"Error broadcasting to all: {e}")
                disconnected.add(websocket)
        
        # ניקוי connections מנותקים
        for ws in disconnected:
            self.disconnect(ws)
        
        logger.debug(f"Broadcasted to {sent_count} connections")
        return sent_count
    
    def get_connection_count(self) -> int:
        """
        מחזיר מספר connections פעילים
        Returns:
            מספר connections
        """
        return len(self.connections)
    
    def get_topic_subscribers_count(self, topic: str) -> int:
        """
        מחזיר מספר subscribers ל-topic
        Args:
            topic: שם ה-topic
        Returns:
            מספר subscribers
        """
        return len(self.topics.get(topic, set()))
    
    def get_topics(self) -> list:
        """
        מחזיר רשימת כל ה-topics
        Returns:
            רשימת topics
        """
        return list(self.topics.keys())


# יצירת instance גלובלי של המנהל
websocket_manager = WebSocketManager()

