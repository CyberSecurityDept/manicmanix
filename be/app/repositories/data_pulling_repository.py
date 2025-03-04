import shutil
import os
import subprocess
import re

from typing import List, Dict
from fastapi import HTTPException

class Data_Pulling:
    @staticmethod
    def check_adb_connected() -> bool:
        try:
            result = subprocess.run(
                ["adb", "devices"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            output = result.stdout.decode("utf-8").strip()
            lines = output.split("\n")
            for line in lines[1:]:
                if "device" in line:
                    return True
            return False
        except Exception:
            return False

    @staticmethod
    def get_device_serials() -> List[str]:  
        try:
            result = subprocess.run(["adb", "devices"], capture_output=True, text=True, check=True)
            lines = result.stdout.strip().split("\n")[1:]  # Skip the first line
            return [line.split()[0] for line in lines if line.endswith("\tdevice")]
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to get device serials: {e.stderr}")

    @staticmethod
    def user_enum(serial: str) -> List[str]:
        try:
            result = subprocess.run(["adb", "-s", serial, "shell", "pm", "list", "users"], capture_output=True, text=True, check=True)
            
            #nge ekstrak id user dari nama user dan alias nya   
            pattern = r'UserInfo{(\d+):'
            user_ids = re.findall(pattern, result.stdout)
            return user_ids
        except subprocess.CalledProcessError as e:
            raise Exception(f"User enumeration failed for device {serial}: {e.stderr}")
        



    #ngepull semua data berdasarkan user, nanti bakal disimpen di ~/project/temp/{serial}/{user}
    @staticmethod
    def pull_files_from_android(serial: str, user: str) -> str:
        """
        Mengambil file dari perangkat Android berdasarkan user dan menyimpannya di folder tujuan.
        File-file tersebut akan disortir berdasarkan ekstensi dan dipindahkan ke folder yang sesuai.

        :param serial: Serial number perangkat Android.
        :param user: User ID pada perangkat Android.
        :return: Pesan sukses atau error.
        """
        try:
            # Path tujuan untuk menyimpan file yang di-pull dari perangkat Android
            dest_path = os.path.expanduser(f"{str(os.getenv('DESTINATION_FOR_DATA_PULLING'))}/{serial}")
            os.makedirs(dest_path, exist_ok=True)  # Buat folder jika belum ada
            
            # Path sumber di perangkat Android (misalnya, /storage/emulated/0/)
            source_path = f"/storage/emulated/{user}/"
            
            # Jalankan perintah ADB untuk menarik file dari perangkat Android
            result = subprocess.run(
                ["adb", "-s", serial, "pull", "-a", source_path, dest_path, "--sync"],
                capture_output=True, text=True, check=True
            )
            
            # Path untuk menyimpan file yang diisolasi (APK, dokumen, dll)
            isolated_path = os.path.expanduser(f"{str(os.getenv('APP_ISOLATED_FOR_VIRUS_TOTAL'))}/{serial}")
            os.makedirs(isolated_path, exist_ok=True)  # Buat folder jika belum ada
            
            # Path untuk folder installed_apps (file APK yang sudah di-pull sebelumnya)
            installed_apps_path = os.path.join(isolated_path, "installed_apps")
            
            # Daftar kategori folder untuk menyimpan file berdasarkan ekstensi
            categories = {
                'installer': os.path.join(isolated_path, 'installer'),  # Folder untuk aplikasi (APK, EXE, dll)
                'documents': os.path.join(isolated_path, 'documents'),  # Folder untuk dokumen (PDF, DOCX, dll)
                'archive': os.path.join(isolated_path, 'archive'),      # Folder untuk arsip (ZIP, RAR, dll)
                'media': os.path.join(isolated_path, 'media'),      # Folder untuk arsip (MP4, JPG, dll)
            }
            
            # Buat folder untuk setiap kategori jika belum ada
            for folder in categories.values():
                os.makedirs(folder, exist_ok=True)
            
            # Loop melalui semua file yang di-pull dari perangkat Android
            for root, _, files in os.walk(dest_path):
                for file in files:
                    # Gunakan os.path.splitext untuk mendapatkan ekstensi file (misalnya, ".apk")
                    file_extension = os.path.splitext(file)[1].lower().strip('.')  # Hapus tanda titik dari ekstensi
                    
                    # Tentukan kategori file berdasarkan ekstensi
                    category = None
                    for cat, extensions in FILE_CATEGORIES.items():
                        if file_extension in extensions:
                            category = cat  # Set kategori jika ekstensi cocok
                            break
                    
                    # Jika file termasuk dalam kategori yang ditentukan
                    if category:
                        file_path = os.path.join(root, file)  # Path lengkap file sumber
                        
                        # Periksa apakah file berada di folder installed_apps
                        if installed_apps_path in root:
                            print(f"File {file} berada di folder installed_apps. Mengabaikan.")
                            continue  # Lanjutkan ke file berikutnya jika file berada di installed_apps
                        
                        # Tentukan folder tujuan berdasarkan kategori
                        destination_folder = categories.get(category, isolated_path)  # Default ke isolated_path jika kategori tidak ditemukan
                        destination_file_path = os.path.join(destination_folder, file)  # Path lengkap file tujuan
                        
                        # Periksa apakah file sudah ada di folder tujuan
                        if os.path.exists(destination_file_path):
                            print(f"File {file} sudah ada di {destination_folder}. Mengabaikan duplikat.")
                            continue  # Lanjutkan ke file berikutnya jika file sudah ada
                        
                        # Pindahkan file ke folder tujuan
                        shutil.copy(file_path, destination_folder)
                        print(f"File {file} dipindahkan ke {destination_folder}.")

            return f"Files pulled successfully for user {user} to {dest_path}, and sorted files moved to {isolated_path}"
        except subprocess.CalledProcessError as e:
            raise Exception(f"ADB pull failed for device {serial}, user {user}: {e.stderr}")
        
    @staticmethod
    def get_base_apk(serial: str):
        """
        Mendapatkan path base.apk untuk setiap paket yang terinstal di perangkat Android dan mendownloadnya ke folder isolated_path.

        :param serial: Serial number perangkat Android.
        :return: Dictionary yang berisi nama paket dan path base.apk-nya.
        """
        try:
            # Mendapatkan daftar semua paket yang terinstal (hanya aplikasi user-installed)
            packages_output = subprocess.getoutput(f"adb -s {serial} shell pm list packages -3 --user 0")
            
            # Memisahkan output menjadi list nama paket
            packages = packages_output.replace("package:", "").splitlines()

            # Dictionary untuk menyimpan hasil
            base_apk_paths = {}

            # Path tujuan untuk menyimpan base.apk
            isolated_path = os.path.expanduser(f"{str(os.getenv('APP_ISOLATED_FOR_VIRUS_TOTAL'))}/{serial}/installed_apps/")
            os.makedirs(isolated_path, exist_ok=True)

            # Loop melalui setiap paket dan dapatkan path base.apk-nya
            for package in packages:
                try:
                    # Dapatkan output dari `adb shell pm path {package}`
                    path_output = subprocess.getoutput(f"adb -s {serial} shell pm path {package}")
                    
                    # Pisahkan output menjadi beberapa baris (setiap baris adalah path terpisah)
                    paths = path_output.strip().splitlines()

                    # Loop melalui setiap path
                    for path in paths:
                        # Ambil path base.apk dari output (biasanya dalam format "package:/path/to/base.apk")
                        base_apk_path = path.replace("package:", "").strip()

                        # Jika path base.apk ditemukan
                        if base_apk_path:
                            # Buat folder untuk setiap package
                            package_folder = os.path.join(isolated_path, package)
                            os.makedirs(package_folder, exist_ok=True)

                            # Nama file baru sesuai dengan nama package
                            new_apk_name = f"{package}.apk"
                            new_apk_path = os.path.join(package_folder, new_apk_name)

                            # Download base.apk dari perangkat Android
                            subprocess.run(["adb", "-s", serial, "pull", "-a",base_apk_path, new_apk_path, "--sync"], check=True)

                            # Simpan path baru ke dalam dictionary
                            base_apk_paths[package] = new_apk_path
                            break  # Hanya ambil base.apk, abaikan split_config jika ada

                except subprocess.CalledProcessError as e:
                    logger.error(f"Gagal menarik base.apk untuk paket {package}: {e.stderr}")
                    continue

            return base_apk_paths

        except Exception as e:
            logger.error(f"Terjadi kesalahan dalam fungsi get_base_apk: {e}")
            raise Exception(f"Failed to get base APK: {e}")
        
    @staticmethod
    def generate_isolated_json(serial: str) -> str:
        # Dapatkan path dasar dari environment variable
        base_path = os.path.expanduser(f"{str(os.getenv('APP_ISOLATED_FOR_VIRUS_TOTAL'))}/{serial}")
        
        if not os.path.isdir(base_path):
            raise Exception(f"Direktori isolasi untuk serial {serial} tidak ditemukan: {base_path}")
        
        result = {
            "archive": [],
            "documents": [],
            "installer": [],
            "application": []
        }
        
        # Proses folder kategori: archive, documents, installer
        for category in ["archive", "documents", "installer"]:
            category_path = os.path.join(base_path, category)
            if os.path.isdir(category_path):
                for file in os.listdir(category_path):
                    file_path = os.path.join(category_path, file)
                    if os.path.isfile(file_path):
                        result[category].append(file)
        
        # Proses kategori aplikasi.
        # Pertama, cek apakah terdapat folder 'installed_apps'. 
        # Sesuai fungsi get_base_apk, base.apk disimpan di:
        # APP_ISOLATED_FOR_VIRUS_TOTAL/{serial}/installed_apps/{package}/{package}.apk
        installed_apps_path = os.path.join(base_path, "installed_apps")
        if os.path.isdir(installed_apps_path):
            for package in os.listdir(installed_apps_path):
                package_dir = os.path.join(installed_apps_path, package)
                if os.path.isdir(package_dir):
                    apk_name = f"{package}.apk"
                    apk_path = os.path.join(package_dir, apk_name)
                    if os.path.isfile(apk_path):
                        result["application"].append(apk_name)
        else:
            # Jika folder 'installed_apps' tidak ada, cek folder-folder lain di level base_path
            reserved = {"archive", "documents", "installer"}
            for entry in os.listdir(base_path):
                entry_path = os.path.join(base_path, entry)
                if os.path.isdir(entry_path) and entry not in reserved:
                    apk_name = f"{entry}.apk"
                    apk_path = os.path.join(entry_path, apk_name)
                    if os.path.isfile(apk_path):
                        result["application"].append(apk_name)
        
        # Tulis data JSON ke file isolated.json di base_path
        json_file_path = os.path.join(base_path, "isolated.json")
        with open(json_file_path, "w") as json_file:
            json.dump(result, json_file, indent=4)
        
        return json_file_path
    
FILE_CATEGORIES = {

    'archive': [
        'zip', 'rar', '7z', 'tar', 'gz',
        'bz2', 'xz', 'iso', 'tgz', 'tbz2',
        'lzma', 'cab', 'z', 'lz', 'lzo'
    ],
    'installer': [
        'exe', 'msi', 'dmg', 'app', 'apk',
    ],
    'documents': [
        "pdf", "doc", "docx", "xls", "xlsx", "txt"
    ],
    'media': [
        "mov", "avi", "mp4", "mp3", "mpeg", "jpg", 
        "png", "svg", "gif", "webp", "mkv", "wav", 
        "ogg", "wmv"
    ],
    }