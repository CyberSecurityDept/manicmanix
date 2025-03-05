import json
from pathlib import Path
import os
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RiskRepository:
    @staticmethod
    def get_latest_scan_directory(base_path: Path) -> Path:
        try:
            directories = [d for d in base_path.iterdir() if d.is_dir()]
            if not directories:
                raise FileNotFoundError(f"Tidak ada direktori scan ditemukan di {base_path}")
            latest_directory = max(directories, key=lambda x: x.stat().st_mtime)
            logger.info(f"Direktori scan terbaru ditemukan: {latest_directory}")
            return latest_directory
        except Exception as e:
            logger.error(f"Error saat mencari direktori terbaru: {e}")
            raise

    @staticmethod
    def read_task_results(task_result_dir: str) -> List[Dict]:
        task_results = []
        if not os.path.exists(task_result_dir):
            raise FileNotFoundError(f"Direktori {task_result_dir} tidak ditemukan")

        logger.info(f"Memeriksa direktori: {task_result_dir}")
        logger.info(f"File di direktori: {os.listdir(task_result_dir)}")

        for filename in os.listdir(task_result_dir):
            if filename.endswith(".json"):
                file_path = os.path.join(task_result_dir, filename)
                try:
                    with open(file_path, "r") as file:
                        data = json.load(file)
                        if isinstance(data, dict):
                            data["file"] = filename  # Tambahkan nama file ke data
                            task_results.append(data)
                        else:
                            logger.warning(f"File {filename} tidak berisi dictionary: {data}")
                except json.JSONDecodeError:
                    logger.error(f"File {filename} bukan JSON yang valid")
                except Exception as e:
                    logger.error(f"Error membaca file {filename}: {e}")
        return task_results

    @staticmethod
    def calculate_malware_risk_percentage(task_results: List[Dict]) -> List[Dict]:
        malware_risks = []

        for result in task_results:
            try:
                if not isinstance(result, dict) or "data" not in result:
                    logger.error(f"Invalid structure for result: {result}")
                    continue

                data = result.get("data", {})
                attributes = data.get("attributes", {})
                names = attributes.get("names", [])

                if not names:
                    logger.warning(f"Skipping file due to missing 'names': {result}")
                    continue

                logger.debug(f"Processing file: {names[0]}")

                stats = attributes.get("last_analysis_stats", {})
                if not stats:
                    logger.warning(f"Skipping file due to missing 'last_analysis_stats': {names[0]}")
                    continue

                total_malicious = stats.get("malicious", 0)
                total_suspicious = stats.get("suspicious", 0)
                logger.debug(f"File: {names[0]}, Malicious: {total_malicious}, Suspicious: {total_suspicious}")

                total_engines = (
                    stats.get("malicious", 0)
                    + stats.get("suspicious", 0)
                    + stats.get("undetected", 0)
                    + stats.get("failure", 0)
                    + stats.get("type-unsupported", 0)
                )

                malware_risk_percentage = (
                    0.0 if total_engines == 0 else ((total_malicious + total_suspicious) / total_engines) * 100
                )

                file_size = attributes.get("size", "unknown")
                file_type = attributes.get("type_tag", "unknown")
                file_hash = attributes.get("sha256", "unknown")
                creation_date = attributes.get("first_submission_date", "unknown")
                modification_date = attributes.get("last_modification_date", "unknown")
                access_date = attributes.get("last_analysis_date", "unknown")

                formatted_file_size = f"{file_size} bytes" if file_size != "unknown" else "unknown"

                malware_risks.append({
                    "file": names[0],
                    "file_size": formatted_file_size,
                    "file_type": file_type,
                    "file_hash": file_hash,
                    "creation_date": creation_date,
                    "modification_date": modification_date,
                    "access_date": access_date,
                    "malware_risk_percentage": malware_risk_percentage
                })

                logger.debug(f"Processed file: {names[0]} with risk percentage: {malware_risk_percentage:.2f}%")

            except Exception as e:
                logger.error(f"Error processing file {result.get('file')}: {e}")
                continue

        return malware_risks

    @staticmethod
    def calculate_security_percentage(task_results: List[Dict], k: int = 1) -> str:
        n = 0  # Jumlah file yang terindikasi malware

        for result in task_results:
            try:
                attributes = result.get("data", {}).get("attributes", {})
                stats = attributes.get("last_analysis_stats", {})
                malicious = stats.get("malicious", 0)
                suspicious = stats.get("suspicious", 0)
                logger.debug(f"File: {result.get('file')}, Malicious: {malicious}, Suspicious: {suspicious}")

                if malicious > 0 or suspicious > 0:
                    n += 1

            except Exception as e:
                logger.error(f"Error menghitung persentase keamanan untuk file {result.get('file')}: {e}")
                continue  # Lanjut ke file berikutnya jika terjadi error

        security_percentage = 100 / (1 + k * n)
        security_percentage_formatted = f"{security_percentage:.2f}%"
        logger.info(f"Jumlah file terindikasi malware/suspicious (n): {n}, Sensitivitas (k): {k}, Security Percentage: {security_percentage_formatted}")
        return security_percentage_formatted

    @staticmethod
    def extract_apk_metadata(task_results: List[Dict]) -> List[Dict]:
        apk_metadata = []

        for result in task_results:
            try:
                names = result.get("data", {}).get("attributes", {}).get("names", [])
                if not names:
                    continue

                attributes = result.get("data", {}).get("attributes", {})
                androguard = attributes.get("androguard", {})
                permissions = androguard.get("RiskIndicator", {}).get("PERM", {})
                apk_metadata.append({
                    "file": names[0] if names else "unknown",
                    "package_name": androguard.get("Package", "unknown"),
                    "main_activity": androguard.get("main_activity", "unknown"),
                    "permissions": permissions
                })
            except Exception as e:
                logger.error(f"Error mengekstrak metadata APK untuk file {result.get('file')}: {e}")
                continue
        return apk_metadata

    @staticmethod
    def extract_antivirus_results(task_results: List[Dict]) -> List[Dict]:
        antivirus_results = []
        for result in task_results:
            try:
                names = result.get("data", {}).get("attributes", {}).get("names", [])
                if not names:
                    continue

                attributes = result.get("data", {}).get("attributes", {})
                analysis_results = attributes.get("last_analysis_results", {})
                results = []

                for engine_name, details in analysis_results.items():
                    if details.get("category") == "malicious":
                        results.append({
                            "engine_name": engine_name,
                            "result": details.get("result", "unknown"),
                            "category": details.get("category", "unknown")
                        })

                antivirus_results.append({
                    "file": names[0] if names else "unknown",
                    "results": results
                })
            except Exception as e:
                logger.error(f"Error mengekstrak hasil antivirus untuk file {result.get('file')}: {e}")
                continue
        return antivirus_results