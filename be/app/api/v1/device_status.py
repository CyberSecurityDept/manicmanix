from fastapi import APIRouter
from app.services.device_status_service import DeviceStatusService

router = APIRouter()


@router.get("/check-device-status/")
async def check_device_status():
    status_data = DeviceStatusService.check_and_save_device_status()

    return {
        "status": 200,
        "message": "Check device status successfully",
        "data": status_data,
    }
