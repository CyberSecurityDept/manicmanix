import subprocess
import re
import os
from datetime import datetime
from fastapi import HTTPException
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_gitlab_app_version():
    """
    Mendapatkan versi aplikasi frontend dari environment variable CURRENT_APP_VERSION.
    """
    try:
        # Ambil versi aplikasi dari environment variable
        app_version = os.getenv("CURRENT_APP_VERSION")
        if not app_version:
            raise ValueError("CURRENT_APP_VERSION tidak ditemukan di environment variables.")
        
        return [
            {
                "app_version": app_version,
                "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saat mendapatkan versi aplikasi: {str(e)}")

def get_mvt_version():
    """
    Mendapatkan versi mvt-android dari environment variable CURRENT_BEHAVIOURAL_VERSION.
    """
    try:
        # Ambil versi cyber dari environment variable
        cyber_version = os.getenv("CURRENT_BEHAVIOURAL_VERSION")
        if not cyber_version:
            raise ValueError("CURRENT_BEHAVIOURAL_VERSION tidak ditemukan di environment variables.")
        
        return [
            {
                "cyber_version": cyber_version,
                "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saat mendapatkan versi cyber: {str(e)}")