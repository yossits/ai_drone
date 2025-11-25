"""
נקודת כניסה לאפליקציה - FastAPI
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pathlib import Path

from app.config import settings
from app.core.static import STATIC_DIR

# ייבוא routers מכל המודולים
from app.modules.dashboard import router as dashboard_router
from app.modules.flight_controller import router as flight_controller_router
from app.modules.flight_map import router as flight_map_router
from app.modules.ground_control_station import router as gcs_router
from app.modules.modem import router as modem_router
from app.modules.vpn import router as vpn_router
from app.modules.dynamic_dns import router as dns_router
from app.modules.camera import router as camera_router
from app.modules.networks import router as networks_router
from app.modules.users import router as users_router
from app.modules.application import router as application_router

# ייבוא WebSocket router
from app.core import websocket_router

# ייבוא system monitor
from app.core.system_monitor import start_monitoring, stop_monitoring

# יצירת FastAPI app
app = FastAPI(
    title=settings.APP_NAME, version=settings.APP_VERSION, debug=settings.DEBUG
)

# חיבור Static Files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# חיבור routers של כל המודולים
app.include_router(dashboard_router)
app.include_router(flight_controller_router)
app.include_router(flight_map_router)
app.include_router(gcs_router)
app.include_router(modem_router)
app.include_router(vpn_router)
app.include_router(dns_router)
app.include_router(camera_router)
app.include_router(networks_router)
app.include_router(users_router)
app.include_router(application_router)

# חיבור WebSocket router
app.include_router(websocket_router.router)


# Root redirect ל-dashboard
@app.get("/")
async def root():
    return RedirectResponse(url="/dashboard")


# Startup event - הפעלת system monitor
@app.on_event("startup")
async def startup_event():
    """הפעלת system monitor בעת הפעלת האפליקציה"""
    start_monitoring(interval=5)
    print("System monitor started")


# Shutdown event - עצירת system monitor
@app.on_event("shutdown")
async def shutdown_event():
    """עצירת system monitor בעת סגירת האפליקציה"""
    await stop_monitoring()
    print("System monitor stopped")
