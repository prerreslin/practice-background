from fastapi import BackgroundTasks
from main import UPLOAD_DIR
from time import sleep
from shutil import copyfileobj
import os

def process_file_with_progress(filename: str, task_id: str):
    from routes.files import task_status
    
    file_location = os.path.join(UPLOAD_DIR, filename)
    processed_file_location = os.path.join(UPLOAD_DIR, f"{filename.split('.')[0]}_processed.{filename.split('.')[1]}")

    task_status[task_id]["status"] = "Processing"
    
    sleep(5)
    with open(file_location, "rb") as f_in, open(processed_file_location, "wb") as f_out:
        copyfileobj(f_in, f_out)
    
    task_status[task_id]["status"] = "Completed"


