from fastapi import APIRouter
from app.services import activity_service
from typing import Dict, Any

router = APIRouter()


@router.get("/activities", response_model=Dict[str, Any])
async def get_activities():
    return activity_service.get_detected_activities()

@router.get("/fullscan-activities", response_model=Dict[str, Any])
async def get_fullscan_activities():
    return activity_service.get_fullscan_detected_activities()