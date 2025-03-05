import asyncio
import shutil
import aiohttp
import os
import logging
import json
import time
import re
import requests
import aiohttp
import httpx
import subprocess
import mimetypes

from pathlib import Path
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from datetime import datetime
from pydantic import BaseModel
from typing import List, Dict, Optional
from app.repositories.data_pulling_repository import Data_Pulling
from app.services.data_pulling_service import dataPullingService
from app.services.device_overview_service import DeviceOverviewService
from app.services.device_scan_service import run_device_scan
from app.utils.calculate_progress import calculate_realistic_progress
from app.repositories.risk_repository import RiskRepository
from app.repositories.fast_scan_repository import read_dumpsys_activities, calculate_security_percentage_from_activities, background_fast_scan
from app.api.v1.results import get_result

router = APIRouter()
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_SCAN_PATH = Path(os.path.expanduser(f"{str(os.getenv('BASE_SCAN_PATH'))}"))
os.makedirs(BASE_SCAN_PATH, exist_ok=True)

SCAN_HISTORY_PATH = os.path.expanduser(f"{str(os.getenv('BASE_SCAN_PATH'))}")
os.makedirs(BASE_SCAN_PATH, exist_ok=True)

BATCH_SIZE_LIMIT_MB = int(os.getenv("BATCH_SIZE_LIMIT", 250))
BATCH_SIZE_LIMIT_BYTES = BATCH_SIZE_LIMIT_MB * 1024 * 1024

def add_scan_history(
    no: int,
    name: str,
    model: str,
    imei1: str, 
    imei2: str,
    security_patch: str,
    last_scan: str,
    security_percentage: float,
    scan_type: str,
    status: str,
):
    try:
        SCAN_HISTORY_PATH = Path(os.path.expanduser(f"{str(os.getenv('BASE_SCAN_PATH'))}"))

        if SCAN_HISTORY_PATH.exists():
            with open(SCAN_HISTORY_PATH, "r") as file:
                history_data: List[Dict] = json.load(file)
        
        else:
            history_data = []

        
        new_entry = {
            "no": no,
            "name": name,
            "model": model,
            "imei1": imei1,
            "imei2": imei2,
            "security_patch": security_patch,
            "last_scan": last_scan,
            "security_percentage": security_percentage,
            "scan_type": scan_type,
            "status": status,
        }

        
        history_data.append(new_entry)

        
        with open(SCAN_HISTORY_PATH, "w") as file:
            json.dump(history_data, file, indent=4)
            file.write("\n")  

        print(f"Riwayat scan berhasil ditambahkan: {new_entry}")
    except Exception as e:
        print(f"Gagal menambahkan riwayat scan: {e}")

async def get_device_details(serial_number: str) -> dict:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{os.getenv('BASE_URL_DEVICE_OVERVIEW_DEFAULT')}device-overview/")
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Gagal mengambil detail perangkat: {e}")
        return {}
    
def restart_adb_server():
    try: 
        subprocess.run(["adb","kill-server"], check=True)
        subprocess.run(["adb","start-server"], check=True)

        print('=== ADB Server restarted Successfully ! ===')
    except subprocess.CalledProcessError as e:
        print(f"Failed to Restart ADB Server {e}")
        raise

@router.get("/fastscan-progress/{serial_number}")
async def fastscan_progress(serial_number: str):
    try:
        
        base_dir = f"output-scan/fast-scan/{serial_number}"
        
        if not os.path.exists(base_dir):
            raise HTTPException(status_code=404, detail="Serial number directory not found")
        
        subdirs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
        if not subdirs:
            raise HTTPException(status_code=404, detail="No subdirectory found in serial number directory")
        
        target_folder = subdirs[0]
        
        log_file_path = os.path.join(base_dir, target_folder, "command.log")
        if not os.path.exists(log_file_path):
            logger.error("Log file not found!")
            raise HTTPException(status_code=404, detail="Log file not found")
        progress_data = calculate_realistic_progress(log_file_path)
        return progress_data
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get fast scan progress: {str(e)}"
        )

@router.get("/fullscan-progress/{serial_number}")
async def fullscan_progress(serial_number: str):
    try:
        
        base_dir = f"output-scan/full-scan/{serial_number}"
        
        
        if not os.path.exists(base_dir):
            raise HTTPException(status_code=404, detail="Serial number directory not found")
        
        
        subdirs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
        
        if not subdirs:
            raise HTTPException(status_code=404, detail="No subdirectory found in serial number directory")
        
        
        target_folder = subdirs[0]
        
        
        log_file_path = os.path.join(base_dir, target_folder, "command.log")
        print(f"Looking for log file at: {log_file_path}")

        if not os.path.exists(log_file_path):
            print("Log file not found!")
            raise HTTPException(status_code=404, detail="Log file not found")

        progress_data = calculate_realistic_progress(log_file_path)
        return progress_data

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get full scan progress: {str(e)}"
        )

