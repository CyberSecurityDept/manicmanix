from fastapi import APIRouter
from app.repositories.simplify_info import get_device_info

router = APIRouter()


@router.get("/simplify-get-info")
async def simplify_get_info():
    """Endpoint to retrieve phone model and security patch version."""
    device_info = get_device_info()
    return {
        "status": "success" if "error" not in device_info else "failure",
        "message": (
            "Device info retrieved successfully"
            if "error" not in device_info
            else "Failed to retrieve device info"
        ),
        "data": device_info,
    }
