from fastapi import FastAPI
from pydantic import BaseModel
from enum import Enum
import json
import random

app = FastAPI()
class Status(Enum):
    OPEN = "OPEN"
    IN_PROCESS = "IN_PROCESS"
    ON_REVIEW = "ON_REVIEW"
    CLOSED = "CLOSED"
    
class Task(BaseModel):
    status: Status
    descr:str

def get_tasks_from_database():
    with open("database.json", "r") as db:
        try:
            tasks = json.load(db)
        except json.JSONDecodeError:
            tasks = {}
    return tasks

def dump_tasks_to_database(tasks):
    with open("database.json","w") as db:
        json.dump(tasks,db,indent=4)

@app.get("/tasks")
def get_tasks():
    with open("database.json","r") as db:
        return get_tasks_from_database()

@app.post("/tasks")
def create_task(task:Task):
    
    task = task.model_dump(mode = "json")
    task_id = abs(hash(random.randbytes(32)))
    
    tasks = get_tasks_from_database()
            
    tasks[task_id] = task

    dump_tasks_to_database(tasks)

    return f"Task created with id {task_id}"

@app.put("/tasks/{task_id}")
def update_task(task_id: int, new_status: Status):

    tasks = get_tasks_from_database()
    try:
        tasks[str(task_id)]['status'] = new_status.value
    except KeyError:
        return "No task with this ID"
    
    dump_tasks_to_database(tasks)
            
    return "Task status changed succesfully"

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    tasks = get_tasks_from_database()
    try:
        tasks.pop(str(task_id))
    except KeyError:
        return "No task with this ID"
    dump_tasks_to_database(tasks)
    return "Task deleted succesfully"
