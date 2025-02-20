import logging
import re

from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def calculate_realistic_progress(log_file_path):
    milestones = [
        "Parsing STIX2 indicators file",
        "Extracted indicators for collection",
        "Loaded a total of",
        "Checking Android device over debug bridge",
        "Running module ChromeHistory",
        "Running module SMS",
        "Running module Whatsapp",
        "Running module Processes",
        "Running module Getprop",
        "Running module Settings",
        "Running module SELinuxStatus",
        "Running module DumpsysBatteryHistory",
        "Running module DumpsysReceivers",
        "Running module DumpsysActivities",
        "Running module DumpsysDBInfo",
        "Running module DumpsysFull",
        "Running module DumpsysAppOps",
        "Running module Packages",
        "Running module Logcat",
        "Running module RootBinaries",
        "Running module Files",
        "Found a known suspicious app",
        "Extracted records on a total of",
        "Full dumpsys output stored at",
        "Please disable Developer Options and ADB",
    ]
    
    total_milestones = len(milestones)
    current_milestone = 0
    seen_milestones = set()

    scan_complete = False
    logs = []

    milestone_progress = 4  

    try:
        with open(log_file_path, "r") as log_file:
            for line in log_file:
                try:
                    log_data = line.strip().split(" - ")
                    log_message = log_data[-1]

                    
                    for milestone in milestones:
                        if re.search(milestone, log_message) and milestone not in seen_milestones:
                            current_milestone += 1
                            seen_milestones.add(milestone)
                    
                    if "Please disable Developer Options and ADB" in log_message:
                        scan_complete = True

                    
                    timestamp = log_data[0] if len(log_data) > 1 else "Unknown"
                    logs.append({"log": log_message, "datetime": timestamp})

                except Exception as e:
                    logger.error(f"Error processing log line: {line.strip()}. Error: {str(e)}")

        
        scan_percentage = current_milestone * milestone_progress

        
        if scan_complete:
            scan_percentage = 100

        
        missing_milestones = [m for m in milestones if m not in seen_milestones]
        if missing_milestones:
            pass
            

        return {
            "status": 200,
            "message": "Get Scan Progress successfully",
            "data": {
                "scan_percentage": str(int(scan_percentage)),
                "scan_complete": scan_complete,
                "log_process": logs,
            },
        }

    except FileNotFoundError:
        logger.error(f"Log file not found: {log_file_path}")
        return {
            "status": 404,
            "message": "Log file not found",
            "data": None,
        }
    except Exception as e:
        logger.error(f"Failed to calculate progress: {str(e)}")
        return {
            "status": 500,
            "message": f"Failed to calculate progress: {str(e)}",
            "data": None,
        }