import logging
import os
import subprocess
from fastapi import APIRouter, HTTPException
from app.repositories.list_version_repository import (
    get_gitlab_app_version,
    get_mvt_version,
    update_app_version,
    update_cyber_version,
    save_versions,
    compare_versions,
)
from app.schemas.schemas import UpdateVersionRequest
from dotenv import load_dotenv


load_dotenv()


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router = APIRouter()

def get_current_app_version():
    return os.getenv("CURRENT_APP_VERSION", "v1.0.0")

def run_git_pull():
    try:
        result = subprocess.run(
            ["git", "pull"],
            capture_output=True,
            text=True,
            check=True
        )
        logger.info(f"Git pull berhasil: {result.stdout.strip()}")
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        error_message = e.stderr.strip() if e.stderr else "Unknown error"
        logger.error(f"Error saat menjalankan 'git pull': {error_message}")
        raise HTTPException(status_code=400, detail=f"Error saat menjalankan 'git pull': {error_message}")

def get_latest_local_tag():
    try:
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            capture_output=True,
            text=True,
            check=True
        )
        latest_tag = result.stdout.strip()
        logger.info(f"Tag terbaru dari repositori lokal: {latest_tag}")
        return latest_tag
    except subprocess.CalledProcessError as e:
        error_message = e.stderr.strip() if e.stderr else "Unknown error"
        logger.error(f"Error saat mendapatkan tag terbaru: {error_message}")
        raise HTTPException(status_code=400, detail=f"Error saat mendapatkan tag terbaru: {error_message}")

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

@router.get("/list-version", summary="Get current app and cyber versions")
def list_version():
    try:
        app_versions = get_gitlab_app_version()
        cyber_versions = get_mvt_version()

        response = {
            "status": 200,
            "message": "Get version successfully",
            "data": {
                "app_versions": app_versions,
                "cyber_versions": cyber_versions,
            },
        }
        return response
    except Exception as e:
        logger.error(f"Error saat mendapatkan versi: {e}")
        raise HTTPException(status_code=500, detail=f"Error saat mendapatkan versi: {str(e)}")

@router.post("/update-app")
async def check_update_app():
    try:
        current_version = get_current_app_version()
        logger.info(f"Versi aplikasi saat ini: {current_version}")
        pull_output = run_git_pull()
        latest_version_tag = get_latest_local_tag()
        
        if latest_version_tag != current_version:
            
            update_env_file("CURRENT_APP_VERSION", latest_version_tag)
            logger.info(f"File .env telah diperbarui dengan versi terbaru: {latest_version_tag}")

            message = "updated app successfully."
            download_output = "pull tag success"
            updated_version = latest_version_tag
        else:
            message = "Application is already up to date."
            download_output = "No new tags to pull."
            updated_version = current_version

        return {
            "message": message,
            "updated_version": updated_version,
            "download_output": download_output,
            "latest_version_tag": latest_version_tag,
        }
    except Exception as e:
        logger.error(f"Error saat memeriksa pembaruan aplikasi: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error saat memeriksa pembaruan aplikasi: {str(e)}")