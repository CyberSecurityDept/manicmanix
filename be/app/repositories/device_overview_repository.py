from app.models.database import db

device_overview_collection = db["device_overview"]


class DeviceRepository:

    @staticmethod
    def get_last_scan(serial_number: str):
        device = device_overview_collection.find_one({"serial_number": serial_number})
        if device:
            return device.get("last_scan", None)
        return None

    @staticmethod
    def save_device_overview(serial_number: str, data: dict):
        device_overview_collection.update_one(
            {"serial_number": serial_number}, {"$set": data}, upsert=True
        )

    @staticmethod
    def get_device_name(serial_number: str):
        device = device_overview_collection.find_one({"serial_number": serial_number})
        if device:
            return device.get("name", "")
        return ""

    @staticmethod
    def set_device_name(serial_number: str, name: str):
        device_overview_collection.update_one(
            {"serial_number": serial_number}, {"$set": {"name": name}}, upsert=True
        )
