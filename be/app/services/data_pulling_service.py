from app.repositories.data_pulling_repository import Data_Pulling
from fastapi import HTTPException

class dataPullingService:
    def check_adb_connected(self) -> bool:
        try:
            return Data_Pulling.check_adb_connected()
        except Exception as e:
            raise Exception(f"Error checking ADB connection: {e}")

    def get_device_serials(self) -> list:
        try:
            return Data_Pulling.get_device_serials()
        except Exception as e:
            raise Exception(f"Error getting device serials: {e}")

    def user_enum(self, serial_number: str) -> list:
        try:
            return Data_Pulling.user_enum(serial_number)
        except Exception as e:
            raise Exception(f"Error enumerating users for device {serial_number}: {e}")

    def pull_files_from_android(self, serial_number: str, user_id: str) -> str:
        try:
            return Data_Pulling.pull_files_from_android(serial_number, user_id)
        except Exception as e:
            raise Exception(f"Error pulling files for device {serial_number}, user {user_id}: {e}")

    @staticmethod
    def process_all_devices():
        try:
            if not Data_Pulling.check_adb_connected():
                raise Exception("No devices connected via ADB")
            device_serials = Data_Pulling.get_device_serials()
            if not device_serials:
                raise Exception("No devices found")
            all_categories = []
            for serial in device_serials:
                user_ids = Data_Pulling.user_enum(serial)
                for user in user_ids:
                    Data_Pulling.pull_files_from_android(serial, user)
                    categories = Data_Pulling.categorize_files(serial, user)
                    all_categories.extend(categories)
            return all_categories
        except Exception as e:
            raise Exception(str(e))