from typing import List
from app.repositories.removal_progress_repository import delete_malware_by_package_names
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def calculate_removal_progress(serial_number: str, package_names: List[str], threshold: int) -> dict:
    try:
        # Panggil repository untuk menghapus paket
        result = delete_malware_by_package_names(serial_number, package_names)
        
        # Ekstrak hasil
        deleted_packages = result.get("message", "").split(":")[-1].strip()
        not_found_packages = result.get("not_found", [])
        total_packages = len(package_names)
        deleted_count = len(deleted_packages.split(", ")) if deleted_packages else 0
        
        # Hitung persentase kemajuan
        progress_percentage = (deleted_count / total_packages) * 100 if total_packages > 0 else 0
        
        # Evaluasi hasil berdasarkan threshold
        if progress_percentage >= threshold:
            return {
                "status": "success",
                "message": f"Penghapusan berhasil dengan progress {progress_percentage:.2f}%",
                "data": {
                    "total_packages": total_packages,
                    "packages_removed": deleted_count,
                    "progress_percentage": progress_percentage,
                    "threshold": threshold,
                    "packages_failed": not_found_packages,
                },
            }
        else:
            return {
                "status": "failed",
                "message": f"Penghapusan gagal dengan progress {progress_percentage:.2f}%",
                "data": {
                    "total_packages": total_packages,
                    "packages_removed": deleted_count,
                    "progress_percentage": progress_percentage,
                    "threshold": threshold,
                    "packages_failed": not_found_packages,
                },
            }
    except ValueError as e:
        raise ValueError(str(e))
    except Exception as e:
        raise Exception(str(e))