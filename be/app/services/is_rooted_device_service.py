from app.repositories.is_rooted_device_repository import check_root_status_via_adb

def check_if_device_is_rooted(serial_number: str) -> bool:
    is_rooted = check_root_status_via_adb(serial_number)

    return is_rooted