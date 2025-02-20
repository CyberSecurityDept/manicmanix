from app.repositories.data_pulling_repository import Data_Pulling
from fastapi import HTTPException

class dataPullingService:
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