import shutil
import os
import subprocess
import re
import json
from typing import List, Dict
from fastapi import HTTPException

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
        "ogg", "wmv", "jpeg",
    ],
}

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
            lines = result.stdout.strip().split("\n")[1:]
            return [line.split()[0] for line in lines if line.endswith("\tdevice")]
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to get device serials: {e.stderr}")

    @staticmethod
    def user_enum(serial: str) -> List[str]:
        try:
            result = subprocess.run(["adb", "-s", serial, "shell", "pm", "list", "users"], capture_output=True, text=True, check=True)
            pattern = r'UserInfo{(\d+):'
            user_ids = re.findall(pattern, result.stdout)
            return user_ids
        except subprocess.CalledProcessError as e:
            raise Exception(f"User enumeration failed for device {serial}: {e.stderr}")

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

            # Path untuk menyimpan file yang diisolasi (APK, dokumen, dll)
            isolated_path = os.path.expanduser(f"{str(os.getenv('APP_ISOLATED_FOR_VIRUS_TOTAL'))}/{serial}")

            # Bersihkan folder tujuan sebelum memproses file baru
            if os.path.exists(isolated_path):
                shutil.rmtree(isolated_path)
            os.makedirs(isolated_path, exist_ok=True)

            # Path sumber di perangkat Android (misalnya, /storage/emulated/0/)
            source_path = f"/storage/emulated/{user}/"

            # Jalankan perintah ADB untuk menarik file dari perangkat Android
            result = subprocess.run(
                ["adb", "-s", serial, "pull", "-a", source_path, dest_path, "--sync"],
                capture_output=True, text=True, check=True
            )

            # Path untuk folder installed_apps (file APK yang sudah di-pull sebelumnya)
            installed_apps_path = os.path.join(isolated_path, "installed_apps")
            os.makedirs(installed_apps_path, exist_ok=True)

            # Daftar kategori folder untuk menyimpan file berdasarkan ekstensi
            categories = {
                'installer': os.path.join(isolated_path, 'installer'),  # Folder untuk aplikasi (APK, EXE, dll)
                'documents': os.path.join(isolated_path, 'documents'),  # Folder untuk dokumen (PDF, DOCX, dll)
                'archive': os.path.join(isolated_path, 'archive'),      # Folder untuk arsip (ZIP, RAR, dll)
                'media': os.path.join(isolated_path, 'media'),          # Folder untuk media (MP4, JPG, dll)
            }

            # Buat folder untuk setiap kategori jika belum ada
            for folder in categories.values():
                os.makedirs(folder, exist_ok=True)

            # Dictionary untuk menyimpan informasi file
            file_info = {
                'archive': [],
                'documents': [],
                'installer': [],
                'media': [],
                'application': []
            }

            # Panggil fungsi get_base_apk
            base_apk_paths = Data_Pulling.get_base_apk(serial)
            print(f"Base APK paths: {base_apk_paths}")

            # Loop melalui semua file yang di-pull dari perangkat Android
            for root, _, files in os.walk(dest_path):
                for file in files:
                    file_extension = os.path.splitext(file)[1].lower().strip('.')

                    # Jika file adalah APK dan berasal dari aplikasi yang sudah terinstal
                    if file_extension == "apk" and root.startswith(installed_apps_path):
                        print(f"File {file} adalah APK dari aplikasi terinstal. Mengabaikan.")
                        continue

                    # Tentukan kategori file berdasarkan ekstensi
                    category = None
                    for cat, extensions in FILE_CATEGORIES.items():
                        if file_extension in extensions:
                            category = cat
                            break

                    # Jika file termasuk dalam kategori yang ditentukan
                    if category:
                        file_path = os.path.join(root, file)

                        # Tentukan folder tujuan berdasarkan kategori
                        destination_folder = categories.get(category, isolated_path)
                        destination_file_path = os.path.join(destination_folder, file)

                        # Periksa apakah file sudah ada di folder tujuan
                        if os.path.exists(destination_file_path):
                            print(f"File {file} sudah ada di {destination_folder}. Mengabaikan duplikat.")
                            continue

                        # Pindahkan file ke folder tujuan
                        shutil.copy(file_path, destination_folder)
                        print(f"File {file} dipindahkan ke {destination_folder}.")

                        # Tambahkan informasi file ke dictionary
                        file_info[category].append({
                            "name": file,
                            "local_path": os.path.join(root, file).replace(dest_path, f"/storage/emulated")
                        })
                    elif file_extension == "apk":
                        # Jika file adalah APK tetapi tidak masuk ke kategori lain
                        file_path = os.path.join(root, file)

                        # Pindahkan file APK ke folder installed_apps
                        destination_folder = os.path.join(isolated_path, "installed_apps")
                        destination_file_path = os.path.join(destination_folder, file)

                        # Periksa apakah file sudah ada di folder tujuan
                        if os.path.exists(destination_file_path):
                            print(f"File {file} sudah ada di {destination_folder}. Mengabaikan duplikat.")
                            continue

                        # Pindahkan file ke folder tujuan
                        shutil.copy(file_path, destination_folder)
                        print(f"File {file} dipindahkan ke {destination_folder}.")

                        # Tambahkan informasi file ke dictionary
                        file_info['application'].append({
                            "name": file,
                            "local_path": os.path.join(root, file).replace(dest_path, f"/storage/emulated")
                        })

            # Print file_info untuk verifikasi
            print(json.dumps(file_info, indent=4))

            # Tulis data JSON ke file isolated.json di base_path
            json_file_path = os.path.join(isolated_path, "isolated.json")
            with open(json_file_path, "w") as json_file:
                json.dump(file_info, json_file, indent=4)
            print(f"JSON file written to {json_file_path}")

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
            packages_output = subprocess.getoutput(f"adb -s {serial} shell pm list packages -3 --user 0")
            packages = packages_output.replace("package:", "").splitlines()
            base_apk_paths = {}
            installed_apps_path = os.path.join(os.path.expanduser(f"{str(os.getenv('APP_ISOLATED_FOR_VIRUS_TOTAL'))}/{serial}"), "installed_apps")
            os.makedirs(installed_apps_path, exist_ok=True)

            for package in packages:
                try:
                    path_output = subprocess.getoutput(f"adb -s {serial} shell pm path {package}")
                    paths = path_output.strip().splitlines()

                    for path in paths:
                        base_apk_path = path.replace("package:", "").strip()

                        if base_apk_path:
                            package_folder = os.path.join(installed_apps_path, package)
                            os.makedirs(package_folder, exist_ok=True)

                            new_apk_name = f"{package}.apk"
                            new_apk_path = os.path.join(package_folder, new_apk_name)

                            subprocess.run(["adb", "-s", serial, "pull", "-a", base_apk_path, new_apk_path, "--sync"], check=True)

                            base_apk_paths[package] = new_apk_path
                            break

                except subprocess.CalledProcessError as e:
                    print(f"Gagal menarik base.apk untuk paket {package}: {e.stderr}")
                    continue

            return base_apk_paths

        except Exception as e:
            print(f"Terjadi kesalahan dalam fungsi get_base_apk: {e}")
            raise Exception(f"Failed to get base APK: {e}")

    @staticmethod
    def get_isolated_data(device):
        isolated_file_path = f"src/isolated/{device}/isolated.json"
        if not os.path.exists(isolated_file_path):
            raise FileNotFoundError(f"File {isolated_file_path} tidak ditemukan.")

        with open(isolated_file_path, "r") as file:
            return json.load(file)