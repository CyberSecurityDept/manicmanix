import json
import os
import logging
import subprocess
from datetime import datetime
from typing import Dict
from app.repositories.risk_repository import RiskRepository
from app.repositories.result_scan_overview_repository import ResultScanOverviewRepository
from pathlib import Path


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResultService:
    @staticmethod
    def get_phone_model(serial_number: str) -> str:
        try:
            command = f"adb -s {serial_number} shell getprop ro.product.model" 
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                phone_model = result.stdout.strip()
                return phone_model
            else:
                return "Unknown"
        except Exception as e:
            return "Unknown"

    @staticmethod
    def get_security_patch_date(serial_number: str) -> str:
        try:
            command = f"adb -s {serial_number} shell getprop ro.vendor.build.security_patch"
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                security_patch_date = result.stdout.strip()
                return security_patch_date
            else:
                return "Unknown"
        except Exception as e:
            return "Unknown"
        
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
                
    @staticmethod
    def generate_result(serial_number: str, task_results: list) -> Dict:
        try:
            scan_type = "full-scan"
            base_path = Path(os.path.expanduser(f"{str(os.getenv('BASE_SCAN_PATH'))}")) / scan_type / serial_number
            latest_scan_directory = ResultService.get_latest_scan_directory(base_path)
            previous_detail_result = latest_scan_directory / "detail_result.json"
            with open(previous_detail_result, "r") as file:
                data = json.load(file)
                last_scan_percentage = data["security_percentage"]
            security_percentage = RiskRepository.calculate_security_percentage(task_results)
            scan_overview_result = ResultScanOverviewRepository.generate_scan_overview(task_results)
            security_patch_date = ResultService.get_security_patch_date(serial_number)
            phone_model = ResultService.get_phone_model(serial_number)
            total_threats = 0
            for category in scan_overview_result["scan_overview"].values():
                total_threats += category["threats"]

            result = {
                "security_percentage": security_percentage.replace("%", ""),
                "last_scan_percentage": last_scan_percentage,
                "phone_model": phone_model,
                "security_patch_date": security_patch_date,
                "scan_overview": scan_overview_result["scan_overview"],
                "total_threats": total_threats,
                "threats": scan_overview_result["threats"]
            }

            return result
        except Exception as e:
            raise RuntimeError(f"Gagal generate hasil pemindaian: {e}")