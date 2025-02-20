#!/usr/bin/env python3

import os
import sys
import json
import logging
from contextlib import redirect_stderr, redirect_stdout
import io

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mvt.android.modules.adb.base import AndroidExtraction


class CaptureLogHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.log_message = None

    def emit(self, record):
        self.log_message = self.format(record)


def adb_status():
    android_extraction = AndroidExtraction()

    response = {
        "status": "success",
        "message": "Device connected successfully",
    }

    stderr_buffer = io.StringIO()
    stdout_buffer = io.StringIO()

    log_capture = CaptureLogHandler()
    log_capture.setLevel(logging.CRITICAL)
    log_formatter = logging.Formatter("%(message)s")
    log_capture.setFormatter(log_formatter)

    logger = logging.getLogger("mvt.android.modules.adb.base")
    logger.addHandler(log_capture)

    original_exit = sys.exit

    def sys_exit(_=None):
        raise SystemExit

    sys.exit = sys_exit

    try:
        with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
            android_extraction._adb_connect()

    except SystemExit:
        error_message = log_capture.log_message

        response = {
            "status": "error",
            "message": error_message,
        }

    except Exception as e:
        response = {"status": "error", "message": str(e)}

    finally:
        sys.exit = original_exit
        logger.removeHandler(log_capture)

    return response


if __name__ == "__main__":
    result = adb_status()
    print(json.dumps(result, indent=2))