@router.post("/fast-scan/{serial_number}")
async def fast_scan(serial_number: str, name: str, background_tasks: BackgroundTasks):
    try:
        start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        current_time = datetime.now().strftime("%d%m%Y_%H%M%S")
        scan_id = f"{serial_number}_{current_time}"
        
        device_details = DeviceOverviewService.get_device_overview()
        model = device_details.get("model", "")
        imei1 = device_details.get("imei1", "")
        imei2 = device_details.get("imei2", "")
        security_patch = device_details.get("security_patch", "")
        security_percentage = "0.00%"
        
        DeviceOverviewService.update_device_overview(serial_number, {
            "name": name,
            "last_scan": start_time,
        })
        
        output_dir = BASE_SCAN_PATH / "fast-scan" / serial_number / current_time
        output_dir.mkdir(parents=True, exist_ok=True)
        
        
        fast_scan_result_path = output_dir / "detail_result.json"
        initial_result = {
            "scan_id": scan_id,
            "serial_number": serial_number,
            "time_stamp": current_time,  
            "name": name,
            "model": model,
            "imei1": imei1,
            "imei2": imei2,
            "security_patch": security_patch,
            "last_scan": start_time,
            "security_percentage": security_percentage,
            "scan_type": "fast-scan",
            "status": "started"
        }
        with open(fast_scan_result_path, "w") as f:
            json.dump(initial_result, f, indent=4)
        
        
        history_scan_path = BASE_SCAN_PATH / "history_scan.json"
        history_entries = []
        if history_scan_path.exists():
            try:
                with open(history_scan_path, "r") as f:
                    history_entries = json.load(f)
                    if not isinstance(history_entries, list):
                        history_entries = []
            except Exception as e:
                logger.error(f"Error reading history_scan.json: {e}")
                history_entries = []
        
        entry_no = len(history_entries) + 1
        new_entry = {
            "no": entry_no,
            "scan_id": scan_id,      
            "time_stamp": current_time,  
            "name": name,
            "model": model,
            "imei1": imei1,
            "imei2": imei2,
            "security_patch": security_patch,
            "last_scan": start_time,
            "security_percentage": security_percentage,  
            "scan_type": "fast-scan",
            "status": "started"
        }
        history_entries.append(new_entry)
        with open(history_scan_path, "w") as f:
            json.dump(history_entries, f, indent=4)
        
        
        background_tasks.add_task(background_fast_scan, str(output_dir), serial_number, scan_id, new_entry)
        
        return {
            "status": 200,
            "message": "Fast scan started successfully in the background",
            "data": {"serial_number": serial_number, "name": name, "scan_id": scan_id},
        }
    
    except Exception as e:
        error_message = str(e)
        
        if "Unable to connect to the device over USB" in error_message or "Device is busy" in error_message:
            logger.error("Detected connection or busy error. Restarting ADB server...")
            try:
                restart_adb_server()
                if fast_scan_result_path.exists():
                    with open(fast_scan_result_path, "r") as f:
                        result_data = json.load(f)
                    result_data["status"] = "restarted"
                    with open(fast_scan_result_path, "w") as f:
                        json.dump(result_data, f, indent=4)
                background_tasks.add_task(background_fast_scan, str(output_dir), serial_number, scan_id, new_entry)
                if history_scan_path.exists():
                    with open(history_scan_path, "r") as f:
                        history_entries = json.load(f)
                    for entry in history_entries:
                        if entry.get("scan_id") == scan_id:
                            entry["status"] = "restarted"
                            break
                    with open(history_scan_path, "w") as f:
                        json.dump(history_entries, f, indent=4)
                return {
                    "status": 200,
                    "message": "ADB server restarted and fast scan retried in the background",
                    "data": {"serial_number": serial_number, "name": name, "scan_id": scan_id},
                }
            except Exception as adb_error:
                if fast_scan_result_path.exists():
                    with open(fast_scan_result_path, "r") as f:
                        result_data = json.load(f)
                    result_data["status"] = "failed"
                    result_data["error"] = str(adb_error)
                    result_data["failed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    with open(fast_scan_result_path, "w") as f:
                        json.dump(result_data, f, indent=4)
                if history_scan_path.exists():
                    with open(history_scan_path, "r") as f:
                        history_entries = json.load(f)
                    for entry in history_entries:
                        if entry.get("scan_id") == scan_id:
                            entry["status"] = "failed"
                            break
                    with open(history_scan_path, "w") as f:
                        json.dump(history_entries, f, indent=4)
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to restart ADB server and retry fast scan: {str(adb_error)}"
                )
        else:
            if fast_scan_result_path.exists():
                with open(fast_scan_result_path, "r") as f:
                    result_data = json.load(f)
                result_data["status"] = "failed"
                result_data["error"] = error_message
                result_data["failed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                with open(fast_scan_result_path, "w") as f:
                    json.dump(result_data, f, indent=4)
            if history_scan_path.exists():
                with open(history_scan_path, "r") as f:
                    history_entries = json.load(f)
                for entry in history_entries:
                    if entry.get("scan_id") == scan_id:
                        entry["status"] = "failed"
                        break
                with open(history_scan_path, "w") as f:
                    json.dump(history_entries, f, indent=4)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to start fast scan: {error_message}"
            )


