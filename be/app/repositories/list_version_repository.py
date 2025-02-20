import subprocess
import re
import json
import os
from pathlib import Path
from fastapi import HTTPException
from datetime import datetime
from packaging.version import Version, InvalidVersion

VERSIONS_FILE = Path("versions.json")
APP_VERSION = "v1.0"
CYBER_VERSION = "v1.1"

def get_gitlab_app_version():
    return [
        {
            "app_version": APP_VERSION,
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    ]

def get_mvt_version():
    """
    Mendapatkan versi mvt-android menggunakan perintah 'mvt-android version'.
    """
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
            raise ValueError("Versi tidak ditemukan dalam output mvt-android.")
        latest_version = version_match.group(1)  # Mengambil versi (misalnya, "2.6.0")
        return [
            {
                "cyber_version": latest_version,
                "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        ]
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Gagal menjalankan 'mvt-android version': {e.stderr}")

def update_app_version(new_version):
    global APP_VERSION
    APP_VERSION = new_version

def update_cyber_version(new_version):
    global CYBER_VERSION
    CYBER_VERSION = new_version

def load_versions():
    if not VERSIONS_FILE.exists():
        raise HTTPException(status_code=404, detail="Versions file not found.")
    try:
        with open(VERSIONS_FILE, "r") as file:
            return json.load(file)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse versions file: {e}")

def save_versions(data):
    try:
        with open(VERSIONS_FILE, "w") as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save versions file: {e}")

def compare_versions(current_version: str, new_version: str):
    try:
        current = Version(current_version)
        new = Version(new_version)
        return new > current
    except InvalidVersion as e:
        raise ValueError(f"Format versi tidak valid: {e}")