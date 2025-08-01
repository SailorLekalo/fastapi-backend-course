from fastapi import FastAPI
from pydantic import BaseModel
from enum import Enum
from dotenv import load_dotenv
import json
import random
import requests
import os

class Status(Enum):
    OPEN = "OPEN"
    IN_PROCESS = "IN_PROCESS"
    ON_REVIEW = "ON_REVIEW"
    CLOSED = "CLOSED"
    
class Task(BaseModel):
    status: Status
    descr:str

class Storage:
    __TOKEN: str
    __GIST_ID: str
    __GIST_FILENAME: str
    
    def __init__(self, TOKEN: str, GIST_ID: str, GIST_FILENAME: str):
        self.__TOKEN = TOKEN
        self.__GIST_ID = GIST_ID
        self.__GIST_FILENAME = GIST_FILENAME
        
    def get_tasks_from_database(self):
        
        url = f"https://api.github.com/gists/{self.__GIST_ID}"
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }

        response = requests.get(url, headers=headers)
        return json.loads(response.json()['files'][self.__GIST_FILENAME]['content'])

    def dump_tasks_to_database(self,tasks):
        url = f"https://api.github.com/gists/{self.__GIST_ID}"
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.__TOKEN}",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        data = {
            "files": {
                f"{self.__GIST_FILENAME}": {
                    "content": json.dumps(tasks,ensure_ascii=False)
                }
            }
        }
        response = requests.patch(url, headers=headers, json=data)
        print(response)
        


app = FastAPI()
load_dotenv()
storage = Storage(os.getenv('TOKEN'), os.getenv('GIST_ID'), os.getenv('GIST_FILENAME'))



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
