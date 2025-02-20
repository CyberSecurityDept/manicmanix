import os

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from fastapi.responses import HTMLResponse
from app.api.v1.device_status import router as device_status_router
from app.api.v1.device_overview import router as device_overview_router
from app.api.v1.device_scan import router as device_scan_router
from app.api.v1.activities import router as activities_router
from app.api.v1.simplify_device_info import router as simplify_device_router
from app.api.v1.malware_removal import router as removal_router
from fastapi.staticfiles import StaticFiles
from app.api.v1.pull_data import router as pull_data_router
from app.api.v1.results import router as results_router
from app.api.v1.check_update import router as check_update_router
from app.api.v1.history_scan import router as history_scan_router
from app.api.v1.list_version import router as list_version
from app.api.v1.is_rooted_device import router as is_rooted_device
from app.api.v1.removal_progress import router as removal_progress
from app.api.v1.packages import router as package
from app.api.v1.result_fastscan import router as result_fastscan
from app.api.v1.history_full_scan import router as history_fullscan_router
# from app.api.v1.history_fast_scan import router as history_fastscan_router
from app.api.v1.history_fast_scan import router as history_fastscan_router
from app.api.v1.check_update_app import router as check_update_app
from app.api.v1.update_cyber import router as update_cyber


load_dotenv()
app = FastAPI(
    title=os.getenv("API_TITLE"),
    description=os.getenv("API_DESCRIPTION"),
    version="1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(device_status_router, prefix="/v1", tags=["device"])
app.include_router(device_overview_router, prefix="/v1", tags=["device"])
app.include_router(device_scan_router, prefix="/v1", tags=["device"])
app.include_router(activities_router, prefix="/v1", tags=["device"])
app.include_router(simplify_device_router, prefix="/v1", tags=["device"])
app.include_router(results_router, prefix="/v1", tags=["device"])
app.include_router(removal_router, prefix="/v1", tags=["device"])
app.include_router(pull_data_router, prefix="/v1", tags=["device"])
app.include_router(check_update_router, prefix="/v1", tags=["ota-update"])
app.include_router(history_scan_router, prefix="/v1", tags=["history-scan"])
app.include_router(history_fullscan_router, prefix="/v1", tags=["history-scan"])
app.include_router(history_fastscan_router, prefix="/v1", tags=["history-scan"])
app.include_router(list_version, prefix="/v1", tags=["ota-update"])
app.include_router(is_rooted_device, prefix="/v1", tags=["device"])
app.include_router(removal_progress, prefix="/v1", tags=["device"])
app.include_router(package, prefix="/v1",tags=["device"])
app.include_router(result_fastscan,prefix="/v1",tags=["device"] )
app.include_router(check_update_app,prefix="/v1",tags=["ota-update"])
app.include_router(update_cyber,prefix="/v1",tags=["ota-update"])

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", include_in_schema=False)
async def root_redirect():
    return RedirectResponse(url="/docs")