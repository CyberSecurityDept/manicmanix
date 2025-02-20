
import json
import os
import logging
import aiohttp
from pathlib import Path
from fastapi import APIRouter, HTTPException
from async_lru import alru_cache
from dotenv import load_dotenv

# Import service yang sudah kamu buat (pastikan path impor sudah benar)
from app.services.device_overview_service import DeviceOverviewService
from app.repositories.risk_repository import RiskRepository

router = APIRouter()    


load_dotenv()
BASE_SCAN_PATH = Path(os.path.expanduser(f"{str(os.getenv('BASE_SCAN_PATH'))}"))


@staticmethod
def read_history():
    BASE_SCAN_PATH = Path(os.path.expanduser(f"{str(os.getenv('BASE_SCAN_PATH'))}"))
    if BASE_SCAN_PATH.exists:
        history_file = str(os.getenv('HISTORY_FILE'))
        with open(history_file, "r") as file:
            data = json.load(file)
            print(data)

# Konfigurasi logging
log_level = logging.DEBUG if os.getenv("ENVIRONMENT", "development") == "development" else logging.INFO
logging.basicConfig(level=log_level)
logger = logging.getLogger(__name__)

CACHE_MAXSIZE = 128
TIMEOUT_SECONDS = 10

@router.get("/history-scan")
async def get_history():
    load_dotenv()
    base_scan_path = Path(os.path.expanduser(os.getenv("BASE_SCAN_PATH", "")))

    if not base_scan_path.exists():
        raise HTTPException(status_code=404, detail="output folder tidak ditemukan")
    
    history_file = str(os.path.expanduser(os.getenv("HISTORY_FILE")))
    if not history_file or not os.path.exists(history_file):
        raise HTTPException(status_code=404,  detail="File History tidak ditemukan")
    
    try:
        with open(history_file, "r") as file:
            data = json.load(file)
        return data
    
    except Exception as e:
        logging.error(f"Terjadi kesalahan saat membaca file history: {e}")
        raise HTTPException(status_code=500, detail="")

