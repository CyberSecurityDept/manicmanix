from fastapi import FastAPI, File, UploadFile
from typing import List
from celery.result import AsyncResult
import sqlite3
import os
import json

from app.models import AddKeysRequest, ScanFilesRequest
from app.database import initialize_database, get_db_connection
from app.tasks import scan_file_task


app = FastAPI()

UPLOAD_FOLDER = "/app/uploaded_files"


@app.on_event("startup")
def startup_event():
    initialize_database()


@app.post("/upload-files/")
async def upload_files(files: List[UploadFile] = File(...)):
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    saved_files = []

    for file in files:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        # file_path = os.
        with open(file_path, "wb") as f:
            f.write(await file.read())
        saved_files.append(file_path)

    return {"uploaded_files": saved_files, "message": "Files uploaded successfully"}


@app.post("/add_keys")
def add_keys(request: AddKeysRequest):
    conn = get_db_connection()
    inserted, skipped = [], []

    for key in request.keys:
        try:
            conn.execute("INSERT INTO api_keys (key) VALUES (?)", (key,))
            conn.commit()
            inserted.append(key)
        except sqlite3.IntegrityError:
            skipped.append(key)

    conn.close()
    return {"inserted": inserted, "skipped": skipped}


@app.post("/scan-files")
def scan_files(request: ScanFilesRequest):
    tasks = [scan_file_task.delay(file_path) for file_path in request.file_paths]
    return {"task_ids": [task.id for task in tasks]}






# masalah : 
# 1. endpoint task-status masih ada di web localhost
# 2. nilai yang direturn cuma perlu task.result aja
@app.get("/task-result/{task_id}")
def get_task_status(task_id: str):

    conn = get_db_connection()
    cursor = conn.execute("SELECT * FROM task_results WHERE task_id = ?", (task_id,))
    result = cursor.fetchone()
    conn.close()



    task_result = AsyncResult(task_id)
    if task_result.state == "PENDING":
        return {"task_id": task_id, "status": task_result.state, "result": None}




    elif task_result.state == "FAILURE":
        return {
            "task_id": task_id,
            # "file_path": result["file_path"],
            "status": task_result.state,
            "result": str(task_result.info),
        }
    else:
        # return {
        #     "task_id": task_id,
        #     "file_path": result["file_path"],
        #     "status": task_result.state,
        #     "result": task_result.info,
        # }
            return task_result.info

# @app.get("/task-result/{task_id}")
# def get_task_result(task_id: str):
#     conn = get_db_connection()
#     cursor = conn.execute("SELECT * FROM task_results WHERE task_id = ?", (task_id,))
#     result = cursor.fetchone()
#     conn.close()
#     if not result:
#         return {"error": "Task not found"}
#     return {
#         "task_id": result["task_id"],
#         "file_path": result["file_path"],
#         "status": result["status"],
#         # "result": str(task_result.info),
#         "created_at": result["created_at"],
#     }