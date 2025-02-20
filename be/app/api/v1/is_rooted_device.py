from fastapi import APIRouter, HTTPException
from app.services.is_rooted_device_service import check_if_device_is_rooted

# Inisialisasi router
router = APIRouter()

@router.get("/is-rooted/{serial_number}")
async def is_rooted(serial_number: str):
    try:
        # Panggil layanan untuk memeriksa status root
        is_rooted = check_if_device_is_rooted(serial_number)
        return {
            "status": 200,
            "message": "Root status checked successfully",
            "data": {
                "serial_number": serial_number,
                "is_rooted": is_rooted,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check root status: {str(e)}")