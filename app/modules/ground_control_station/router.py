"""
Router למודול Ground Control Station
"""
from typing import List
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from app.core.templates import templates
from app.modules.ground_control_station import services

router = APIRouter(prefix="/ground-control-station", tags=["ground-control-station"])


class Destination(BaseModel):
    """מודל ל-destination"""
    name: str
    ip: str
    port: str
    destinationEnabled: bool
    telemetryEnabled: bool


class DestinationsRequest(BaseModel):
    """מודל לבקשת שמירת destinations"""
    destinations: List[Destination]


@router.get("/", response_class=HTMLResponse)
async def gcs_page(request: Request):
    """דף Ground Control Station"""
    data = services.get_gcs_data()
    return templates.TemplateResponse(
        "ground_control_station/templates/ground_control_station.html",
        {"request": request, **data}
    )


@router.post("/destinations")
async def save_destinations(request: DestinationsRequest):
    """שומר destinations"""
    destinations_data = [dest.dict() for dest in request.destinations]
    success = services.save_destinations(destinations_data)
    
    if success:
        return JSONResponse({"status": "success"})
    else:
        return JSONResponse({"status": "error", "message": "Failed to save destinations"}, status_code=500)

