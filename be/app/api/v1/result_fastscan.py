from datetime import datetime
from fastapi import APIRouter, HTTPException
from typing import Dict, List
import json
import logging
import os
from pathlib import Path
import subprocess
import re


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

def get_latest_scan_directory(base_path: str) -> str:
    try:
        directories = [
            d for d in os.listdir(base_path)
            if os.path.isdir(os.path.join(base_path, d))
        ]
        if not directories:
            raise FileNotFoundError(f"Tidak ada direktori scan ditemukan di {base_path}")
        latest_directory = max(
            directories, key=lambda x: os.path.getmtime(os.path.join(base_path, x))
        )
        return os.path.join(base_path, latest_directory)
    except Exception as e:
        logger.error(f"Error saat mencari direktori terbaru: {e}")
        raise

@router.get("/result-fastscan", response_model=Dict)
async def get_result_fastscan(serial_number: str):
    try:
        # Ambil BASE_SCAN_PATH dari environment variable
        base_scan_path = os.path.expanduser(os.getenv("BASE_SCAN_PATH", "/default/path"))
        # Gunakan path BASE_SCAN_PATH/fast-scan/{serial_number}
        base_path = os.path.join(base_scan_path, "fast-scan", serial_number)
        
        # Cari direktori scan terbaru berdasarkan time_stamp dengan format DDMMYYYY_HHMMSS
        latest_scan_directory = get_latest_scan_directory(base_path)
        
        # Baca file detail_result.json dari direktori terbaru
        detail_result_path = os.path.join(latest_scan_directory, "detail_result.json")
        if not os.path.exists(detail_result_path):
            raise FileNotFoundError(f"File detail_result.json tidak ditemukan di {latest_scan_directory}")
        
        with open(detail_result_path, "r") as file:
            result_data = json.load(file)
        
        response = {
            "message": "Get fast-scan result successfully",
            "status": "success",
            "data": result_data
        }
        return response

    except FileNotFoundError as e:
        logger.error(f"Direktori atau file tidak ditemukan: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error saat mendapatkan hasil pemindaian cepat: {e}")
        raise HTTPException(status_code=500, detail=str(e))