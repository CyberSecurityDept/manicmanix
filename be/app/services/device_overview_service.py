import os
import subprocess
import requests
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from datetime import datetime
from app.repositories.device_overview_repository import DeviceRepository
from urllib.parse import quote
from dotenv import load_dotenv

load_dotenv(override=True)
class DeviceOverviewService:

    @staticmethod
    def update_device_overview(serial_number: str, data: dict):
        DeviceRepository.save_device_overview(serial_number, data)

    @staticmethod
    def run_adb_command(command):
        result = subprocess.run(command, capture_output=True, text=True)
        return result.stdout.strip()

    @staticmethod
    def get_device_model():
        return DeviceOverviewService.run_adb_command(
            ["adb", "shell", "getprop", "ro.product.model"]
        )

    @staticmethod
    def get_android_version():
        return DeviceOverviewService.run_adb_command(
            ["adb", "shell", "getprop", "ro.build.version.release"]
        )

    @staticmethod
    def get_security_patch():
        return DeviceOverviewService.run_adb_command(
            ["adb", "shell", "getprop", "ro.build.version.security_patch"]
        )

    @staticmethod
    def get_serial_number():
        return DeviceOverviewService.run_adb_command(["adb", "get-serialno"])

    @staticmethod
    def get_last_scan(serial_number: str):
        last_scan = DeviceRepository.get_last_scan(serial_number)
        if last_scan is None:
            return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return last_scan

    @staticmethod
    def get_device_name(serial_number: str) -> str:
        try:
            # Get the brand of the device
            brand = subprocess.check_output(
                ["adb", "-s", serial_number, "shell", "getprop", "ro.product.brand"],
                stderr=subprocess.STDOUT
            ).decode("utf-8").strip()

            # Get the model of the device
            model = subprocess.check_output(
                ["adb", "-s", serial_number, "shell", "getprop", "ro.product.model"],
                stderr=subprocess.STDOUT
            ).decode("utf-8").strip()

            # Combine brand and model
            return f"{brand} {model}"
        except subprocess.CalledProcessError as e:
            # Handle errors, such as when the device is not connected or ADB fails
            return f"Error retrieving device name for serial {serial_number}: {e.output.decode('utf-8').strip()}"


    @staticmethod
    def get_imei(slot: int) -> str:
        result = subprocess.run(
            ["bash", "app/utils/bash/get-imei.sh"], capture_output=True, text=True
        )
        imei_lines = result.stdout.strip().split("\n")

        if slot == 1:
            return imei_lines[0].replace("IMEI 1: ", "").strip()
        elif slot == 2:
            return imei_lines[1].replace("IMEI 2: ", "").strip()
        else:
            return "Tidak valid"

    @staticmethod
    def get_device_images(model: str) -> str:
        try:
            base_url = f"{os.getenv('BASE_URL_DEVICE_OVERVIEW')}static/phone-images/images"
            brand = DeviceOverviewService.get_device_brand()
            encode_image = quote(model)
            image_url = f"{base_url}/{brand}/{encode_image}.jpg"
            
            local_path = os.path.join("static/phone-images/images", brand, f"{model}.jpg")
            if os.path.exists(local_path):
                return image_url
            else:
                print(f"Gambar tidak ditemukan untuk model: {model}. Menggunakan default.")
                return f"{base_url}/default.jpg"  # URL default jika file tidak ditemukan
        except Exception as e:
            print(f"Error saat mengakses folder lokal: {e}")
            return f"{os.getenv('BASE_URL_DEVICE_OVERVIEW_DEFAULT')}static/phone-images/images/default.jpg"
    
    @staticmethod
    def get_device_brand() -> str:
        try:
            import subprocess
            brand = subprocess.check_output("adb shell getprop ro.product.brand", shell=True).decode('utf-8').strip()
            return brand.lower()
        except Exception as e:
            print(f"Error mendapatkan brand dari perangkat: {e}")
            return "default"


    @staticmethod
    def get_device_overview():
        serial_number = DeviceOverviewService.get_serial_number()
        model = DeviceOverviewService.get_device_model()  # Ambil model perangkat
        overview = {
            "name": DeviceOverviewService.get_device_name(serial_number),
            "image": DeviceOverviewService.get_device_images(model),  # Gambar diambil berdasarkan model
            "model": model,
            "imei1": DeviceOverviewService.get_imei(1),
            "imei2": DeviceOverviewService.get_imei(2),
            "android_version": DeviceOverviewService.get_android_version(),
            "last_scan": DeviceOverviewService.get_last_scan(serial_number),
            "security_patch": DeviceOverviewService.get_security_patch(),
            "serial_number": serial_number,
        }

        DeviceRepository.save_device_overview(serial_number, overview)
        return overview
