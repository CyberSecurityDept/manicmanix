import logging
import os
import subprocess
import requests
import re
from datetime import datetime
from fastapi import APIRouter, HTTPException
from app.repositories.list_version_repository import (
    get_gitlab_app_version,
    get_mvt_version,
)
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

def get_current_app_version():
    return os.getenv("CURRENT_APP_VERSION")

def validate_tag(tag_name: str):
    """
    Memvalidasi format tag (misalnya, vX.Y.Z).
    """
    if not re.match(r"^v\d+\.\d+\.\d+$", tag_name):
        raise ValueError(f"Format tag tidak valid: {tag_name}")

def checkout_latest_tag(tag_name: str):
    try:
        validate_tag(tag_name)
        logger.info("Memastikan semua tag tersedia di repositori lokal...")
        subprocess.run(["git", "fetch", "--tags"], check=True)
        logger.info(f"Checkout ke tag '{tag_name}'...")
        result = subprocess.run(
            ["git", "checkout", tag_name],
            capture_output=True,
            text=True,
            check=True
        )
        logger.info(f"Checkout berhasil: {result.stdout.strip()}")
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        error_message = e.stderr.strip() if e.stderr else "Unknown error"
        logger.error(f"Error Git: {error_message}")
        raise HTTPException(status_code=400, detail=f"Error Git: {error_message}")

def get_latest_remote_tag_api(owner: str, repo: str):
    try:
        url = f"https://api.github.com/repos/{owner}/{repo}/tags"
        github_token = os.getenv("GITHUB_TOKEN_APP")
        if not github_token:
            raise ValueError("GITHUB_TOKEN_APP tidak ditemukan di environment variables.")
        
        headers = {"Authorization": f"token {github_token}"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        tags = response.json()
        if not tags:
            raise ValueError("Tidak ada tag yang ditemukan di repositori GitHub.")
        
        latest_tag = tags[0]["name"]
        logger.info(f"Tag terbaru dari GitHub: {latest_tag}")
        return latest_tag
    except requests.RequestException as e:
        logger.error(f"Error jaringan saat mengambil tag dari GitHub: {str(e)}")
        raise HTTPException(status_code=503, detail="Service Unavailable: Gagal menghubungi GitHub.")

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
        return {
            "status": 200,
            "message": "Get version successfully",
            "data": {
                "app_versions": app_versions,
                "cyber_versions": cyber_versions,
            },
        }
    except Exception as e:
        logger.error(f"Error saat mendapatkan versi: {e}")
        raise HTTPException(status_code=500, detail=f"Error saat mendapatkan versi: {str(e)}")

@router.post("/update-app")
async def update_app():
    try:
        logger.info("Memulai proses pembaruan aplikasi...")
        current_version = get_current_app_version()
        logger.info(f"Versi aplikasi saat ini: {current_version}")
        github_owner = "CyberSecurityDept"
        github_repo = "manicmanix"
        latest_version_tag = get_latest_remote_tag_api(github_owner, github_repo)
        logger.info(f"Tag terbaru dari GitHub: {latest_version_tag}")
        if latest_version_tag != current_version:
            checkout_output = checkout_latest_tag(latest_version_tag)
            logger.info(f"Checkout output: {checkout_output}")
            update_env_file("CURRENT_APP_VERSION", latest_version_tag)
            logger.info(f"File .env telah diperbarui dengan versi terbaru: {latest_version_tag}")
            message = "updated app successfully."
            download_output = "Checked out to latest tag."
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
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error saat memperbarui aplikasi: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error saat memperbarui aplikasi: {str(e)}")