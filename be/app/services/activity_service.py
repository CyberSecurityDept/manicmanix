from typing import Dict, Any
from app.repositories import activity_repo


def get_detected_activities() -> Dict[str, Any]:
    activities = activity_repo.get_activities_from_file()
    response = {
        "status": "success",
        "message": "Detected activities retrieved successfully.",
        "data": activities,
    }
    return response

def get_fullscan_detected_activities() -> Dict[str, Any]:
    activities = activity_repo.get_fullscan_activities_from_file()
    response = {
        "status": "success",
        "message": "Detected activities retrieved successfully.",
        "data": activities,
    }
    return response