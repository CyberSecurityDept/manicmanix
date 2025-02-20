import subprocess
import re
from app.repositories.device_status_repository import DeviceStatusRepository

PHONE_KEYWORDS = [
    "Android", "Phone", "Samsung", "Xiaomi", "Huawei", "Nokia", "Qualcomm",
    "OnePlus", "Google", "Pixel", "Sony", "Xperia", "Motorola", "Moto", "Oppo",
    "Vivo", "LG", "ASUS", "Zenfone", "Lenovo", "Realme", "ZTE", "HTC",
    "BlackBerry", "Alcatel", "Meizu", "Micromax", "Spreadtrum", "Snapdragon",
    "Exynos", "Broadcom", "HiSilicon Kirin", "MediaTek", "Apple", "iPhone",
    "Honor", "Infinix", "Tecno", "Itel", "Coolpad", "Gionee", "LeEco", "Vertu",
    "Fairphone", "Unisoc", "Dimensity", "Helio", "Tensor", "Bionic",
    "Exynos Modem", "Adreno GPU", "5G", "4G LTE", "Foldable", "Dual-SIM",
    "eSIM", "AMOLED", "Super AMOLED", "LTPO", "Fast Charging", "Wireless Charging",
    "Reverse Charging", "Galaxy", "Redmi", "Mi", "Poco", "Find", "Reno", "Mate",
    "P series", "Pixel", "OnePlus Nord", "ROG Phone", "iOS", "HarmonyOS",
    "ColorOS", "MIUI", "One UI", "ZenUI", "Realme UI", "EMUI", "OxygenOS",
    "HydrogenOS", "Ultra-Wide", "Macro", "Telephoto", "Periscope", "Night Mode",
    "HDR", "AI Camera", "Depth Sensor", "Bokeh", "Face Unlock", "Fingerprint",
    "Under-Display Fingerprint", "Face ID", "Dolby Atmos", "Hi-Res Audio",
    "Stereo Speakers", "3.5mm Jack", "Gaming Phone", "Snapdragon Elite Gaming",
    "Liquid Cooling","SM8350-MTP"
]

class DeviceStatusService:

    @staticmethod
    def check_usb_connection():
        try:
            result = subprocess.run(
                ["lsusb"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            output = result.stdout.decode("utf-8").strip()
            # Buat pola regex dari PHONE_KEYWORDS
            pattern = re.compile("|".join(re.escape(kw.lower()) for kw in PHONE_KEYWORDS))
            # Cek apakah ada kecocokan di output
            if pattern.search(output.lower()):
                return True
            return False
        except Exception as e:
            print(f"Error checking USB connection: {e}")
            return False

    @staticmethod
    def check_adb_connection():
        try:
            result = subprocess.run(
                ["adb", "devices"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            output = result.stdout.decode("utf-8").strip()
            lines = output.split("\n")[1:]  # Abaikan header
            for line in lines:
                parts = line.split()
                if len(parts) == 2 and parts[1] == "device":
                    return True
            return False
        except Exception as e:
            print(f"Error checking ADB connection: {e}")
            return False
    # def check_ios_connection():
    #     print("Memeriksa koneksi iOS...")  # Debug log
    #     try:
    #         result = subprocess.run(
    #             ["ideviceinfo"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    #         )
    #         output = result.stdout.decode("utf-8").strip()
    #         error_output = result.stderr.decode("utf-8").strip()

    #         if "No device found" in error_output:
    #             print("Tidak ada perangkat iOS yang terhubung.")
    #             return False
    #         elif error_output:
    #             print(f"Kesalahan ideviceinfo: {error_output}")
    #             return False

    #         if output:
    #             print("Perangkat iOS terhubung.")
    #             return True

    #         return False
    #     except Exception as e:
    #         print(f"Error checking iOS connection: {e}")
    #         return False


    
    @staticmethod
    def check_and_save_device_status():
        is_cable_connected = DeviceStatusService.check_usb_connection()
        is_adb_connected = DeviceStatusService.check_adb_connection()
        print(f"USB Connected: {is_cable_connected}, ADB Connected: {is_adb_connected}")
        status_data = DeviceStatusRepository.save_device_status(
            is_cable_connected, is_adb_connected,
        )
        return status_data