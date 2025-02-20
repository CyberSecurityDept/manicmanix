import os
import json
import subprocess
from app.utils.config import PROJECT_ROOT
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_device_id() -> str:
    result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
    lines = result.stdout.splitlines()
    for line in lines[1:]:
        parts = line.split()
        if len(parts) >= 2 and parts[1] == "device":
            return parts[0]
    return None

def find_dumpsys_file(serial_number: str) -> str:
    base_path = os.path.join(PROJECT_ROOT, "output-scan", "full-scan", serial_number)
    logger.info(f"Mencari file dumpsys_activities_detected.json di: {base_path}")
    
    # Cari file secara rekursif
    for root, dirs, files in os.walk(base_path):
        if "dumpsys_activities_detected.json" in files:
            return os.path.join(root, "dumpsys_activities_detected.json")
    
    logger.error(f"File dumpsys_activities_detected.json tidak ditemukan di: {base_path}")
    return None

def delete_malware_by_package_names(serial_number: str, package_names: list) -> dict:
    try:
        logger.info("Fetching device ID...")
        device_id = get_device_id()
        if not device_id:
            logger.error("No connected device found.")
            return {"status": "error", "message": "No connected device found via ADB."}
        
        logger.info(f"Device ID: {device_id}")
        dumpsys_file_path = find_dumpsys_file(serial_number)
        if not dumpsys_file_path:
            logger.error(f"File dumpsys_activities_detected.json tidak ditemukan.")
            return {
                "status": "error",
                "message": "File dumpsys_activities_detected.json tidak ditemukan.",
            }
        
        # Load JSON
        logger.info("Loading JSON data...")
        with open(dumpsys_file_path, "r") as file:
            data = json.load(file)
        
        deleted_packages = []
        not_found_packages = []
        for package_name in package_names:
            logger.info(f"Searching for package: {package_name}")
            if package_name in data:
                # Delete the package entry
                logger.info(f"Deleting package: {package_name}")
                del data[package_name]
                deleted_packages.append(package_name)
            else:
                logger.warning(f"Package '{package_name}' not found.")
                not_found_packages.append(package_name)
        
        # Save updated JSON if any packages were deleted
        if deleted_packages:
            logger.info("Saving updated JSON...")
            with open(dumpsys_file_path, "w") as file:
                json.dump(data, file, indent=4)
            logger.info(f"Packages {deleted_packages} successfully deleted.")
            return {
                "status": "success",
                "message": f"Packages {deleted_packages} successfully deleted.",
                "not_found": not_found_packages,
            }
        else:
            logger.warning("No packages were deleted.")
            return {
                "status": "error",
                "message": "No packages were deleted.",
                "not_found": not_found_packages,
            }
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON: {e}")
        return {"status": "error", "message": f"Failed to parse JSON: {e}"}
    except Exception as e:
        logger.exception(f"An error occurred: {e}")
        return {"status": "error", "message": f"An error occurred: {e}"}