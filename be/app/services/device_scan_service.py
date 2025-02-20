import os
from mvt import android
from click import Group
import logging
import subprocess

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_device_scan(output_directory: str):
    os.makedirs(output_directory, exist_ok=True)

    try:
        subprocess.run(["adb", "kill-server"], check=True)
        logger.info("ADB server restarted successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to restart ADB server: {str(e)}")
        raise RuntimeError(f"Failed to restart ADB server: {str(e)}")

    cli: Group = android.cli

    default_args = [
        "check-adb",
        "--output",
        output_directory,
        "--iocs",
        "modules/indicators/",
        "-p",
        "1",
    ]

    try:
        cli(default_args)
        logger.info("Scan completed successfully.")
    except SystemExit as e:
        logger.info(f"Scan completed with exit code: {e.code}")
    except Exception as e:
        logger.error(f"Failed to run scan: {str(e)}")
        raise RuntimeError(f"Failed to run scan: {str(e)}")
