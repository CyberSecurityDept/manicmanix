import os

# Correctly define PROJECT_ROOT as three levels up from config.py
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUTPUT_SCAN_PATH = os.path.join(
    PROJECT_ROOT, "output-scan", "dumpsys_activities_detected.json"
)