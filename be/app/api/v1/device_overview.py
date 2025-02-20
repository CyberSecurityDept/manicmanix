from fastapi import APIRouter
from app.services.device_overview_service import DeviceOverviewService

router = APIRouter()


@router.get("/device-overview/")
async def device_overview():
    try:
        overview_data = DeviceOverviewService.get_device_overview()

        return {
            "status": 200,
            "message": "Get Device Overview successfully",
            "data": overview_data,
        }
    except Exception as e:
        return {
            "status": 500,
            "message": "Failed to get device overview",
            "error": str(e),
        }
