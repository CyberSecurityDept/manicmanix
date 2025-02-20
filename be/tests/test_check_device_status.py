import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import subprocess
from app.main import app

client = TestClient(app)

dummy_lsusb_output = """
Bus 001 Device 002: ID 18d1:4ee7 Google Inc. Nexus/Pixel Device (MTP)
Bus 002 Device 003: ID 1a2b:3c4d Qualcomm Snapdragon Phone
"""
dummy_adb_output_no_device = """
List of devices attached
"""
dummy_adb_output_with_device = """
List of devices attached
R9CX1011H9H	device
"""


@pytest.fixture
def mock_subprocess_run():
    with patch("app.services.device_status_service.subprocess.run") as mock_run:
        yield mock_run


@pytest.fixture
def set_lsusb_output(mock_subprocess_run):
    def set_output(lsusb_output, adb_output):
        def mock_run(command, *args, **kwargs):
            if command == ["lsusb"]:
                return subprocess.CompletedProcess(
                    args=command, returncode=0, stdout=lsusb_output.encode()
                )
            elif command == ["adb", "devices"]:
                return subprocess.CompletedProcess(
                    args=command, returncode=0, stdout=adb_output.encode()
                )
            return subprocess.CompletedProcess(args=command, returncode=0, stdout=b"")

        mock_subprocess_run.side_effect = mock_run

    return set_output


# def test_check_device_status_with_device(set_lsusb_output):
#     set_lsusb_output(dummy_lsusb_output, dummy_adb_output_with_device)

#     response = client.get("/v1/check-device-status/")
#     assert response.status_code == 200
#     data = response.json()
#     assert data["status"] == 200
#     assert data["data"]["is_cable_connected"] is True
#     assert data["data"]["is_adb_connected"] is True


# def test_check_device_status_no_adb_device(set_lsusb_output):
#     set_lsusb_output(dummy_lsusb_output, dummy_adb_output_no_device)

#     response = client.get("/v1/check-device-status/")
#     assert response.status_code == 200
#     data = response.json()
#     assert data["status"] == 200
#     assert data["data"]["is_cable_connected"] is True
#     assert data["data"]["is_adb_connected"] is False


# def test_check_device_status_no_usb_device(set_lsusb_output):
#     set_lsusb_output("", dummy_adb_output_no_device)

#     response = client.get("/v1/check-device-status/")
#     assert response.status_code == 200
#     data = response.json()
#     assert data["status"] == 200
#     assert data["data"]["is_cable_connected"] is False
#     assert data["data"]["is_adb_connected"] is False
