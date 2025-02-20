import json
import os
from typing import Dict, List
import logging
from datetime import datetime
import subprocess
from app.repositories.data_pulling_repository import Data_Pulling

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

FILE_CATEGORIES = {
    'archive': ['zip', 'rar', '7z', 'tar', 'gz', 'bz2', 'xz', 'iso', 'tgz', 'tbz2', 'lzma', 'cab', 'z', 'lz', 'lzo'],
    'installer': ['exe', 'msi', 'dmg', 'app', 'apk'],
    'documents': ["pdf", "doc", "docx", "xls", "xlsx", "txt"],
    'media': ["mov", "avi", "mp4", "mp3", "mpeg", "jpg", "png", "svg", "gif", "webp", "mkv", "wav", "ogg", "wmv"]
}

class ResultScanOverviewRepository:
    @staticmethod
    def generate_scan_overview(task_results: List[Dict]) -> Dict:
        scan_overview = {
            "scan_overview": {
                "applications": {"scanned": 0, "threats": 0},
                "documents": {"scanned": 0, "threats": 0},
                "media": {"scanned": 0, "threats": 0},
                "installer": {"scanned": 0, "threats": 0}
            },
            "total_threats": 0,
            "threats": []
        }

        try:
            device_serials = Data_Pulling.get_device_serials()
            if not device_serials:
                logger.warning("Device serials tidak ditemukan.")
                return scan_overview
        except Exception as e:
            logger.error(f"Error saat mendapatkan device serials: {e}")
            return scan_overview

        
        media_isolated_path = os.getenv('MEDIA_ISOLATED_PATH')
        if not media_isolated_path:
            logger.error("MEDIA_ISOLATED_PATH tidak diatur dalam variabel lingkungan.")
            return scan_overview

        media_category = os.path.join(media_isolated_path, device_serials[0], "media")
        if not os.path.exists(media_category):
            logger.warning(f"Path media {media_category} tidak ditemukan.")
            return scan_overview

        
        try:
            file_in_media = set(os.listdir(media_category))
        except Exception as e:
            logger.error(f"Error saat membaca direktori media {media_category}: {e}")
            return scan_overview

        
        for result in task_results:
            try:
                # Ambil nama file dari atribut "names"
                names = result.get("data", {}).get("attributes", {}).get("names", [])
                if not names:
                    continue

                attributes = result.get("data", {}).get("attributes", {})
                stats = attributes.get("last_analysis_stats", {})
                is_malicious = stats.get("malicious", 0) > 0

                for file_name in names:
                    clean_file_name = file_name.strip().replace(" ", "_").replace("%20", "_")
                    file_extension = clean_file_name.split(".")[-1].lower() if "." in clean_file_name else ""
                    file_category = None
                    for category, extensions in FILE_CATEGORIES.items():
                        if file_extension in extensions:
                            file_category = category
                            break

                    if not file_category:
                        if any(clean_file_name.lower().endswith(ext) for ext in FILE_CATEGORIES['media']):
                            file_category = 'media'
                        elif any(clean_file_name.lower().endswith(ext) for ext in FILE_CATEGORIES['documents']):
                            file_category = 'documents'
                        elif any(clean_file_name.lower().endswith(ext) for ext in FILE_CATEGORIES['installer']):
                            file_category = 'installer'
                        else:
                            file_category = 'applications'
                    
                    scan_overview["scan_overview"][file_category]["scanned"] += 1
                    
                    if is_malicious:
                        scan_overview["scan_overview"][file_category]["threats"] += 1
                        scan_overview["total_threats"] += 1

                        name = clean_file_name
                        package_name = name.split(".")[0] if "." in name else ""

                        scan_overview["threats"].append({
                            "name": name,
                            "package_name": package_name,
                            "date_time": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                            "type": file_category.capitalize()
                        })
                    
                    if clean_file_name in file_in_media and file_category == "media":
                        scan_overview["scan_overview"][file_category]["scanned"] += 1
                        if is_malicious:
                            scan_overview["scan_overview"][file_category]["threats"] += 1
                            scan_overview["total_threats"] += 1
                            scan_overview["threats"].append({
                                "name": clean_file_name,
                                "package_name": "",
                                "date_time": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                                "type": file_category.capitalize()
                            })

            except Exception as e:
                logger.error(f"Error memproses hasil pemindaian untuk file {names[0] if names else 'unknown'}: {e}")
                continue
        
        try:
            media_files = set(os.listdir(media_category))
            media_extensions = set(FILE_CATEGORIES['media'])
            for file_name in media_files:
                file_extension = file_name.split(".")[-1].lower() if "." in file_name else ""
                if file_extension in media_extensions:
                    scan_overview["scan_overview"]["media"]["scanned"] += 1
        except Exception as e:
            logger.error(f"Error saat menghitung file media di isolated: {e}")

        return scan_overview