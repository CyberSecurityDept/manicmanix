from fastapi import APIRouter
from fastapi import HTTPException
from app.services.data_pulling_service import dataPullingService
router = APIRouter()

@router.get("/pull-data/", response_model=dict)
async def pull_data():
    try:
        result = dataPullingService.process_all_devices()
        return {
            "status": 200,
            "message": "Get categories successfully",
            "data": {
                "categories": result
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))