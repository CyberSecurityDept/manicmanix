from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.services.package_service import PackageService
from app.repositories.package_repositories import PackageRepository


router = APIRouter()


repository = PackageRepository()
service = PackageService(repository)

@router.get("/packages", response_class=JSONResponse)
async def get_packages():
    try:
        
        installed_apps_data = service.get_installed_apps_data()
        installed_apps_count = installed_apps_data["count"]
        installed_packages = installed_apps_data["data"]

        malicious_apps_data = service.get_malicious_apps_data()
        malicious_apps_count = malicious_apps_data["count"]
        malicious_packages = malicious_apps_data["data"]

        
        return {
            "installed_apps": installed_apps_count,
            "malicious_detected": malicious_apps_count,
            "installed_packages": installed_packages,
            "malicious_packages": malicious_packages
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})