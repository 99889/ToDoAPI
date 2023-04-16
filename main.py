from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from bson.objectid import ObjectId
from typing import List, Optional

# Initialize FastAPI app
app = FastAPI()

# Initialize MongoDB client
client = MongoClient('mongodb://localhost:27017/')
db = client['todo']
collection = db['tasks']


# User Authentication
# Here, for simplicity, we are using basic auth with a single hardcoded username and password.
# In a production environment, we would want to use a more secure authentication method
@app.middleware("http")
async def authenticate(request, call_next):
    if request.headers.get('Authorization') != 'Basic YWRtaW46cGFzc3dvcmQ=':
        raise HTTPException(status_code=401, detail="Invalid credentials")
    response = await call_next(request)
    return response


# Create a new task
@app.post("/tasks/")
async def create_task(task: dict):
    result = collection.insert_one(task)
    return {"id": str(result.inserted_id)}


# Get all tasks
@app.get("/tasks/")
async def read_tasks():
    tasks = []
    for task in collection.find():
        tasks.append({
            "id": str(task['_id']),
            "title": task['title'],
            "description": task['description']
        })
    return tasks


# Get a single task
@app.get("/tasks/{task_id}")
async def read_task(task_id: str):
    task = collection.find_one({"_id": ObjectId(task_id)})
    if task:
        return {
            "id": str(task['_id']),
            "title": task['title'],
            "description": task['description']
        }
    else:
        raise HTTPException(status_code=404, detail="Task not found")


# Update a task
@app.put("/tasks/{task_id}")
async def update_task(task_id: str, task: dict):
    result = collection.update_one({"_id": ObjectId(task_id)}, {"$set": task})
    if result.modified_count == 1:
        return {"message": "Task updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="Task not found")


# Delete a task
@app.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    result = collection.delete_one({"_id": ObjectId(task_id)})
    if result.deleted_count == 1:
        return {"message": "Task deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Task not found")
