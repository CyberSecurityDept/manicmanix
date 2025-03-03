import json
import os
from typing import Dict, List
import logging
from datetime import datetime
import sys
project_directory = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_directory)
from data_pulling_repository import Data_Pulling

# Konfigurasi logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Kategori file berdasarkan ekstensi
FILE_CATEGORIES = {
    'archive': ['zip', 'rar', '7z', 'tar', 'gz', 'bz2', 'xz', 'iso', 'tgz', 'tbz2', 'lzma', 'cab', 'z', 'lz', 'lzo'],
    'installer': ['exe', 'msi', 'dmg', 'app', 'apk'],
    'documents': ["pdf", "doc", "docx", "xls", "xlsx", "txt"],
    'media': ["mov", "avi", "mp4", "mp3", "mpeg", "jpg", "jpeg", "png", "svg", "gif", "webp", "mkv", "wav", "ogg", "wmv"]
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
            # Mendapatkan device serials
            device_serials = Data_Pulling.get_device_serials()
            if not device_serials:
                logger.warning("Device serials tidak ditemukan.")
                return scan_overview
        except Exception as e:
            logger.error(f"Error saat mendapatkan device serials: {e}")
            return scan_overview
        
        # Mendapatkan path media isolated
        media_isolated_path = os.getenv('MEDIA_ISOLATED_PATH')
        if not media_isolated_path:
            logger.error("MEDIA_ISOLATED_PATH tidak diatur dalam variabel lingkungan.")
            return scan_overview
        
        media_category = os.path.join(media_isolated_path, device_serials[0], "media")
        base_path = os.path.join(media_isolated_path, device_serials[0], 'installer')
        if not os.path.exists(media_category):
            logger.warning(f"Path media {media_category} tidak ditemukan.")
            return scan_overview
        
        try:
            # Membaca file di direktori media
            file_in_media = set(os.listdir(media_category))
        except Exception as e:
            logger.error(f"Error saat membaca direktori media {media_category}: {e}")
            return scan_overview
        
        # Menghitung file media yang ada di direktori media_category
        for file_name in file_in_media:
            file_extension = file_name.split(".")[-1].lower() if "." in file_name else ""
            print(file_name, 'media masuk')
            if file_extension in FILE_CATEGORIES['media']:
                scan_overview["scan_overview"]["media"]["scanned"] += 1
        
        # Memproses hasil pemindaian
        for result in task_results:
            try:
                names = result["result"]["response"]["data"]["attributes"]["names"]
                print(names, 'masukkkk')
                if not names:
                    logger.warning("Tidak ada nama file dalam hasil pemindaian.")
                    continue
                
                attributes = result.get("result", {}).get("response", {}).get("data", {}).get("attributes", {})
                stats = attributes.get("last_analysis_stats", {})
                is_malicious = stats.get("malicious", 0) > 0
                for file_name in names:
                    file_extension = file_name.split(".")[-1].lower() if "." in file_name else ""
                    file_category = None
                    # Menentukan kategori file
                    for category, extensions in FILE_CATEGORIES.items():
                        if file_extension in extensions:
                            file_category = category
                            break
                    if file_category is None:
                        if any(file_name.lower().endswith(f".{ext}") for ext in FILE_CATEGORIES['archive']):
                            file_category = 'archive'
                        elif any(file_name.lower().endswith(f".{ext}") for ext in FILE_CATEGORIES['installer']):
                            file_category = 'installer'
                        elif any(file_name.lower().endswith(f".{ext}") for ext in FILE_CATEGORIES['documents']):
                            file_category = 'documents'
                        elif any(file_name.lower().endswith(f".{ext}") for ext in FILE_CATEGORIES['media']):
                            file_category = 'media'
                    # Menambahkan jumlah file yang discan
                    if file_category:
                        scan_overview["scan_overview"][file_category]["scanned"] += 1
                        print(file_name, 'sama harusnya')
                    else:
                        logger.error(f"File {file_name} tidak memiliki kategori yang dikenali")
                    
                    # Jika file malicious, tambahkan ke ancaman
                    
                    if is_malicious:
                        scan_overview["scan_overview"][file_category]["threats"] += 1
                        
                        # Menentukan source_path dari isolated.json
                        try:
                            device_serials = Data_Pulling.get_device_serials()
                            device = device_serials[0]
                            isolated_data = Data_Pulling.get_isolated_data(device)
                            source_path = None
                            
                            # Cari path berdasarkan file_category atau file_name
                            if file_category in isolated_data:
                                category_data = isolated_data[file_category]
                                for item in category_data:
                                    # Normalisasi nama file untuk memastikan case-insensitive
                                    if item["name"].lower() == file_name.lower():
                                        source_path = item.get("local_path", None)
                                        print(f"Match found: {file_name} -> {source_path}")
                                        break
                            
                            # Jika tidak ditemukan, gunakan fallback path
                            if source_path is None:
                                source_path = "unknown"
                                print(f"Fallback path used for {file_name}: {source_path}")

                        except FileNotFoundError as e:
                            print(f"File tidak ditemukan: {e}")
                        except ValueError as e:
                            print(f"Error: {e}")
                        except Exception as e:
                            print(f"Error tak terduga saat membaca isolated.json: {e}")

                        # Tambahkan ancaman ke daftar threats
                        scan_overview["threats"].append({
                            "name": file_name,
                            "package_name": file_name.split(".")[0] if "." in file_name else "",
                            "date_time": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                            "type": file_category.capitalize(),
                            "source_path": source_path
                        })
            except Exception as e:
                logger.error(f"Error memproses hasil pemindaian untuk file {names[0] if names else 'unknown'}: {e}")
                continue
        
        return scan_overview