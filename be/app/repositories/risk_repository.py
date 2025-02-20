import json
import os
from typing import List, Dict
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# test gitlab
class RiskRepository:
    @staticmethod
    def read_task_results(task_result_dir: str) -> List[Dict]:
        task_results = []
        if not os.path.exists(task_result_dir):
            raise FileNotFoundError(f"Direktori {task_result_dir} tidak ditemukan")

        logger.info(f"Memeriksa direktori: {task_result_dir}")
        logger.info(f"File di direktori: {os.listdir(task_result_dir)}")

        for filename in os.listdir(task_result_dir):
            print(filename)
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
                # Validasi struktur dasar input
                if not isinstance(result, dict) or "data" not in result:
                    logger.error(f"Invalid structure for result: {result}")
                    continue
                
                # Ekstraksi data
                data = result.get("data", {})
                attributes = data.get("attributes", {})
                names = attributes.get("names", [])
                
                # Jika tidak ada nama file, skip
                if not names:
                    logger.warning(f"Skipping file due to missing 'names': {result}")
                    continue
                
                # Log nama file untuk debugging
                logger.debug(f"Processing file: {names[0]}")
                
                # Ambil statistik analisis
                stats = attributes.get("last_analysis_stats", {})
                if not stats:
                    logger.warning(f"Skipping file due to missing 'last_analysis_stats': {names[0]}")
                    continue
                
                # Hitung nilai malicious dan suspicious
                total_malicious = stats.get("malicious", 0)
                total_suspicious = stats.get("suspicious", 0)
                logger.debug(f"File: {names[0]}, Malicious: {total_malicious}, Suspicious: {total_suspicious}")
                
                # Hitung total mesin analisis
                total_engines = (
                    stats.get("malicious", 0)
                    + stats.get("suspicious", 0)
                    + stats.get("undetected", 0)
                    + stats.get("failure", 0)
                    + stats.get("type-unsupported", 0)
                )
                
                # Hitung persentase risiko malware
                malware_risk_percentage = (
                    0.0 if total_engines == 0 
                    else ((total_malicious + total_suspicious) / total_engines) * 100
                )
                
                # Ambil informasi tambahan dari attributes
                file_size = attributes.get("size", "unknown")
                file_type = attributes.get("type_tag", "unknown")
                file_hash = attributes.get("sha256", "unknown")
                creation_date = attributes.get("first_submission_date", "unknown")
                modification_date = attributes.get("last_modification_date", "unknown")
                access_date = attributes.get("last_analysis_date", "unknown")
                
                # Format ukuran file jika tersedia
                formatted_file_size = f"{file_size} bytes" if file_size != "unknown" else "unknown"
                
                # Tambahkan hasil ke list malware_risks
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
                # Ambil data dari last_analysis_stats
                attributes = result.get("data", {}).get("attributes", {})
                stats = attributes.get("last_analysis_stats", {})
                malicious = stats.get("malicious", {})
                print(f"Nilai malicious : {malicious}")
                
                # Hitung jumlah file yang terindikasi malware
                if stats.get("malicious", 0) > 0:
                    n += 1
            except Exception as e:
                logger.error(f"Error menghitung persentase keamanan untuk file {result.get('file')}: {e}")
                continue  # Lanjut ke file berikutnya jika terjadi error

        # Hitung persentase keamanan berdasarkan rumus
        security_percentage = 100 / (1 + k * n)

        # Format ke dalam bentuk persentase
        security_percentage_formatted = f"{security_percentage:.2f}%"

        logger.info(f"Jumlah file terindikasi malware (n): {n}, Sensitivitas (k): {k}, Security Percentage: {security_percentage_formatted}")

        return security_percentage_formatted
    
    @staticmethod
    def extract_apk_metadata(task_results: List[Dict]) -> List[Dict]:
        apk_metadata = []
        
        for result in task_results:
            try:
                # ambil atribut names dari json
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
                # ambil atribut names dari json
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