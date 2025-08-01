from fastapi import FastAPI
from pydantic import BaseModel
from enum import Enum
import json
import random

class Status(Enum):
    OPEN = "OPEN"
    IN_PROCESS = "IN_PROCESS"
    ON_REVIEW = "ON_REVIEW"
    CLOSED = "CLOSED"
    
class Task(BaseModel):
    status: Status
    descr:str

class Storage():
    __storage: str|None
    def __init___(self, storage:str|None):
        self.storage = storage
        if not os.path.exists(self.storage):
             with open(self.filename, "w") as f:
                json.dump({}, f)
        
    def get_tasks_from_database(self):
        with open(storage, "r") as db:
            try:
                tasks = json.load(db)
            except json.JSONDecodeError:
                tasks = {}
        return tasks

    def dump_tasks_to_database(self,tasks):
        with open(storage,"w") as db:
            json.dump(tasks,db,indent=4)

app = FastAPI()
storage = Storage("database.json")

@app.get("/tasks")
def get_tasks():
    return storage.get_tasks_from_database()
    

@app.post("/tasks")
def create_task(task:Task):
    
    task = task.model_dump(mode = "json")
    task_id = abs(hash(random.randbytes(32)))
    
    tasks = storage.get_tasks_from_database()
            
    tasks[task_id] = task

    storage.dump_tasks_to_database(tasks)

    return f"Task created with id {task_id}"

@app.put("/tasks/{task_id}")
def update_task(task_id: int, new_status: Status):

    tasks = storage.get_tasks_from_database()
    try:
        tasks[str(task_id)]['status'] = new_status.value
    except KeyError:
        return "No task with this ID"
    
    storage.dump_tasks_to_database(tasks)
            
    return "Task status changed succesfully"

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    tasks = storage.get_tasks_from_database()
    try:
        tasks.pop(str(task_id))
    except KeyError:
        return "No task with this ID"
    storage.dump_tasks_to_database(tasks)
    return "Task deleted succesfully"
