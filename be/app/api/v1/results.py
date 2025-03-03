import os
import json
import logging
import os
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pathlib import Path
from typing import Dict, List
from dotenv import load_dotenv
from app.services.results_service import ResultService
from app.repositories.risk_repository import RiskRepository
from app.repositories.result_scan_overview_repository import ResultScanOverviewRepository

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
                # Filter hanya entri dengan matched_indicator.type == "app_ids"
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

def count_scanned_and_threats(installed_apps_path: Path, dumpsys_data: List[Dict]) -> Dict:
    scanned = 0
    threats = 0
    if installed_apps_path.exists():
        scanned = len([folder for folder in installed_apps_path.iterdir() if folder.is_dir()])
        logger.info(f"Total applications scanned: {scanned}")
        installed_apps = {folder.name for folder in installed_apps_path.iterdir() if folder.is_dir()}
        for entry in dumpsys_data:
            package_name = entry.get("package_name", "")
            if package_name in installed_apps:
                threats += 1
                logger.info(f"Detected threat: {package_name}")
    return {"scanned": scanned, "threats": threats}

def count_scanned_and_threats_for_installer(installer_path: Path, dumpsys_data: List[Dict]) -> Dict:
    scanned = 0
    threats = 0
    if installer_path.exists():
        scanned = len([item for item in installer_path.iterdir() if item.is_file() or item.is_dir()])
        logger.info(f"Total installers scanned: {scanned}")
        installer_items = {item.name for item in installer_path.iterdir() if item.is_file() or item.is_dir()}
        for entry in dumpsys_data:
            package_name = entry.get("package_name", "")
            if package_name in installer_items:
                threats += 1
                logger.info(f"Detected threat in installer: {package_name}")
    return {"scanned": scanned, "threats": threats}

@router.get("/result-fullscan", response_model=Dict)
async def get_result(serial_number: str, scan_type: str = "full-scan"):
    try:
        if scan_type not in ["full-scan", "fast-scan"]:
            raise HTTPException(status_code=400, detail="Jenis scan tidak valid. Gunakan 'full-scan' atau 'fast-scan'.")

        base_path = Path(os.path.expanduser(f"{str(os.getenv('BASE_SCAN_PATH'))}")) / scan_type / serial_number
        latest_scan_directory = get_latest_scan_directory(base_path)
        task_result_path = latest_scan_directory / "task_result"
        task_results = RiskRepository.read_task_results(task_result_path)
        result_data = ResultService.generate_result(serial_number, task_results)

        if not isinstance(result_data, dict):
            raise ValueError("result_data harus berupa dictionary")
        if not isinstance(result_data.get("threats", []), list):
            raise ValueError("result_data['threats'] harus berupa list")

        # Proses dan perbaiki data threat
        updated_threats = []
        for threat in result_data.get("threats", []):
            package_name = threat.get("package_name", "")
            # Gantikan variabel 'name' yang tidak didefinisikan dengan nilai yang ada atau fallback ke package_name
            threat_name = threat.get("name", package_name)
            updated_threat = {
                "name": threat_name,
                "package_name": package_name,
                "date_time": threat.get("date_time", ""),
                "type": threat.get("type", ""),
                "source_path": threat.get("source_path")
            }
            logger.info(f"Processed threat: {updated_threat}")
            updated_threats.append(updated_threat)

        # Tambahkan threat dari file dumpsys_activities_detected.json
        activities_detected = read_dumpsys_activities_detected(latest_scan_directory)
        for activity in activities_detected:
            threat = {
                "name": activity.get("activity", "unknown"),
                "package_name": activity.get("package_name", "unknown"),
                "date_time": datetime.now().isoformat(),
                "type": "Application",
                "source_path": threat.get("source_path")
            }
            updated_threats.append(threat)

        # Update data threat dan total threats berdasarkan perhitungan terbaru
        result_data["threats"] = updated_threats
        result_data["total_threats"] = len(updated_threats)
        logger.info(f"Total threats detected: {result_data['total_threats']}")

        # Buat overview dengan nilai default, lalu update berdasarkan hasil scanning
        scan_overview = {
            "applications": {"scanned": 0, "threats": 0},
            "documents": {"scanned": 0, "threats": 0},
            "media": {"scanned": 0, "threats": 0},
            "installer": {"scanned": 0, "threats": 0}
        }

        base_path_media = os.getenv('MEDIA_ISOLATED_PATH')
        installed_apps_path = Path(base_path_media) / f"{serial_number}" / "installed_apps"
        applications_stats = count_scanned_and_threats(installed_apps_path, activities_detected)
        scan_overview["applications"]["scanned"] += applications_stats["scanned"]
        scan_overview["applications"]["threats"] += applications_stats["threats"]

        installer_path = Path(base_path_media) / f"{serial_number}" / "installer"
        installer_stats = count_scanned_and_threats_for_installer(installer_path, activities_detected)
        scan_overview["installer"]["scanned"] = result_data["scan_overview"]["installer"]["scanned"]
        scan_overview["installer"]["threats"] = result_data["scan_overview"]["installer"]["threats"]
        
        scan_overview["documents"]["scanned"] = result_data["scan_overview"]["documents"]["scanned"]
        scan_overview["documents"]["threats"] = result_data["scan_overview"]["documents"]["threats"]
        
        scan_overview["media"]["scanned"] = result_data["scan_overview"]["media"]["scanned"]
        scan_overview["media"]["threats"] = result_data["scan_overview"]["media"]["threats"]

        # Update scan_overview tanpa mengubah total_threats dan threats yang sudah dihitung
        result_data["scan_overview"] = scan_overview

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
        logger.error(f"Error pada endpoint /result-fullscan: {e}")
        raise HTTPException(status_code=500, detail=str(e))