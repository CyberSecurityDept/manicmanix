from datetime import datetime
import os
import json
import logging
from pathlib import Path
from typing import List, Dict
from app.api.v1.device_scan import run_device_scan

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_SCAN_PATH = Path(os.getenv("BASE_SCAN_PATH", "/default/path"))
os.makedirs(BASE_SCAN_PATH, exist_ok=True)

def read_dumpsys_activities(output_dir: str) -> List[Dict]:
    try:
        dumpsys_file = os.path.join(output_dir, "dumpsys_activities_detected.json")
        if not os.path.exists(dumpsys_file):
            logger.warning(f"File dumpsys_activities_detected.json tidak ditemukan di {output_dir}.")
            return []
        with open(dumpsys_file, "r") as f:
            activities = json.load(f)
            if not isinstance(activities, list):
                logger.error("Format dumpsys_activities_detected.json tidak valid.")
                return []
            return activities
    except Exception as e:
        logger.error(f"Gagal membaca dumpsys_activities_detected.json: {e}")
        return []

def calculate_security_percentage_from_activities(activities: List[Dict]) -> str:
    total_activities = len(activities)
    suspicious_activities = sum(
        1 for activity in activities if activity.get("matched_indicator", {}).get("type") == "app_ids"
    )
    if total_activities == 0:
        return "98.00%"
    security_percentage = max(0, 100 - (suspicious_activities / total_activities * 100))
    if suspicious_activities == 0:
        return "98.00%"
    return f"{security_percentage:.2f}%"

def create_fast_scan_detail_result(output_dir: Path, scan_data: dict):
    detail_result_path = output_dir / "detail_result.json"
    with open(detail_result_path, "w") as f:
        json.dump(scan_data, f, indent=4)
    logger.info(f"Created detail_result.json at: {detail_result_path}")

def background_fast_scan(output_dir: str, serial_number: str, scan_id: str, initial_data: dict):
    try:
        logger.info(f"Starting fast scan for device {serial_number} with scan_id {scan_id}...")
        
        # Jalankan pemindaian perangkat
        run_device_scan(output_dir)
        logger.info(f"Fast scan finished for device {serial_number}.")
        
        # Baca aktivitas dari file dumpsys
        activities = read_dumpsys_activities(output_dir)
        logger.info(f"Menemukan {len(activities)} aktivitas terdeteksi.")
        
        # Hitung persentase keamanan
        new_security_percentage = calculate_security_percentage_from_activities(activities)
        logger.info(f"Calculated security_percentage: {new_security_percentage}")
        
        # Ambil time_stamp dari initial_data atau dari nama folder
        folder_name = Path(output_dir).name  # Nama folder = current_time
        time_stamp = initial_data.get("time_stamp", folder_name)
        
        # Siapkan data untuk file detail_result.json sesuai model output
        updated_data = {
            "no": initial_data.get("no"),
            "scan_id": scan_id,
            "serial_number": serial_number,
            "time_stamp": time_stamp,  # pastikan time_stamp sesuai dengan nama folder
            "name": initial_data.get("name", ""),
            "model": initial_data.get("model", ""),
            "imei1": initial_data.get("imei1", ""),
            "imei2": initial_data.get("imei2", ""),
            "security_patch": initial_data.get("security_patch", ""),
            "last_scan": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "security_percentage": new_security_percentage,
            "scan_type": "fast-scan",
            "status": "started"
        }
        
        # Pastikan direktori output ada dan buat file detail_result.json
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        create_fast_scan_detail_result(Path(output_dir), updated_data)
        logger.info("Fast scan detail result created.")
        
        # Update nilai security_percentage di history_scan.json
        history_scan_path = BASE_SCAN_PATH / "history_scan.json"
        if history_scan_path.exists():
            with open(history_scan_path, "r") as f:
                history_entries = json.load(f)
            for entry in history_entries:
                if entry.get("scan_id") == scan_id:
                    entry["security_percentage"] = new_security_percentage
                    entry["last_scan"] = updated_data["last_scan"]
                    break
            with open(history_scan_path, "w") as f:
                json.dump(history_entries, f, indent=4)
        else:
            logger.warning("history_scan.json tidak ditemukan untuk diupdate.")
    
    except Exception as e:
        logger.error(f"Error during fast scan for device {serial_number}: {e}")
        
        # Jika terjadi error, buat file detail_result.json dengan status "failed"
        error_data = {
            "no": initial_data.get("no", 0),
            "scan_id": scan_id,
            "serial_number": serial_number,
            "time_stamp": initial_data.get("time_stamp", Path(output_dir).name),
            "name": initial_data.get("name", ""),
            "model": initial_data.get("model", ""),
            "imei1": initial_data.get("imei1", ""),
            "imei2": initial_data.get("imei2", ""),
            "security_patch": initial_data.get("security_patch", ""),
            "last_scan": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "security_percentage": "0.00%",
            "scan_type": "fast-scan",
            "status": "failed",
            "error": str(e),
            "failed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        create_fast_scan_detail_result(Path(output_dir), error_data)
        raise
