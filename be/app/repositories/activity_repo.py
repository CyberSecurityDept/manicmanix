import os
import json
import subprocess
import glob
from datetime import datetime
from typing import List, Dict, Union
from app.utils.config import PROJECT_ROOT

def expand_project_root() -> str:
    try:
        expanded = os.path.expanduser(PROJECT_ROOT)
        if not os.path.exists(expanded):
            raise ValueError(f"PROJECT_ROOT invalid: {expanded}")
        return expanded
    except Exception as e:
        raise RuntimeError(f"Gagal expand PROJECT_ROOT: {str(e)}")

def get_device_id() -> Union[str, None]:
    try:
        result = subprocess.run(
            ["adb", "devices"],
            capture_output=True,
            text=True,
            check=True,
            timeout=10
        )
        
        print("[DEBUG] Raw ADB Output:\n" + result.stdout)
        
        devices = [
            line.split("\t")[0]
            for line in result.stdout.splitlines()[1:]
            if "\tdevice" in line
        ]
        
        print(f"[DEBUG] Found devices: {devices}")
        
        return devices[0] if devices else None
        
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] ADB Command failed: {e.stderr}")
        return None
    except Exception as e:
        print(f"[ERROR] Unexpected error in get_device_id: {str(e)}")
        return None

def find_latest_timestamp_dir(base_path: str) -> str:
    try:
        dirs = []
        for name in os.listdir(base_path):
            dir_path = os.path.join(base_path, name)
            if os.path.isdir(dir_path):
                try:
                    datetime.strptime(name, "%d-%m-%y_%H:%M:%S")
                    dirs.append((name, os.path.getmtime(dir_path)))
                except ValueError:
                    continue
        
        if not dirs:
            print(f"[DEBUG] No valid timestamp directories in {base_path}")
            return None
            
        # Urutkan berdasarkan modification time
        dirs.sort(key=lambda x: x[1], reverse=True)
        latest_dir = dirs[0][0]
        print(f"[DEBUG] Latest timestamp dir: {latest_dir}")
        return latest_dir
        
    except Exception as e:
        print(f"[ERROR] Error finding latest dir: {str(e)}")
        return None

def get_activities_from_file() -> Union[List[Dict], Dict]:
    """Main function untuk mendapatkan aktivitas dari file"""
    try:
        print("\n[DEBUG] Starting activities retrieval from file")
        
        # Dapatkan device ID
        device_id = get_device_id()
        if not device_id:
            print("[ERROR] No connected device")
            return {"error": "Tidak ada perangkat terhubung"}
        print(f"[DEBUG] Using device ID: {device_id}")
        
        # Expand dan validasi project root
        try:
            root = expand_project_root()
            print(f"[DEBUG] Expanded PROJECT_ROOT: {root}")
        except Exception as e:
            return {"error": str(e)}
        
        # Bangun base path
        base_path = os.path.join(
            root,
            "output-scan",
            "fast-scan",
            device_id.strip()
        )
        print(f"[DEBUG] Constructed base path: {base_path}")
        
        # Validasi base path
        if not os.path.exists(base_path):
            print(f"[ERROR] Directory not found: {base_path}")
            return {
                "error": "Direktori perangkat tidak ditemukan",
                "expected_path": base_path,
                "hint": "Pastikan direktori device sudah dibuat oleh proses scan"
            }
            
        # Cari file di semua subdirektori
        file_candidates = glob.glob(os.path.join(base_path, '*', 'dumpsys_activities_detected.json'))
        if not file_candidates:
            return {"error": "File aktivitas tidak ditemukan di subdirektori manapun"}
        
        # Pilih file terbaru berdasarkan waktu modifikasi
        latest_file = max(file_candidates, key=lambda x: os.path.getmtime(x))
        timestamp_dir = os.path.basename(os.path.dirname(latest_file))
        file_path = latest_file
        print(f"[DEBUG] Using timestamp dir: {timestamp_dir}")
        print(f"[DEBUG] Final file path: {file_path}")
            
        # Baca dan parse file
        with open(file_path, "r") as f:
            data = json.load(f)
            
        return {
            "status": "success",
            "data": data,
            "metadata": {
                "device_id": device_id,
                "timestamp": timestamp_dir,
                "file_path": file_path
            }
        }
        
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON: {str(e)}")
        return {"error": "File JSON korup/tidak valid"}
    except Exception as e:
        print(f"[CRITICAL] Unexpected error: {str(e)}")
        return {"error": f"Kesalahan sistem: {str(e)}"}

def get_fullscan_activities_from_file() -> Union[List[Dict], Dict]:
    """Main function untuk mendapatkan aktivitas fullscan"""
    try:
        print("\n[DEBUG] Starting fullscan activities retrieval")
        
        # Dapatkan device ID
        device_id = get_device_id()
        if not device_id:
            print("[ERROR] No connected device")
            return {"error": "Tidak ada perangkat terhubung"}
        print(f"[DEBUG] Using device ID: {device_id}")
        
        # Expand dan validasi project root
        try:
            root = expand_project_root()
            print(f"[DEBUG] Expanded PROJECT_ROOT: {root}")
        except Exception as e:
            return {"error": str(e)}
        
        # Bangun base path
        base_path = os.path.join(
            root,
            "output-scan",
            "full-scan",
            device_id.strip()
        )
        print(f"[DEBUG] Constructed base path: {base_path}")
        
        # Validasi base path
        if not os.path.exists(base_path):
            print(f"[ERROR] Directory not found: {base_path}")
            return {
                "error": "Direktori perangkat tidak ditemukan",
                "expected_path": base_path,
                "hint": "Pastikan direktori device sudah dibuat oleh proses scan"
            }
            
        # Cari file dumpsys_activities_detected.json secara rekursif
        file_path = find_dumpsys_activities_file(base_path)
        if not file_path:
            return {"error": "File aktivitas tidak ditemukan"}
        print(f"[DEBUG] Found file: {file_path}")
        
        # Baca dan parse file
        with open(file_path, "r") as f:
            data = json.load(f)
            
        return {
            "status": "success",
            "data": data,
            "metadata": {
                "device_id": device_id,
                "file_path": file_path
            }
        }
        
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON: {str(e)}")
        return {"error": "File JSON korup/tidak valid"}
    except Exception as e:
        print(f"[CRITICAL] Unexpected error: {str(e)}")
        return {"error": f"Kesalahan sistem: {str(e)}"}

def find_dumpsys_activities_file(base_path: str) -> Union[str, None]:
    """
    Fungsi untuk mencari file dumpsys_activities_detected.json secara rekursif
    di bawah direktori base_path.
    """
    for root_dir, _, files in os.walk(base_path):
        for file in files:
            if file == "dumpsys_activities_detected.json":
                return os.path.join(root_dir, file)
    return None