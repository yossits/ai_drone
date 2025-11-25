"""
WebSocket Router - ניהול WebSocket endpoints
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import HTMLResponse
import logging
import json

from app.core.websocket import websocket_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["websocket"])


@router.websocket("/")
async def websocket_endpoint(websocket: WebSocket, topic: str = Query(None)):
    """
    WebSocket endpoint ראשי
    Args:
        websocket: WebSocket connection
        topic: Topic ספציפי (אופציונלי, ניתן להעביר כ-query parameter)
    """
    await websocket_manager.connect(websocket, topic)
    
    try:
        while True:
            # קבלת הודעות מה-client (אם נדרש)
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                action = message.get("action")
                
                if action == "subscribe":
                    topic_name = message.get("topic")
                    if topic_name:
                        await websocket_manager.subscribe(websocket, topic_name)
                        await websocket_manager.send_personal_message(
                            websocket,
                            {"status": "subscribed", "topic": topic_name}
                        )
                
                elif action == "unsubscribe":
                    topic_name = message.get("topic")
                    if topic_name:
                        websocket_manager.unsubscribe(websocket, topic_name)
                        await websocket_manager.send_personal_message(
                            websocket,
                            {"status": "unsubscribed", "topic": topic_name}
                        )
                
                elif action == "ping":
                    await websocket_manager.send_personal_message(
                        websocket,
                        {"status": "pong"}
                    )
                
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON received: {data}")
            except Exception as e:
                logger.error(f"Error processing message: {e}")
    
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        websocket_manager.disconnect(websocket)


@router.websocket("/{topic}")
async def websocket_topic_endpoint(websocket: WebSocket, topic: str):
    """
    WebSocket endpoint עם topic ספציפי
    Args:
        websocket: WebSocket connection
        topic: שם ה-topic
    """
    await websocket_manager.connect(websocket, topic)
    
    try:
        while True:
            # קבלת הודעות מה-client (אם נדרש)
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                action = message.get("action")
                
                if action == "unsubscribe":
                    websocket_manager.unsubscribe(websocket, topic)
                    await websocket_manager.send_personal_message(
                        websocket,
                        {"status": "unsubscribed", "topic": topic}
                    )
                
                elif action == "ping":
                    await websocket_manager.send_personal_message(
                        websocket,
                        {"status": "pong", "topic": topic}
                    )
                
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON received: {data}")
            except Exception as e:
                logger.error(f"Error processing message: {e}")
    
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
        logger.info(f"WebSocket disconnected from topic: {topic}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        websocket_manager.disconnect(websocket)


@router.get("/status")
async def websocket_status():
    """
    מחזיר סטטוס של WebSocket connections
    """
    return {
        "connections": websocket_manager.get_connection_count(),
        "topics": websocket_manager.get_topics(),
        "topic_subscribers": {
            topic: websocket_manager.get_topic_subscribers_count(topic)
            for topic in websocket_manager.get_topics()
        }
    }