@router.post("/full-scan/{serial_number}")
async def full_scan(serial_number: str, name: str, background_tasks: BackgroundTasks):
    try:
        start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        device_details = DeviceOverviewService.get_device_overview()
        current_time = datetime.now().strftime("%d%m%Y_%H%M%S")
        
        model = device_details.get("model", "Unknown")
        imei1 = device_details.get("imei1", "")
        imei2 = device_details.get("imei2", "")
        security_patch = device_details.get("security_patch", "")
        security_percentage = "0.0%"
        scan_type = "full-scan"
        
        
        device_data = {
            "name": name,
            "scan_type": "full",
            "last_scan": start_time,
        }
        DeviceOverviewService.update_device_overview(serial_number, device_data)    
        history_scan_path = BASE_SCAN_PATH / "history_scan.json"
        
        
        BASE_SCAN_PATH.mkdir(parents=True, exist_ok=True)
        
        
        history_entries = []
        if history_scan_path.exists():
            try:
                with open(history_scan_path, "r") as history_file:
                    history_entries = json.load(history_file)
                    
                    if not isinstance(history_entries, list):
                        history_entries = [history_entries]
            except Exception as e:
                
                history_entries = []
        else:
            
            with open(history_scan_path, "w") as history_file:
                json.dump([], history_file, indent=4)
        
        
        entry_no = len(history_entries) + 1
        scan_id = f"{serial_number}_{current_time}"
        serial_number =f"{serial_number}"
        time_stamp =f"{current_time}"
        
        
        new_entry = {
            "no": entry_no,
            "scan_id": scan_id,
            "serial_number": serial_number,
            "time_stamp": time_stamp,
            "name": name,
            "model": model,
            "imei1": imei1,
            "imei2": imei2,
            "security_patch": security_patch,
            "last_scan": start_time,
            "security_percentage": security_percentage,
            "scan_type": scan_type
        }
        
        
        history_entries.append(new_entry)
        
        
        with open(history_scan_path, "w") as f:
            json.dump(history_entries, f, indent=4)
        
        
        output_dir = BASE_SCAN_PATH / "full-scan" / serial_number / current_time
        output_dir.mkdir(parents=True, exist_ok=True)
        
        
        
        full_scan_result_path = output_dir / "detail_result.json"
        with open(full_scan_result_path, "w") as f:
            json.dump({
                **new_entry,
                "status": "started",
                "scan_details": {}
            }, f, indent=4)

        
        
        background_tasks.add_task(run_full_scan, str(output_dir), serial_number, scan_id)
        
        
        add_scan_history(
            no=entry_no,
            name=name,
            model=model,
            imei1=imei1,
            imei2=imei2,
            security_patch=security_patch,
            last_scan=start_time,
            security_percentage=security_percentage,
            scan_type=scan_type,
            status="started"
        )
        
        return {
            "status": 200,
            "message": "Full scan started successfully in the background",
            "data": {
                "serial_number": serial_number,
                "name": name,
                "scan_type": scan_type,
                "scan_id": scan_id
            },
        }
    except Exception as e:
        
        return {"status": 500, "message": f"Failed to start full scan: {str(e)}"}    
    
    except Exception as e:
        error_message = str(e)
        if "Unable to connect to the device over USB" in error_message or "Device is busy" in error_message:
            logger.error("Detected connection or busy error. Restarting ADB server...")
            try:
                restart_adb_server()
                
                background_tasks.add_task(run_full_scan, str(output_dir), serial_number, scan_id)
                add_scan_history(
                    no=entry_no,
                    name=name,
                    model=model,
                    imei1=imei1,
                    imei2=imei2,
                    security_patch=security_patch,
                    last_scan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    security_percentage=security_percentage,
                    scan_type=scan_type,
                    status="restarted"
                )
                return {
                    "status": 200,
                    "message": "ADB server restarted and full scan retried in the background",
                    "data": {
                        "serial_number": serial_number,
                        "name": name,
                        "scan_type": scan_type,
                        "scan_id": scan_id
                    },
                }
            except Exception as adb_error:
                add_scan_history(
                    no=entry_no,
                    name=name,
                    model=model,
                    imei1=imei1,
                    imei2=imei2,
                    security_patch=security_patch,
                    last_scan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    security_percentage=security_percentage,
                    scan_type=scan_type,
                    status="failed"
                )
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to restart ADB server and retry full scan: {str(adb_error)}"
                )
        else:
            add_scan_history(
                no=entry_no,
                name=name,
                model=model,
                imei1=imei1,
                imei2=imei2,
                security_patch=security_patch,
                last_scan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                security_percentage=security_percentage,
                scan_type=scan_type,
                status="failed"
            )
            raise HTTPException(
                status_code=500,
                detail=f"Failed to start full scan: {error_message}"
            )
            
