from fastapi import UploadFile, BackgroundTasks
from fastapi.responses import FileResponse
from main import app, UPLOAD_DIR
from utils import process_file_with_progress
from shutil import copyfileobj
from random import randint
import os

task_status = {}

@app.post("/uploadfile_with_progress/")
async def create_upload_file_with_progress(background_tasks: BackgroundTasks, file: UploadFile):
    task_id = str(randint(1000000000, 9999999999))
    file_location = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_location, "wb") as buffer:
        copyfileobj(file.file, buffer)

    task_status[task_id] = "Processing"

    background_tasks.add_task(process_file_with_progress, filename=file.filename, task_id=task_id)

    return {"message": f"File {file.filename} is being processed.", "task_id": task_id}

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    if task_id not in task_status:
        return {"task_id": task_id, "status": "Task not found"}

    status = task_status[task_id]
    if status == "Processing":
        return {"task_id": task_id, "status": "Processing..."}
    
    return {"task_id": task_id, "status": status}

@app.get("/download/{filename}")
async def download_file(filename: str):
    processed_file_location = os.path.join(UPLOAD_DIR, f"{filename.split('.')[0]}_processed.{filename.split('.')[1]}")

    if os.path.exists(processed_file_location):
        return FileResponse(processed_file_location, filename=f"{filename.split('.')[0]}_processed.{filename.split('.')[1]}")

    return {"message": "Processed file is not ready or not found."}
