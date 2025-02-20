import logging
import subprocess
from datetime import datetime
from typing import Dict
from app.repositories.risk_repository import RiskRepository
from app.repositories.result_scan_overview_repository import ResultScanOverviewRepository

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
                
    @staticmethod
    def generate_result(serial_number: str, task_results: list) -> Dict:
        try:
            security_percentage = RiskRepository.calculate_security_percentage(task_results)
            scan_overview_result = ResultScanOverviewRepository.generate_scan_overview(task_results)
            security_patch_date = ResultService.get_security_patch_date(serial_number)
            phone_model = ResultService.get_phone_model(serial_number)
            total_threats = 0
            for category in scan_overview_result["scan_overview"].values():
                total_threats += category["threats"]

            result = {
                "security_percentage": security_percentage.replace("%", ""),
                "last_scan_percentage": 89,
                "phone_model": phone_model,
                "security_patch_date": security_patch_date,
                "scan_overview": scan_overview_result["scan_overview"],
                "total_threats": total_threats,
                "threats": scan_overview_result["threats"]
            }

            return result
        except Exception as e:
            raise RuntimeError(f"Gagal generate hasil pemindaian: {e}")