import json
import os
from dotenv import load_dotenv

class PackageRepository:
    def __init__(self):
        load_dotenv()
        self.base_path = os.getenv("FASTSCAN_PACKAGE_DETECTED")
        if not self.base_path:
            raise ValueError("Environment variable FASTSCAN_PACKAGE_DETECTED is not set.")
        
        self.base_path = os.path.expanduser(self.base_path)
        if not os.path.exists(self.base_path):
            raise FileNotFoundError(f"Base directory does not exist: {self.base_path}")

    def find_dumpsys_appops_detected_json(self):
        for root, dirs, files in os.walk(self.base_path):
            if "dumpsys_appops_detected.json" in files:
                return os.path.join(root, "dumpsys_appops_detected.json")
        
        raise FileNotFoundError("File 'dumpsys_appops_detected.json' not found in the specified directory or its subdirectories.")

    def find_dumpsys_appops_json(self):
        for root, dirs, files in os.walk(self.base_path):
            if "dumpsys_appops.json" in files:
                return os.path.join(root, "dumpsys_appops.json")
        
        raise FileNotFoundError("File 'dumpsys_appops.json' not found in the specified directory or its subdirectories.")