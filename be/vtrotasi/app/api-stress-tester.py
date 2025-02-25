import os
import time
import requests
import json

# Path dan konfigurasi
upload = "app/uploaded_files"
join_root_folder = "/Users/noname/malware-analysis/manicmanix/be/vtrotasi/uploaded_files"

# Dapatkan daftar file paths
file_paths = [f"/{upload}/{file}" for file in os.listdir(join_root_folder) if os.path.isfile(os.path.join(join_root_folder, file))]

# Batasi jumlah file paths yang dikirim dalam satu request
#batch_size disesuaikan dengan total api yang dimiliki, misalkan di key.db ada 5 api key, mkaa batch_size maksimal nya cuma 20-
#karena virustotal batasin 1 api itu 4 request/menit, jadi rumus nya batch_size = api-key * 4
batch_size = 20




batches = [file_paths[i:i+batch_size] for i in range(0, len(file_paths), batch_size)]

for batch in batches:
    url = "http://127.0.0.1:9000/scan-files"
    data = {"file_paths": batch}
    json_data = json.dumps(data)
    headers = {"Content-Type": "application/json"}

    # Kirim request POST ke scan-files
    response = requests.post(url, headers=headers, data=json_data)

    if response.status_code == 200:
        # Parsing response untuk mendapatkan task_ids
        response_data = response.json()
        task_ids = response_data.get("task_ids", [])

        # Tunggu 5 detik sebelum mengirim permintaan ke task-result
        time.sleep(5)

        for task_id in task_ids:
            # Kirim request GET ke task-result endpoint untuk setiap task_id
            task_result_url = f"http://localhost:9000/task-result/{task_id}"
            task_response = requests.get(task_result_url, headers={"accept": "application/json"})

            if task_response.status_code == 200:
                task_result_data = task_response.json()

                # Cek apakah "attributes" ada di dalam response
                if "attributes" in task_result_data.get("result", {}):
                    print(f"{task_id} = success")
                else:
                    print(f"{task_id} = failed")
            else:
                print(f"{task_id} = failed (HTTP Error {task_response.status_code})")
    else:
        print(f"Failed to send files to scan-files. Status Code: {response.status_code}")
        print(f"Response Content: {response.content}")