def get_last_scan_percentage(serial_number: str, current_timestamp: str) -> str:
    try:
        
        base_scan_dir = BASE_SCAN_PATH / "full-scan" / serial_number
        
        if not base_scan_dir.exists():
            logger.info(f"No previous scans found for serial number {serial_number}")
            return "0.0%"
        
        
        timestamps = [d for d in os.listdir(base_scan_dir) if os.path.isdir(os.path.join(base_scan_dir, d))]
        timestamps.sort(reverse=True)  
        
        
        previous_timestamp = None
        for timestamp in timestamps:
            if timestamp != current_timestamp:
                previous_timestamp = timestamp
                break
        
        if not previous_timestamp:
            logger.info(f"No previous scan found before {current_timestamp}")
            return "0.0%"
        
        
        previous_result_path = base_scan_dir / previous_timestamp / "detail_result.json"
        if not previous_result_path.exists():
            logger.warning(f"No detail_result.json found in previous scan directory: {previous_result_path}")
            return "0.0%"
        
        with open(previous_result_path, "r") as f:
            previous_data = json.load(f)
            return previous_data.get("security_percentage", "0.0%")
            
    except Exception as e:
        logger.error(f"Error reading last scan percentage: {e}")
        return "0.0%"
def run_full_scan(output_dir: str, serial_number: str, scan_id: str):
    logger.info("output_dir", output_dir)
    try:
        
        history_scan_path = BASE_SCAN_PATH / "history_scan.json"
        initial_data = {}
        history_entries = []
        if history_scan_path.exists():
            with open(history_scan_path, "r") as f:
                history_entries = json.load(f)
                for entry in history_entries:
                    if entry.get("scan_id") == scan_id:
                        initial_data = entry
                        break
        
        if not initial_data:
            logger.error(f"Tidak dapat menemukan data awal untuk scan_id: {scan_id}")
            raise Exception("Initial scan data not found")

        current_timestamp = initial_data.get("time_stamp")
        last_scan_percentage = get_last_scan_percentage(serial_number, current_timestamp)
        logger.info(f"Last scan percentage: {last_scan_percentage}")

        logger.info(f"Starting full scan in directory: {output_dir}")
        
        logger.info(f'serial_number, output_dir ${serial_number, output_dir}')
        
        logger.info(f"Starting full scan in directory: {output_dir}")
        # run_device_scan(output_dir)  
        
        retrieved_files = retrieve_device_files(serial_number, output_dir)
        logger.info(f"Retrieved {len(retrieved_files)} files")
        
        logger.info(f"serial_number, retrieved_files ${serial_number, retrieved_files}")
        scan_result = perform_deep_scan(serial_number, retrieved_files)
        logger.info("Deep scan completed")
        
        save_scan_result(output_dir, scan_result)
        logger.info("Scan result saved")
        
        scan_result_file = os.path.join(output_dir, "scan_result.json")
        process_scan_result(scan_result_file)
        logger.info("Scan result processed")
        
        try:
            asyncio.run(get_result(serial_number, "full-scan"))
            logger.info("get_result executed successfully")
        except Exception as get_result_error:
            logger.error(f"Error executing get_result: {get_result_error}")
        
        
        
        task_result_dir = os.path.join(output_dir, "task_result")
        new_security_percentage = "0.0%"
        if os.path.exists(task_result_dir):
            logger.info("Reading task results")
            task_results = RiskRepository.read_task_results(task_result_dir)
            new_security_percentage = RiskRepository.calculate_security_percentage(task_results)
            logger.info(f"Calculated security percentage: {new_security_percentage}")
        
        
        default_scan_overview = {
            "applications": {"scanned": 0, "threats": 0},
            "documents": {"scanned": 0, "threats": 0},
            "media": {"scanned": 0, "threats": 0},
            "installer": {"scanned": 0, "threats": 0},
        }
        default_total_threats = 0
        default_threats = []

        base_scan_dir = BASE_SCAN_PATH / "full-scan" / serial_number
        if base_scan_dir.exists():
            timestamp_folders = [
                d for d in os.listdir(base_scan_dir)
                if os.path.isdir(os.path.join(base_scan_dir, d))
            ]
            timestamp_folders.sort(reverse=True)
            if timestamp_folders:
                latest_folder = Path(base_scan_dir) / timestamp_folders[0]
                result_file_path = latest_folder / "full-scan_result.json"
                if result_file_path.exists():
                    with open(result_file_path, "r") as rf:
                        result_data = json.load(rf)
                    scan_overview = result_data.get("scan_overview", default_scan_overview)
                    total_threats = result_data.get("total_threats", default_total_threats)
                    threats = result_data.get("threats", default_threats)
                else:
                    scan_overview = default_scan_overview
                    total_threats = default_total_threats
                    threats = default_threats
            else:
                scan_overview = default_scan_overview
                total_threats = default_total_threats
                threats = default_threats
        else:
            scan_overview = default_scan_overview
            total_threats = default_total_threats
            threats = default_threats

        logger.info(f"Scan overview loaded: {scan_overview}")
        
        
        full_scan_result_path = os.path.join(output_dir, "detail_result.json")
        logger.info(f"Creating full scan result at: {full_scan_result_path}")
        
        updated_data = {
            "no": initial_data.get("no"),
            "scan_id": scan_id,
            "serial_number": serial_number,
            "time_stamp": initial_data.get("time_stamp"),
            "name": initial_data.get("name"),
            "model": initial_data.get("model"),
            "imei1": initial_data.get("imei1"),
            "imei2": initial_data.get("imei2"),
            "security_patch": initial_data.get("security_patch"),
            "last_scan": initial_data.get("last_scan"),
            "security_percentage": new_security_percentage,
            "last_scan_percentage": last_scan_percentage,
            "scan_overview": scan_overview,
            "total_threats": total_threats,
            "threats": threats,
            "scan_type": "full-scan",
            "status": "completed"
        }
        
        with open(full_scan_result_path, "w") as f:
            json.dump(updated_data, f, indent=4)
        logger.info("Full scan result created")
        
        
        if history_scan_path.exists():
            logger.info("Updating history scan")
            updated = False
            for entry in history_entries:
                if entry.get("scan_id") == scan_id:
                    entry["security_percentage"] = new_security_percentage
                    entry["last_scan_percentage"] = last_scan_percentage
                    entry["status"] = "completed"
                    
                    updated = True
                    break

            if updated:
                with open(history_scan_path, "w") as f:
                    json.dump(history_entries, f, indent=4)
                logger.info("History scan updated")
            else:
                logger.warning(f"Tidak menemukan entry dengan id {scan_id} untuk di update")
                
    except Exception as e:
        logger.error(f"Error in run_full_scan: {str(e)}")
        try:
            full_scan_result_path = os.path.join(output_dir, "detail_result.json")
            error_data = {
                **initial_data,
                "status": "failed",
                "error": str(e),
                "failed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            with open(full_scan_result_path, "w") as f:
                json.dump(error_data, f, indent=4)
        except Exception as write_error:
            logger.error(f"Failed to write error status: {write_error}")
        raise

def retrieve_device_files(serial_number: str, output_dir: str) -> list[str]:
    try:
        os.makedirs(output_dir, exist_ok=True)
        pulling_service = dataPullingService()
        
        if not pulling_service.check_adb_connected():
            raise Exception(f"Device {serial_number} tidak terhubung dengan ADB")
        device_serial = pulling_service.get_device_serials()

        if serial_number not in device_serial:
            raise Exception(f"Device dengan serial number {serial_number} tidak ditemukan")
        
        user_ids = pulling_service.user_enum(serial_number)
        if not user_ids:
            raise Exception(f"User tidak ditemukan pada device {serial_number}")

        retrieved_files = []
        for user_id in user_ids:
            try:
                
                result = pulling_service.pull_files_from_android(serial_number, user_id)
                logger.info(f"File berhasil di-pull untuk user {user_id}: {result}")
                user_path = os.path.join(output_dir, f"user_{user_id}")
                for root, _, files in os.walk(user_path):
                    for file in files:
                        retrieved_files.append(os.path.join(root, file))

            except Exception as e:
                logger.error(f"Error ketika pulling data untuk user {user_id}: {e}")
                continue

        if not retrieved_files:
            logger.warning(f"Tidak ada data yang ter-pull dari device {serial_number}")

        return retrieved_files

    except Exception as e:
        logger.error(f"Terjadi Error di fungsi retrieve_device_files: {e}")
        raise Exception(f"Failed to retrieve files from device: {e}")

def perform_deep_scan(serial_number: str, retrieved_files: List[str]):
    
    APP_ISOLATED_DIR = os.getenv('APP_ISOLATED_FOR_VIRUS_TOTAL')
    if not APP_ISOLATED_DIR:
        raise EnvironmentError("Variabel lingkungan APP_ISOLATED_FOR_VIRUS_TOTAL tidak ditemukan")
    
    DOCKER_URL = os.getenv('DOCKER_URL')
    if not DOCKER_URL:
        raise EnvironmentError("Variabel lingkungan DOCKER_URL tidak ditemukan")
    
    isolated_folder = Path(os.path.expanduser(f"{APP_ISOLATED_DIR}/{serial_number}"))
    
    categorized_files = categorize_files(isolated_folder)
    
    batch_size = int(os.getenv('BATCH_SIZE', 412))
    all_scan_results = {"task_ids": []}
    batch_delay = int(os.getenv('BATCH_DELAY', 65))
    request_timeout = int(os.getenv('REQUEST_TIMEOUT', 30))
    
    for category, file_paths in categorized_files.items():
        batches = [file_paths[i:i+batch_size] for i in range(0, len(file_paths), batch_size)]
        
        for i, batch in enumerate(batches, 1):
            batch_paths = [Path(path) for path in batch]
            send_files_to_server(serial_number, {category: batch_paths})
            
            batch_relative_paths = [
                f"/uploaded_files/{serial_number}/{path.relative_to(isolated_folder)}"
                for path in batch_paths
            ]
            
            scan_url = f"{DOCKER_URL}scan-files"
            payload = {"file_paths": batch_relative_paths}
            
            try:
                response = requests.post(
                    scan_url,
                    headers={"Content-Type": "application/json"},
                    json=payload,
                    timeout=request_timeout
                )
                response.raise_for_status()
                all_scan_results["task_ids"].extend(response.json()["task_ids"])
                logger.info(f"Batch {i} dari kategori '{category}' berhasil di-scan: {len(response.json()['task_ids'])} task_ids")
            except requests.exceptions.RequestException as e:
                logger.error(f"Kesalahan pada batch {i} dari kategori '{category}': {e}")
                raise
            
            if i < len(batches):
                logger.info(f"Menunggu {batch_delay} detik sebelum batch berikutnya...")
                time.sleep(batch_delay)
    
    logger.info(f"Total task_ids: {len(all_scan_results['task_ids'])}")
    return all_scan_results

def send_files_to_server(serial_number: str, file_paths_by_category: Dict[str, List[Path]]):
    try:
        upload_url = f"{os.getenv('DOCKER_URL')}upload-files/"
        logger.info(f"Menggunakan URL upload: {upload_url}")

        for category, file_paths in file_paths_by_category.items():
            logger.info(f"Memulai pengunggahan untuk kategori '{category}'")

            # Pisahkan file besar (> BATCH_SIZE_LIMIT) dan file normal
            large_files = []
            normal_files = []

            for file_path in file_paths:
                file_size = file_path.stat().st_size
                if file_size > BATCH_SIZE_LIMIT_BYTES:
                    large_files.append(file_path)
                else:
                    normal_files.append(file_path)

            # Kirim file normal dalam batch
            send_files_in_batches(upload_url, serial_number, category, normal_files)

            # Kirim file besar satu per satu
            for large_file in large_files:
                logger.info(f"Mengunggah file besar: {large_file.name}")
                upload_single_file(upload_url, serial_number, category, large_file)

    except Exception as e:
        logger.error(f"Error saat mengirim file ke server: {e}")
        raise Exception(f"Gagal mengirim file ke server: {e}")


def send_files_in_batches(upload_url: str, serial_number: str, category: str, file_paths: List[Path]):
    """
    Mengirim file dalam batch berdasarkan ukuran total batch.
    """
    current_batch = []
    current_batch_size = 0

    for file_path in file_paths:
        file_size = file_path.stat().st_size

        # Jika menambahkan file ini melebihi batas ukuran batch, kirim batch saat ini
        if current_batch_size + file_size > BATCH_SIZE_LIMIT_BYTES:
            upload_batch(upload_url, serial_number, category, current_batch)
            current_batch = []
            current_batch_size = 0

        # Tambahkan file ke batch saat ini
        current_batch.append(file_path)
        current_batch_size += file_size

    # Kirim batch terakhir jika ada file tersisa
    if current_batch:
        upload_batch(upload_url, serial_number, category, current_batch)


def upload_batch(upload_url: str, serial_number: str, category: str, file_paths: List[Path]):
    """
    Mengunggah satu batch file ke server.
    """
    files = []
    payload = {
        "serial_number": serial_number,
        "category": category
    }

    try:
        for file_path in file_paths:
            content_type, _ = mimetypes.guess_type(str(file_path))
            content_type = content_type or 'application/octet-stream'

            file_obj = file_path.open('rb')
            files.append(("files", (file_path.name, file_obj, content_type)))

        logger.info(f"Mengunggah batch dengan {len(file_paths)} file")
        response = requests.post(upload_url, files=files, data=payload, timeout=120)

        # Tutup semua file objek setelah selesai
        for _, (filename, file_obj, content_type) in files:
            file_obj.close()

        if response.status_code == 200:
            logger.info(f"Batch berhasil diunggah: {response.json()}")
        else:
            logger.error(f"Gagal mengunggah batch: {response.status_code} - {response.text}")
            raise Exception(f"Request upload gagal untuk batch: {response.status_code} - {response.text}")

    except requests.exceptions.Timeout:
        logger.error("Timeout terjadi saat mengunggah batch")
        raise Exception("Timeout terjadi saat mengunggah batch")
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Koneksi gagal saat mengunggah batch: {e}")
        raise Exception(f"Koneksi gagal saat mengunggah batch")
    except Exception as e:
        logger.error(f"Error tak terduga saat mengunggah batch: {e}")
        raise Exception(f"Error tak terduga saat mengunggah batch")


def upload_single_file(upload_url: str, serial_number: str, category: str, file_path: Path):
    """
    Mengunggah satu file ke server.
    """
    content_type, _ = mimetypes.guess_type(str(file_path))
    content_type = content_type or 'application/octet-stream'

    try:
        with file_path.open('rb') as file_obj:
            files = [("files", (file_path.name, file_obj, content_type))]
            payload = {
                "serial_number": serial_number,
                "category": category
            }

            logger.info(f"Mengunggah file besar: {file_path.name}")
            response = requests.post(upload_url, files=files, data=payload, timeout=120)

            if response.status_code == 200:
                logger.info(f"File besar '{file_path.name}' berhasil diunggah: {response.json()}")
            else:
                logger.error(f"Gagal mengunggah file besar '{file_path.name}': {response.status_code} - {response.text}")
                raise Exception(f"Request upload gagal untuk file besar '{file_path.name}': {response.status_code} - {response.text}")

    except requests.exceptions.Timeout:
        logger.error(f"Timeout terjadi saat mengunggah file besar '{file_path.name}'")
        raise Exception(f"Timeout terjadi saat mengunggah file besar '{file_path.name}'")
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Koneksi gagal saat mengunggah file besar '{file_path.name}': {e}")
        raise Exception(f"Koneksi gagal saat mengunggah file besar '{file_path.name}'")
    except Exception as e:
        logger.error(f"Error tak terduga saat mengunggah file besar '{file_path.name}': {e}")
        raise Exception(f"Error tak terduga saat mengunggah file besar '{file_path.name}'")
    
def categorize_files(base_path: str) -> Dict[str, List[Path]]:
    """
    Mengiterasi folder `isolated` dan membagi file ke dalam kategori berdasarkan subfolder.
    """
    categories = {
        "archive": [],
        "documents": [],
        "installed_apps": [],
        "installer": [],
        "media": [],
    }

    # Iterasi melalui semua subfolder di dalam `isolated`
    for root, dirs, files in os.walk(base_path):
        for file in files:
            file_path = Path(os.path.join(root, file))
            parent_dir = file_path.parent.name.lower()

            # Masukkan file ke kategori berdasarkan nama subfolder
            if parent_dir == "archive":
                categories["archive"].append(file_path)
            elif parent_dir == "documents":
                categories["documents"].append(file_path)
            elif parent_dir == "installed_apps":
                categories["installed_apps"].append(file_path)
            elif parent_dir == "installer":
                categories["installer"].append(file_path)
            elif parent_dir == "media":
                categories["media"].append(file_path)

    return categories

def process_scan_result(scan_result_file: str):
    try:
        logger.info(f"Memproses file hasil scan: {scan_result_file}")         
        time.sleep(10)
 
        with open(scan_result_file, "r") as file:
            scan_result = json.load(file)
            logger.info(f"Isi scan_result: {scan_result}")  
        
        
        task_ids = scan_result.get("task_ids", [])
        logger.info(f"Menemukan {len(task_ids)} task_ids: {task_ids}")
        result_dir = os.path.join(os.path.dirname(scan_result_file), "task_result")
        os.makedirs(result_dir, exist_ok=True)
        logger.info(f"Menyimpan hasil response /task-result di direktori: {result_dir}")


        
        for task_id in task_ids:
            try:
                task_result_url = f"{os.getenv('DOCKER_URL')}task-status/{task_id}"
                logger.info(f"Mengirim request ke {task_result_url}...")
                
                
                task_response = requests.get(task_result_url, timeout=30)
                
                if task_response.status_code == 200:
                    response_data = task_response.json()
                    result_value = response_data

                    
                    file_path = response_data.get("result", {}).get("file_path", "")
                    if not file_path:
                        logger.warning(f"file_path tidak ditemukan untuk task {task_id}")
                        file_path = f"unknown_file_{task_id}"

                    
                    file_name_with_extension = os.path.basename(file_path)  
                    if not file_name_with_extension:
                        logger.warning(f"file_path tidak mengandung nama file untuk task {task_id}")
                        file_name_with_extension = f"unknown_file_{task_id}"
                    file_name_without_extension = re.sub(r"\.\w+$", "", file_name_with_extension)  
                    new_file_name = f"{file_name_without_extension}.json"
                    result_file = os.path.join(result_dir, new_file_name)

                    
                    with open(result_file, "w") as file:
                        if isinstance(result_value, str):
                            try:
                                result_value = json.loads(result_value)
                            except json.JSONDecodeError:
                                logger.warning(f"Nilai result untuk task {task_id} bukan JSON yang valid.")
                                

                        json.dump(result_value, file, indent=4)
                    logger.info(f"Hasil task {task_id} disimpan di: {result_file}")
                
                else:
                    logger.error(f"Error saat mengambil hasil task {task_id}: {task_response.status_code} - {task_response.text}")
            
            except Exception as task_error:
                logger.error(f"Error saat mengirim task {task_id}: {task_error}")
                result_file = os.path.join(result_dir, f"error_task_{task_id}.json")
                with open(result_file, "w") as file:
                    json.dump({"error": str(task_error)}, file, indent=4)
        
        logger.info("Proses selesai.")
    except FileNotFoundError:
        logger.error(f"File {scan_result_file} tidak ditemukan.")
    except json.JSONDecodeError:
        logger.error(f"File {scan_result_file} tidak valid (bukan format JSON).")
    except Exception as e:
        logger.error(f"Error saat memproses hasil scan: {e}")

def save_scan_result(output_dir: str, scan_result: dict):
    try:
        logger.info(f"Menyimpan hasil scan ke {output_dir}...")
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, "scan_result.json")
        with open(output_file, "w") as file:
            json.dump(scan_result, file, indent=4)
        logger.info(f"Hasil scan disimpan di {output_file}.")
    except Exception as e:
        logger.error(f"Error saat menyimpan hasil scan: {e}")
        raise RuntimeError(f"Gagal menyimpan hasil scan: {e}")


