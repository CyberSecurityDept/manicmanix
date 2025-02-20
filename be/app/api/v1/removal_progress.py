from fastapi import APIRouter, HTTPException
from app.services.removal_progress_service import calculate_removal_progress
from typing import List

# Inisialisasi router FastAPI
router = APIRouter()

@router.post("/removal-progress-threshold")
async def removal_progress_threshold(
    serial_number: str,
    package_names: List[str],
    threshold: int
):
    try:
        # Validasi input
        if not (0 <= threshold <= 100):
            raise ValueError("Threshold harus berada dalam rentang 0-100.")
        
        # Panggil service untuk menghitung progress
        result = calculate_removal_progress(serial_number, package_names, threshold)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail={"status": "error", "message": str(e)})
    except Exception as e:
        raise HTTPException(status_code=500, detail={"status": "error", "message": str(e)})