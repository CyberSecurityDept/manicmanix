from celery import Celery
from app.database import get_db_connection
import requests
import hashlib
import os
import logging
from datetime import datetime, timedelta
from tenacity import retry, wait_exponential, stop_after_attempt

# Konfigurasi Celery
celery = Celery("tasks", broker="redis://redis:6379/0", backend="redis://redis:6379/0")

# Konstanta
BASE_URL = "https://www.virustotal.com/api/v3/files/"
RESET_INTERVAL_HOURS = 24
MAX_RETRIES = 3
INITIAL_DELAY = 5
MAX_FILE_SIZE = 32 * 1024 * 1024  # 32 MB

# Konfigurasi Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def reset_limited_keys():
    conn = get_db_connection()
    cursor = conn.execute("SELECT key, reset_time FROM api_keys WHERE status = 'limited'")
    rows = cursor.fetchall()
    now = datetime.utcnow()
    for row in rows:
        reset_time = row["reset_time"]
        if reset_time and datetime.strptime(reset_time, "%Y-%m-%d %H:%M:%S") <= now:
            conn.execute(
                "UPDATE api_keys SET status = 'active', reset_time = NULL WHERE key = ?",
                (row["key"],)
            )
    conn.commit()
    conn.close()

def get_active_key():
    conn = get_db_connection()
    cursor = conn.execute(
        "SELECT key FROM api_keys WHERE status = 'active' ORDER BY usage_count ASC LIMIT 1"
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        logger.info(f"Active API key retrieved: {row['key']}")
        return row["key"]
    else:
        logger.warning("No active API keys available.")
        return None

def handle_api_key_limit(api_key: str):
    reset_time = (datetime.utcnow() + timedelta(hours=RESET_INTERVAL_HOURS)).strftime("%Y-%m-%d %H:%M:%S")
    conn = get_db_connection()
    conn.execute(
        "UPDATE api_keys SET status = 'limited', reset_time = ? WHERE key = ?",
        (reset_time, api_key)
    )
    conn.commit()
    conn.close()

def mark_api_key_as_banned(api_key: str):
    conn = get_db_connection()
    conn.execute(
        "UPDATE api_keys SET status = 'banned', reset_time = NULL WHERE key = ?",
        (api_key,)
    )
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
        status = excluded.status, result = excluded.result
        """,
        (task_id, file_path, status, result),
    )
    conn.commit()
    conn.close()

def calculate_sha256(file_path):
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise FileNotFoundError("File not found.")
    return sha256_hash.hexdigest()

def validate_file(file_path):
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        raise FileNotFoundError("File not found.")
    if os.path.getsize(file_path) > MAX_FILE_SIZE:
        logger.error(f"File size exceeds the maximum allowed limit: {file_path}")
        raise ValueError("File size exceeds the maximum allowed limit.")

@retry(wait=wait_exponential(multiplier=1, min=INITIAL_DELAY, max=60), stop=stop_after_attempt(MAX_RETRIES))
def make_api_request(api_key, url, method="GET", files=None):
    headers = {"x-apikey": api_key}
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, files=files)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP error occurred: {http_err} - URL: {url}")
        raise
    except requests.exceptions.RequestException as req_err:
        logger.error(f"Request error occurred: {req_err} - URL: {url}")
        raise

def upload_file(api_key, file_path):
    validate_file(file_path)
    url = "https://www.virustotal.com/api/v3/files"
    headers = {"x-apikey": api_key}
    with open(file_path, "rb") as file:
        try:
            response = make_api_request(api_key, url, method="POST", files={"file": file})
            logger.info(f"File uploaded successfully: {file_path}")
            return response
        except Exception as e:
            logger.error(f"Failed to upload file: {file_path} - Error: {e}")
            raise

def handle_user_not_active_error(api_key, task_id, file_path):
    retry_count = 0
    delay = INITIAL_DELAY
    while retry_count < MAX_RETRIES:
        logger.info(f"Retrying after UserNotActiveError - Attempt {retry_count + 1}")
        api_key = get_active_key()
        if not api_key:
            error_msg = "All API keys are banned or inactive."
            logger.error(error_msg)
            save_task_result(task_id, file_path, "FAILURE", error_msg)
            return {"file_path": file_path, "error": error_msg}
        try:
            report = make_api_request(api_key, BASE_URL + file_hash, method="GET")
            increment_key_usage(api_key)
            logger.info(f"Report retrieved for {file_path}: {report}")
            save_task_result(task_id, file_path, "SUCCESS", str(report))
            return {"file_path": file_path, "response": report}
        except requests.exceptions.HTTPError as http_err:
            if http_err.response.status_code == 429:
                handle_api_key_limit(api_key)
                logger.warning(f"Rate limit exceeded for API key: {api_key}")
            elif http_err.response.status_code == 404:
                logger.info(f"File not found on VirusTotal, proceeding to upload: {file_path}")
                try:
                    upload_response = upload_file(api_key, file_path)
                    increment_key_usage(api_key)
                    logger.info(f"File uploaded successfully: {file_path} - Response: {upload_response}")
                    save_task_result(task_id, file_path, "SUCCESS", str(upload_response))
                    return {"file_path": file_path, "response": upload_response}
                except Exception as e:
                    logger.error(f"Failed to upload file: {file_path} - Error: {e}")
                    save_task_result(task_id, file_path, "FAILURE", str(e))
                    return {"file_path": file_path, "error": str(e)}
            elif http_err.response.status_code == 403 and "UserNotActiveError" in http_err.response.text:
                retry_count += 1
                logger.warning(f"UserNotActiveError encountered - Retrying after {delay} seconds")
                time.sleep(delay)
                delay *= 2
            else:
                error_msg = f"Unexpected error from VirusTotal: {str(http_err)}"
                logger.error(error_msg)
                save_task_result(task_id, file_path, "FAILURE", error_msg)
                return {"file_path": file_path, "error": error_msg}
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
            save_task_result(task_id, file_path, "FAILURE", error_msg)
            return {"file_path": file_path, "error": error_msg}
    error_msg = "Max retries exceeded for UserNotActiveError."
    logger.error(error_msg)
    save_task_result(task_id, file_path, "FAILURE", error_msg)
    return {"file_path": file_path, "error": error_msg}

@celery.task(bind=True)
def scan_file_task(self, file_path):
    reset_limited_keys()
    api_key = get_active_key()
    if not api_key:
        error_msg = "No active API keys available."
        logger.error(error_msg)
        save_task_result(self.request.id, file_path, "FAILURE", error_msg)
        return {"file_path": file_path, "error": error_msg}

    try:
        file_hash = calculate_sha256(file_path)
        logger.info(f"Calculated SHA256 hash for {file_path}: {file_hash}")
    except Exception as e:
        error_msg = f"Error calculating hash: {str(e)}"
        logger.error(error_msg)
        save_task_result(self.request.id, file_path, "FAILURE", error_msg)
        return {"file_path": file_path, "error": error_msg}

    try:
        report = make_api_request(api_key, BASE_URL + file_hash, method="GET")
        increment_key_usage(api_key)
        logger.info(f"Report retrieved for {file_path}: {report}")
        save_task_result(self.request.id, file_path, "SUCCESS", str(report))
        return {"file_path": file_path, "response": report}
    except requests.exceptions.HTTPError as http_err:
        if http_err.response.status_code == 429:
            handle_api_key_limit(api_key)
            logger.warning(f"Rate limit exceeded for API key: {api_key}")
            api_key = get_active_key()
            if not api_key:
                error_msg = "All API keys have reached their limit."
                logger.error(error_msg)
                save_task_result(self.request.id, file_path, "FAILURE", error_msg)
                return {"file_path": file_path, "error": error_msg}
            try:
                report = make_api_request(api_key, BASE_URL + file_hash, method="GET")
                increment_key_usage(api_key)
                logger.info(f"Report retrieved for {file_path}: {report}")
                save_task_result(self.request.id, file_path, "SUCCESS", str(report))
                return {"file_path": file_path, "response": report}
            except Exception as e:
                error_msg = f"Error after handling rate limit: {str(e)}"
                logger.error(error_msg)
                save_task_result(self.request.id, file_path, "FAILURE", error_msg)
                return {"file_path": file_path, "error": error_msg}
        elif http_err.response.status_code == 404:
            logger.info(f"File not found on VirusTotal, proceeding to upload: {file_path}")
            try:
                upload_response = upload_file(api_key, file_path)
                increment_key_usage(api_key)
                logger.info(f"File uploaded successfully: {file_path} - Response: {upload_response}")
                save_task_result(self.request.id, file_path, "SUCCESS", str(upload_response))
                return {"file_path": file_path, "response": upload_response}
            except Exception as e:
                error_msg = f"Error uploading file: {str(e)}"
                logger.error(error_msg)
                save_task_result(self.request.id, file_path, "FAILURE", error_msg)
                return {"file_path": file_path, "error": error_msg}
        elif http_err.response.status_code == 403 and "UserNotActiveError" in http_err.response.text:
            return handle_user_not_active_error(api_key, self.request.id, file_path)
        else:
            error_msg = f"Unexpected error from VirusTotal: {str(http_err)}"
            logger.error(error_msg)
            save_task_result(self.request.id, file_path, "FAILURE", error_msg)
            return {"file_path": file_path, "error": error_msg}
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        save_task_result(self.request.id, file_path, "FAILURE", error_msg)
        return {"file_path": file_path, "error": error_msg}