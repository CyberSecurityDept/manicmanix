from app.models.database import db

device_status_collection = db["device_status"]


class DeviceStatusRepository:
    @staticmethod
    def save_device_status(is_cable_connected: bool, is_adb_connected: bool):
        status_data = {
            "is_cable_connected": is_cable_connected,
            "is_adb_connected": is_adb_connected,
        }
        result = device_status_collection.insert_one(status_data)

        saved_status = device_status_collection.find_one({"_id": result.inserted_id})
        saved_status.pop("_id", None)

        return saved_status
