import os
import requests
import json

upload = "app/uploaded_files"

#ganti ke path uploaded_files
join_root_folder = "/home/christofer/project/cundamanix/vtrotasi/uploaded_files"

# nyari nama file didalmem folder uploaded_files
#abis itu nanti path nya bakal di ganti ke /app/uploaded_files
#trus dikirim ke endpoint scan-files
file_paths = [f"/{upload}/{file}" for file in os.listdir(join_root_folder) if os.path.isfile(os.path.join(join_root_folder, file))]
url = "http://127.0.0.1:8000/scan-files"
data = {
    "file_paths": file_paths
}

json_data = json.dumps(data)

headers  = { 
    "Content-Type": "application/json"
}


response = requests.post(url, headers=headers, data=json_data,)



print("Response Status Code:", response.status_code)
print("Response Content:", response.content)