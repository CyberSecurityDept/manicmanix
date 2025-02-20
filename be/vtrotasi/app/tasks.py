from celery import Celery
from app.database import get_db_connection
import requests
import hashlib
from datetime import datetime, timedelta

celery = Celery("tasks", broker="redis://redis:6379/0", backend="redis://redis:6379/0")

BASE_URL = "https://www.virustotal.com/api/v3/files/"
RESET_INTERVAL_HOURS = 24


def reset_limited_keys():
    conn = get_db_connection()
    cursor = conn.execute("SELECT key, reset_time FROM api_keys WHERE status = 'limited'")
    rows = cursor.fetchall()
    now = datetime.utcnow()

    for row in rows:
        reset_time = row["reset_time"]
        if reset_time and datetime.strptime(reset_time, "%Y-%m-%d %H:%M:%S") <= now:
            conn.execute(
                "UPDATE api_keys SET status = 'active', reset_time = NULL WHERE key = ?", (row["key"],)
            )  # noqa
    conn.commit()
    conn.close()


def get_active_key():
    conn = get_db_connection()
    cursor = conn.execute("SELECT key FROM api_keys WHERE status = 'active' ORDER BY usage_count ASC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    return row["key"] if row else None


def handle_api_key_limit(api_key: str):
    reset_time = (datetime.utcnow() + timedelta(hours=RESET_INTERVAL_HOURS)).strftime("%Y-%m-%d %H:%M:%S")
    conn = get_db_connection()
    conn.execute("UPDATE api_keys SET status = 'limited', reset_time = ? WHERE key = ?", (reset_time, api_key))
    conn.commit()
    conn.close()


def increment_key_usage(api_key: str):
    conn = get_db_connection()
    conn.execute(
        """
        UPDATE api_keys
        SET usage_count = usage_count + 1, last_used = ?
        WHERE key = ?
        """,
        (datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"), api_key),
    )
    conn.commit()
    conn.close()


def save_task_result(task_id, file_path, status, result):
    conn = get_db_connection()
    conn.execute(
        """
        INSERT INTO task_results (task_id, file_path, status, result)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(task_id) DO UPDATE SET
        status=excluded.status, result=excluded.result
        """,
        (task_id, file_path, status, result),
    )
    conn.commit()
    conn.close()


@celery.task(bind=True)
def scan_file_task(self, file_path):
    reset_limited_keys()

    api_key = get_active_key()
    if not api_key:
        save_task_result(self.request.id, file_path, "FAILURE", "No active API keys available.")
        return {"file_path": file_path, "error": "No active API keys available."}

    headers = {"x-apikey": api_key}

    # Calculate file hash
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
    except FileNotFoundError:
        save_task_result(self.request.id, file_path, "FAILURE", "File not found.")
        return {"file_path": file_path, "error": "File not found."}

    file_hash = sha256_hash.hexdigest()
    url = BASE_URL + file_hash

    while True:
        response = requests.get(url, headers=headers)

        if response.status_code == 429:
            handle_api_key_limit(api_key)
            api_key = get_active_key()
            if not api_key:
                save_task_result(
                    self.request.id, file_path, "FAILURE", "All API keys have reached their limit."
                )  # noqa
                return {"file_path": file_path, "error": "All API keys have reached their limit."}
            headers["x-apikey"] = api_key
        elif response.status_code == 404:
            with open(file_path, "rb") as file:
                upload_response = requests.post(
                    "https://www.virustotal.com/api/v3/files", headers=headers, files={"file": file}
                )
                if upload_response.status_code != 200:
                    save_task_result(self.request.id, file_path, "FAILURE", "Error uploading file.")
                    return {"file_path": file_path, "error": "Error uploading file to VirusTotal."}
                increment_key_usage(api_key)
                save_task_result(self.request.id, file_path, "SUCCESS", str(upload_response.json()))
                return {"file_path": file_path, "response": upload_response.json()}
        else:
            increment_key_usage(api_key)
            save_task_result(self.request.id, file_path, "SUCCESS", str(response.json()))
            return {"file_path": file_path, "response": response.json()}
