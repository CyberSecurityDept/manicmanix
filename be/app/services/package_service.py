import json
from app.repositories.package_repositories import PackageRepository

class PackageService:
    def __init__(self, repository):
        self.repository = repository

    def get_installed_apps_data(self):
        file_path = self.repository.find_dumpsys_appops_json()
        with open(file_path, 'r', encoding='utf-8') as file:
            try:
                data = json.load(file)
                result = []
                for entry in data:
                    package_name = entry.get("package_name", "Unknown")
                    name = entry.get("name", "Unknown")
                    result.append({"package_name": package_name, "name": name})
                return {
                    "data": result,
                    "count": len(data)
                }
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON format in file: {file_path}") from e

    def get_malicious_apps_data(self):
        file_path = self.repository.find_dumpsys_appops_detected_json()
        with open(file_path, 'r', encoding='utf-8') as file:
            try:
                data = json.load(file)
                result = []
                for entry in data:
                    package_name = entry.get("package_name", "Unknown")
                    name = entry.get("name", "Unknown")
                    result.append({"package_name": package_name, "name": name})
                return {
                    "data": result,
                    "count": len(data)
                }
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON format in file: {file_path}") from e