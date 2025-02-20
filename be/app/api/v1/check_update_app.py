import os
import logging
import subprocess
from fastapi import APIRouter, HTTPException
import requests
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

def update_env_file(key: str, value: str):
    """
    Memperbarui file .env dengan key dan value tertentu.
    Jika key sudah ada, nilainya akan diperbarui.
    Jika key belum ada, baris baru akan ditambahkan.
    """
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

def get_latest_remote_tag_git(repo_url: str):
    """
    Mendapatkan tag terbaru dari remote repository GitHub menggunakan perintah Git.
    """
    try:
        result = subprocess.run(
            ["git", "ls-remote", "--tags", repo_url],
            capture_output=True,
            text=True,
            check=True
        )
        output = result.stdout.strip()
        logger.info(f"Output dari 'git ls-remote --tags': {output}")

        # Ekstrak tag terbaru dari output
        tags = [line.split("\trefs/tags/")[1] for line in output.splitlines() if "refs/tags/" in line]
        if not tags:
            raise ValueError("Tidak ada tag yang ditemukan di repositori GitHub.")
        latest_tag = tags[-1].replace("^{}", "")  # Ambil tag terbaru (hapus suffix ^{} jika ada)
        logger.info(f"Tag terbaru dari GitHub: {latest_tag}")
        return latest_tag
    except subprocess.CalledProcessError as e:
        error_message = e.stderr.strip() if e.stderr else "Unknown error"
        logger.error(f"Error saat menjalankan 'git ls-remote --tags': {error_message}")
        raise HTTPException(status_code=400, detail=f"Error saat menjalankan 'git ls-remote --tags': {error_message}")

@router.post("/check-update-app")
async def check_update_app():
    """
    Endpoint untuk memeriksa apakah ada versi baru dari aplikasi frontend.
    """
    try:
        current_version = get_current_app_version()
        logger.info(f"Versi aplikasi saat ini: {current_version}")

        # Pilih metode untuk mendapatkan tag terbaru
        use_api = True  # Set ke False jika ingin menggunakan perintah Git

        if use_api:
            github_owner = "CyberSecurityDept"  # Ganti dengan nama pemilik repositori GitHub
            github_repo = "manicmanix"  # Ganti dengan nama repositori GitHub
            latest_version_tag = get_latest_remote_tag_api(github_owner, github_repo)
        else:
            # Dapatkan tag terbaru dari perintah Git
            repo_url = "https://github.com/CyberSecurityDept/manicmanix.git"
            latest_version_tag = get_latest_remote_tag_git(repo_url)

        logger.info(f"Tag terbaru dari GitHub: {latest_version_tag}")

        # Bandingkan versi
        if latest_version_tag != current_version:
            # Perbarui file .env dengan versi terbaru
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