import json
import os
import logging
from pathlib import Path
from fastapi import APIRouter, HTTPException, Path as FastAPIPath
from dotenv import load_dotenv

# Inisialisasi router FastAPI
router = APIRouter()

# Load environment variables
load_dotenv()

# Konfigurasi logging
log_level = logging.DEBUG if os.getenv("ENVIRONMENT", "development") == "development" else logging.INFO
logging.basicConfig(level=log_level)
logger = logging.getLogger(__name__)

# Mendapatkan BASE_SCAN_PATH dari environment variable
BASE_SCAN_PATH = Path(os.path.expanduser(os.getenv("BASE_SCAN_PATH", "")))

@router.get("/history_full_scan/{serial_number}/{time_stamp}")
async def get_history_full_scan(
    serial_number: str = FastAPIPath(..., description="Nomor seri perangkat"),
    time_stamp: str = FastAPIPath(..., description="Timestamp pemindaian")
):
    """
    Endpoint untuk mendapatkan hasil pemindaian penuh (full scan) berdasarkan serial_number dan time_stamp.
    """
    # Memeriksa apakah BASE_SCAN_PATH ada
    if not BASE_SCAN_PATH.exists():
        raise HTTPException(status_code=404, detail="Base scan path tidak ditemukan")

    # Membangun path ke file detail_result.json
    file_path = BASE_SCAN_PATH / "full-scan" / serial_number / time_stamp / "detail_result.json"

    # Memeriksa apakah file detail_result.json ada
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File detail_result.json tidak ditemukan")

    try:
        # Membaca isi file JSON
        with open(file_path, "r") as file:
            data = json.load(file)
        
        return data

    except Exception as e:
        # Logging error jika terjadi kesalahan saat membaca file
        logger.error(f"Terjadi kesalahan saat membaca file detail_result.json: {e}")
        raise HTTPException(status_code=500, detail="Terjadi kesalahan server saat memproses permintaan")