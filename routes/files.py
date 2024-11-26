from fastapi import UploadFile, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from main import app, UPLOAD_DIR
from utils import process_file_with_progress
from shutil import copyfileobj
from random import randint
import os

task_status = {}

@app.post("/upload-file_with_progress/")
async def create_upload_file_with_progress(background_tasks: BackgroundTasks, file: UploadFile):
    if file.filename.endswith((".json", ".csv")):
        task_id = str(randint(1000000000, 9999999999))
        file_location = os.path.join(UPLOAD_DIR, file.filename)

        with open(file_location, "wb") as buffer:
            copyfileobj(file.file, buffer)

        task_status[task_id] = {"status": "Processing", "filename": file.filename}

        background_tasks.add_task(process_file_with_progress, filename=file.filename, task_id=task_id)

        return {"message": f"File {file.filename} is being processed.", "task_id": task_id}
    raise HTTPException(status_code=400, detail=f"While waiting for .json or .csv, returned {os.path.splitext(file.filename)[1]}")


@app.get("/status/{task_id}")
async def get_status(task_id: str):
    if task_id not in task_status:
        return HTTPException(status_code=404,detail="Task not found")

    status = task_status[task_id]
    
    return {"task_id": task_id, "status": status}


@app.get("/download/{task_id}")
async def download_file(task_id: str):
    if task_id not in task_status:
        raise HTTPException(status_code=404, detail="Task not found")

    task_info = task_status[task_id]

    if task_info["status"] == "Processing":
        raise HTTPException(status_code=400, detail="The file is still being processed.")

    filename = task_info["filename"]
    processed_file_location = os.path.join(
        UPLOAD_DIR, f"{os.path.splitext(filename)[0]}_processed{os.path.splitext(filename)[1]}"
    )

    if os.path.exists(processed_file_location):
        return FileResponse(processed_file_location, filename=f"{os.path.splitext(filename)[0]}_processed{os.path.splitext(filename)[1]}")

    raise HTTPException(status_code=404, detail="Processed file not found")
