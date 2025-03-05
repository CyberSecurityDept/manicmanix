import asyncio
import shutil
import aiohttp
import os
import logging
import json
import time
import re
import requests
import aiohttp
import httpx
import subprocess
import os
import logging

from dotenv import load_dotenv
from pathlib import Path
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from datetime import datetime
from pydantic import BaseModel
from typing import List, Dict, Optional
from app.repositories.risk_repository import RiskRepository

router = APIRouter()
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_SCAN_PATH = Path(os.path.expanduser(f"{str(os.getenv('BASE_SCAN_PATH'))}"))
os.makedirs(BASE_SCAN_PATH, exist_ok=True)

def get_latest_scan_directory(base_path: Path) -> Path:
    try:
        directories = [d for d in base_path.iterdir() if d.is_dir()]
        if not directories:
            raise FileNotFoundError(f"Tidak ada direktori scan ditemukan di {base_path}")
        latest_directory = max(directories, key=lambda x: x.stat().st_mtime)
        logger.info(f"Direktori scan terbaru ditemukan: {latest_directory}")
        return latest_directory
    except Exception as e:
        logger.error(f"Error saat mencari direktori terbaru: {e}")
        raise


@router.get("/calculate-risk/{serial_number}")
async def calculate_risk(serial_number: str):
    try:
        scan_type = "full-scan"
        base_dir = Path(os.path.expanduser(f"{str(os.getenv('BASE_SCAN_PATH'))}")) / scan_type / serial_number
        latest_scan_directory = get_latest_scan_directory(base_dir)

        logger.info(f"Memeriksa direktori: {latest_scan_directory}")

        if not os.path.exists(latest_scan_directory):
            raise FileNotFoundError(f"Direktori {latest_scan_directory} tidak ditemukan")

        task_result_dir = os.path.join(latest_scan_directory, "task_result")
        if not os.path.exists(task_result_dir):
            raise HTTPException(status_code=404, detail="Direktori 'task_result' tidak ditemukan")

        if not os.listdir(task_result_dir):
            raise HTTPException(status_code=404, detail="Direktori 'task_result' kosong")

        task_results = RiskRepository.read_task_results(task_result_dir)

        if not task_results:
            raise HTTPException(status_code=404, detail="Tidak ada data yang valid di 'task_result'")

        malware_risks = RiskRepository.calculate_malware_risk_percentage(task_results)
        security_percentage = RiskRepository.calculate_security_percentage(task_results)
        apk_metadata = RiskRepository.extract_apk_metadata(task_results)
        antivirus_results = RiskRepository.extract_antivirus_results(task_results)

        return {
            "serial_number": serial_number,
            "malware_risks": malware_risks,
            "security_percentage": security_percentage,
            "apk_metadata": apk_metadata,
            "antivirus_results": antivirus_results
        }
    except FileNotFoundError as e:
        logger.error(f"FileNotFoundError: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException as e:
        logger.error(f"HTTPException: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Exception: {e}")
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan: {str(e)}")