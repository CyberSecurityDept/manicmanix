import subprocess


def get_device_info() -> dict:
    """Retrieve the phone model and security patch version using ADB."""
    try:
        # Get the phone model
        model_result = subprocess.run(
            ["adb", "shell", "getprop", "ro.product.model"],
            capture_output=True,
            text=True,
        )
        phone_model = model_result.stdout.strip()

        # Get the security patch version
        patch_result = subprocess.run(
            ["adb", "shell", "getprop", "ro.build.version.security_patch"],
            capture_output=True,
            text=True,
        )
        security_patch = patch_result.stdout.strip()

        return {"phone_model": phone_model, "security_patch": security_patch}
    except Exception as e:
        return {"error": f"Failed to retrieve device info: {e}"}
