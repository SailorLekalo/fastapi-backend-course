from fastapi import FastAPI
from pydantic import BaseModel
from enum import Enum
import uuid

app = FastAPI()
class Status(Enum):
    OPEN = "OPEN"
    IN_PROCESS = "IN_PROCESS"
    ON_REVIEW = "ON_REVIEW"
    CLOSED = "CLOSED"
    
class Task(BaseModel):
    status: Status
    descr:str

tasks = {}
@app.get("/tasks")
def get_tasks():
    return tasks

@app.post("/tasks")
def create_task(task:Task):
    task_id = uuid.uuid4()
    tasks[task_id] = task
    return f"Task created with id {task_id}"

@app.put("/tasks/{task_id}")
def update_task(task_id: int, new_status: Status):
    tasks[task_id].status = new_status
    return "Task status changed succesfully"

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    tasks.pop(task_id)
    return
