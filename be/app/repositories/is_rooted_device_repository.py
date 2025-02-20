import subprocess

def check_root_status_via_adb(serial_number: str) -> bool:
    try:
        result = subprocess.run(
            ["adb", "-s", serial_number, "shell", "su -c 'whoami'"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if "root" in result.stdout:
            return True
        else:
            return False
    except Exception as e:
        print(f"Error checking root status via ADB: {e}")
        return False