def run_mvt_scan(output_dir: str):
    try:
        logger.info("Menjalankan MVT scan...")
        command = [
            "mvt-android",  
            "check-adb",
            "--output", output_dir,
            "--iocs", "modules/indicators/",
            "-p", "1"
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.stdout:
            logger.info("Log MVT (stdout): ⤵")
            logger.info(result.stdout)
        if result.stderr:
            logger.error("Log MVT (stderr): ⤵")
            logger.error(result.stderr)
        
        
        if result.returncode == 0:
            logger.info("MVT scan selesai dengan sukses.")
        else:
            logger.error(f"MVT scan gagal dengan kode exit: {result.returncode}")
            raise RuntimeError(f"MVT scan gagal: {result.stderr}")
    except Exception as e:
        logger.error(f"Error saat menjalankan MVT scan: {e}")
        raise

def read_mvt_report(output_dir: str) -> List[Dict]:
    report_file = os.path.join(output_dir, "mvt_report.json")
    if not os.path.exists(report_file):
        logger.warning(f"File mvt_report.json tidak ditemukan di {output_dir}.")
        return []
    
    try:
        with open(report_file, "r") as f:
            report_data = json.load(f)
            if not isinstance(report_data, list):
                logger.error("Format mvt_report.json tidak valid.")
                return []
            return report_data
    except Exception as e:
        logger.error(f"Gagal membaca mvt_report.json: {e}")
        return []

def calculate_security_percentage_from_mvt(detections: List[Dict]) -> str:
    total_detections = len(detections)
    if total_detections == 0:
        return "98.00%"  
    
    security_percentage = max(0, 100 - (total_detections * 1))
    return f"{security_percentage:.2f}%"