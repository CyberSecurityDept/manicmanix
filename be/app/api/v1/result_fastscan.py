import os
import json
import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pathlib import Path
from typing import Dict, List
from dotenv import load_dotenv
from app.services.results_service import ResultService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
router = APIRouter()
load_dotenv()

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

def read_dumpsys_activities_detected(scan_directory: Path) -> List[Dict]:
    dumpsys_file = scan_directory / "dumpsys_activities_detected.json"
    activities_detected = []
    if dumpsys_file.exists():
        try:
            with open(dumpsys_file, "r") as file:
                activities_detected = json.load(file)
                activities_detected = [
                    entry for entry in activities_detected
                    if entry.get("matched_indicator", {}).get("type") == "app_ids"
                ]
                logger.info(f"Berhasil membaca dan memfilter {dumpsys_file}")
        except json.JSONDecodeError as e:
            logger.error(f"File {dumpsys_file} tidak valid: {e}")
        except Exception as e:
            logger.error(f"Error membaca file {dumpsys_file}: {e}")
    else:
        logger.warning(f"File {dumpsys_file} tidak ditemukan.")
    return activities_detected

def count_scanned_applications(installed_apps_path: Path) -> int:
    if installed_apps_path.exists():
        scanned = len([folder for folder in installed_apps_path.iterdir() if folder.is_dir()])
        logger.info(f"Total applications scanned: {scanned}")
        return scanned
    return 0

@router.get("/result-fastscan", response_model=Dict)
async def get_result_fastscan(serial_number: str):
    try:
        scan_type = "fast-scan"
        base_path = Path(os.path.expanduser(f"{str(os.getenv('BASE_SCAN_PATH'))}")) / scan_type / serial_number
        latest_scan_directory = get_latest_scan_directory(base_path)
        
        # Read dumpsys activities
        activities_detected = read_dumpsys_activities_detected(latest_scan_directory)
        
        # Get phone model and security patch date
        phone_model = ResultService.get_phone_model(serial_number)
        security_patch_date = ResultService.get_security_patch_date(serial_number)
        
        # Count scanned applications
        base_path_media = os.getenv('MEDIA_ISOLATED_PATH')
        installed_apps_path = Path(base_path_media) / f"{serial_number}" / "installed_apps"
        total_scanned = count_scanned_applications(installed_apps_path)
        
        # Get previous scan result for last_scan_percentage
        try:
            previous_detail_result = latest_scan_directory / "detail_result.json"
            with open(previous_detail_result, "r") as file:
                data = json.load(file)
                last_scan_percentage = data.get("security_percentage", "0") + "%"
        except:
            last_scan_percentage = "0%"
        
        # Calculate security percentage (100 / (1 + number_of_threats))
        number_of_threats = len(activities_detected)
        security_percentage = f"{(100 / (1 + number_of_threats)):.2f}"
        
        # Create threats list from dumpsys activities
        threats = []
        current_time = datetime.now().isoformat()
        
        for activity in activities_detected:
            threat = {
                "name": activity.get("activity", "unknown"),
                "package_name": activity.get("package_name", "unknown"),
                "date_time": current_time,
                "type": "Application"
            }
            threats.append(threat)
        
        # Create scan overview
        scan_overview = {
            "applications": {
                "scanned": total_scanned,
                "threats": len(threats)
            },
            "documents": {
                "scanned": 0,
                "threats": 0
            },
            "media": {
                "scanned": 0,
                "threats": 0
            },
            "installer": {
                "scanned": 0,
                "threats": 0
            }
        }
        
        # Prepare result data
        result_data = {
            "security_percentage": security_percentage,
            "last_scan_percentage": last_scan_percentage,
            "phone_model": phone_model,
            "security_patch_date": security_patch_date,
            "scan_overview": scan_overview,
            "total_threats": len(threats),
            "threats": threats
        }
        
        # Save result to file
        output_file_main = latest_scan_directory / f"{scan_type}_result.json"
        with open(output_file_main, "w") as file:
            json.dump(result_data, file, indent=4)
        logger.info(f"Hasil scan utama disimpan ke {output_file_main}")
        
        response = {
            "message": "Get result successfully",
            "status": "success",
            "data": result_data
        }
        return response
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error pada endpoint /result-fastscan: {e}")
        raise HTTPException(status_code=500, detail=str(e))