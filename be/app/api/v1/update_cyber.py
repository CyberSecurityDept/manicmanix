from fastapi import APIRouter, HTTPException
import subprocess
import logging
import os
import re
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_shell_command(command: list, error_message: str):
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
        logger.info(f"Command '{' '.join(command)}' berhasil dijalankan.")
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        error_output = e.stderr.strip() if e.stderr else "Unknown error"
        logger.error(f"{error_message}: {error_output}")
        raise HTTPException(status_code=400, detail=f"{error_message}: {error_output}")

@router.post("/update-cyber-version", summary="Update Cyber Version", description="Endpoint ini mengunduh versi terbaru Cyber Behavioural Analysis dan menjalankan 'mvt-android download-iocs'.")
async def update_cyber_version():
    try:
        logger.info("Memulai pengunduhan versi terbaru Cyber Behavioural Analysis...")
        download_output = run_shell_command(
            ["pip", "install", "--upgrade", "mvt"],
            "Gagal mengunduh versi terbaru Cyber Behavioural Analysis"
        )
        logger.info(f"Output pengunduhan Cyber Behavioural Analysis: {download_output}")

        logger.info("Memulai pengunduhan IOCs terbaru...")
        iocs_output = run_shell_command(
            ["mvt-android", "download-iocs"],
            "Gagal menjalankan 'mvt-android download-iocs'"
        )
        logger.info(f"Output pengunduhan IOCs: {iocs_output}")

        latest_version = run_shell_command(
            ["mvt-android", "version"],
            "Gagal mendapatkan versi terbaru Cyber Behavioural Analysis"
        )
        version_match = re.search(r"Version:\s*v?(\d+\.\d+\.\d+)", latest_version)
        if not version_match:
            raise ValueError("Format versi tidak sesuai. Harap pastikan 'mvt-android version' menghasilkan output yang valid.")
        updated_version = version_match.group(1)

        update_env_file("CURRENT_BEHAVIOURAL_VERSION", updated_version)
        logger.info(f"File .env telah diperbarui dengan versi terbaru: {updated_version}")

        download_output = download_output.replace("mvt", "cyber behavioural analysis")

        iocs_version_match = re.search(r"Version:\s*v?(\d+\.\d+\.\d+)", iocs_output)
        iocs_output_cleaned = f"Version: {iocs_version_match.group(1)}" if iocs_version_match else "Version information not found."

        return {
            "message": "Cyber version and IOCs updated successfully.",
            "updated_version": updated_version,
            "download_output": download_output,
            "iocs_output": iocs_output_cleaned,
        }
    except Exception as e:
        logger.error(f"Error saat memperbarui cyber version: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error saat memperbarui cyber version: {str(e)}")

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