from fastapi import APIRouter, HTTPException
import subprocess
import re
import logging
import os
from dotenv import load_dotenv
from packaging import version

load_dotenv()

router = APIRouter()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_current_version_from_env_file():
    env_path = ".env"
    if not os.path.exists(env_path):
        raise FileNotFoundError("File .env tidak ditemukan.")
    
    with open(env_path, "r") as file:
        for line in file:
            if line.startswith("CURRENT_BEHAVIOURAL_VERSION="):
                value = line.split("=", 1)[1].strip().strip('"')
                return value
    
    raise ValueError("CURRENT_BEHAVIOURAL_VERSION tidak ditemukan dalam file .env.")

def get_mvt_version():
    try:
        result = subprocess.run(
            ["mvt-android", "version"],
            capture_output=True,
            text=True,
            check=True
        )
        output = result.stdout.strip()
        version_match = re.search(r"Version:\s*v?(\d+\.\d+\.\d+)", output)
        if not version_match:
            raise ValueError("Format versi tidak sesuai. Harap pastikan 'mvt-android version' menghasilkan output yang valid.")
        return version_match.group(1)  # Mengambil versi (misalnya, "2.6.0")
    except subprocess.CalledProcessError as e:
        error_message = e.stderr.strip() if e.stderr else "Unknown error"
        logger.error(f"Error menjalankan command 'mvt-android version': {error_message}")
        raise HTTPException(status_code=400, detail=f"Error menjalankan command 'mvt-android version': {error_message}")

def compare_versions(current_version: str, latest_version: str) -> bool:
    return version.parse(latest_version) > version.parse(current_version)

@router.post("/check-update-cyber", summary="Periksa Pembaruan Cyber Version", description="Endpoint ini memeriksa apakah ada versi baru dari `Behavioural Analysis`.")
async def check_update():
    try:
        current_version = get_current_version_from_env_file()
        logger.info(f"Versi saat ini (dari file .env): {current_version}")
        
        latest_version = get_mvt_version()
        logger.info(f"Versi terbaru: {latest_version}")
        
        update_available = compare_versions(current_version, latest_version)
        message = (
            f"BEHAVIOURAL ANALYSIS HAS NEW VERSION: {latest_version}"
            if update_available
            else "Your Behavioural Version Already up to date"
        )
        
        if update_available:
            update_env_file("CURRENT_BEHAVIOURAL_VERSION", latest_version)
            logger.info(f"File .env telah diperbarui dengan versi terbaru: {latest_version}")
        
        return {
            "current_cyber_version": current_version,
            "latest_cyber_version": latest_version,
            "update_available": update_available,
            "message": message,
        }
    except Exception as e:
        logger.error(f"Error saat memeriksa pembaruan: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error saat memeriksa pembaruan: {str(e)}")

def update_env_file(key: str, value: str):
    env_path = ".env"
    updated_lines = []
    key_found = False

    if os.path.exists(env_path):
        with open(env_path, "r") as file:
            for line in file:
                if line.startswith(f"{key}="):
                    updated_lines.append(f'{key}="{value}"\n')
                    key_found = True
                else:
                    updated_lines.append(line)

    if not key_found:
        updated_lines.append(f'{key}="{value}"\n')

    with open(env_path, "w") as file:
        file.writelines(updated_lines)