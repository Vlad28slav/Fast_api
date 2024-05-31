from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import csv
import os

app = FastAPI()


class Task(BaseModel):
    id: int
    title: str
    done: bool = False


CSV_FILE = 'todo.csv'

# Initialize CSV file with headers if it does not exist
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['id', 'title', 'done'])

@app.post("/tasks")
def add_item(task: Task):

    # Add a new task 
    with open(CSV_FILE, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['id', 'title', 'done'])
        writer.writerow(task.model_dump())

    return {"message": "Task added successfully"}

@app.get("/tasks")
def get_items():
    # Returning all rows from a database
    response = []
    with open(CSV_FILE, mode='r', newline='') as file:
        reader = csv.DictReader(file, fieldnames=['id', 'title', 'done'])
        for row in reader:
            response.append(row)

    return response

@app.get("/tasks/{title_to_get}")
def get_item_by_title(title_to_get: str):
    # Returning all rows by title
    response = []
    with open(CSV_FILE, mode='r', newline='') as file:
        reader = csv.DictReader(file, fieldnames=['id', 'title', 'done'])
        for row in reader:
            if title_to_get == row["title"]:
                response.append(row)

    return response


@app.put("/tasks/{title_id}")
def update_item(title_id: str, task: Task):
    # Read existing items
    items = []
    with open(CSV_FILE, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            items.append(row)

    # Find and update the item
    for row in items:
        if str(row['title']) == title_id:
            row['title'] = task.title
            row['id'] = task.id
            row['done'] = task.done
               
    with open(CSV_FILE, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['id', 'title', 'done'])
        writer.writeheader()
        writer.writerows(items)
    
    return "updated succusful"

@app.delete("/tasks/{task_name}")
def delete_task(task_name: str):
    tasks = []
    with open(CSV_FILE, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if str(row['title']) != task_name:
                tasks.append(row)

    with open(CSV_FILE, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['id', 'title', 'done'])
        writer.writeheader()
        writer.writerows(tasks)

    return {"message": "Task deleted successfully"}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
