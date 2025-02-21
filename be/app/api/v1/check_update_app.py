import os
import logging
import requests
from fastapi import APIRouter, HTTPException
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI router
router = APIRouter()

def get_current_app_version():
    """
    Mendapatkan versi aplikasi frontend saat ini dari environment variable.
    """
    return os.getenv("CURRENT_APP_VERSION", "v1.0.0")

def get_latest_remote_tag_api(owner: str, repo: str):
    """
    Mendapatkan tag terbaru dari remote repository GitHub menggunakan API.
    """
    try:
        url = f"https://api.github.com/repos/{owner}/{repo}/tags"
        github_token = os.getenv("GITHUB_TOKEN_APP")  # Ambil token dari environment variable
        if not github_token:
            raise ValueError("GITHUB_TOKEN_APP tidak ditemukan di environment variables.")
        
        headers = {"Authorization": f"token {github_token}"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise exception jika ada error HTTP

        tags = response.json()
        if not tags:
            raise ValueError("Tidak ada tag yang ditemukan di repositori GitHub.")
        
        latest_tag = tags[0]["name"]  # Ambil tag pertama (terbaru)
        logger.info(f"Tag terbaru dari GitHub: {latest_tag}")
        return latest_tag
    except requests.RequestException as e:
        logger.error(f"Error saat mengambil tag dari GitHub: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error saat mengambil tag dari GitHub: {str(e)}")

@router.post("/check-update-app")
async def check_update_app():
    """
    Endpoint untuk memeriksa apakah ada versi baru dari aplikasi frontend.
    """
    try:
        # Versi saat ini
        current_version = get_current_app_version()
        logger.info(f"Versi aplikasi saat ini: {current_version}")

        # Dapatkan tag terbaru dari GitHub API
        github_owner = "CyberSecurityDept"  # Ganti dengan nama pemilik repositori GitHub
        github_repo = "manicmanix"  # Ganti dengan nama repositori GitHub
        latest_version_tag = get_latest_remote_tag_api(github_owner, github_repo)
        logger.info(f"Tag terbaru dari GitHub: {latest_version_tag}")

        # Bandingkan versi
        if latest_version_tag != current_version:
            message = "New version available."
            download_output = "Please update to the latest version."
            updated_version = current_version
        else:
            message = "Application is already up to date."
            download_output = "You Already Updated."
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