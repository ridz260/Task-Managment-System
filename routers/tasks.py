from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from .auth import get_current_user
from starlette import status
from sqlalchemy.orm import Session
from database import SessionLocal
from pydantic import BaseModel, Field
from models import Tasks

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


class TasksRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length = 200)
    priority: int = Field(gt = 0, lt = 11)
    status: str = Field(min_length = 3)



router = APIRouter(
    prefix = "/tasks",
    tags = ["Task Management Landing Page"]
)

user_dependency = Annotated[dict,Depends(get_current_user)]
db_dependency = Annotated[Session, Depends(get_db)]


#GET - say hello to a given user
@router.get("/hello")
async def say_hello(user: user_dependency):
    if user is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "User Authentication Failed")
    
    return "Hello"

#GET - return all task items for a given user
@router.get("/",status_code = status.HTTP_200_OK)
async def get_all_tasks(user: user_dependency,
                        db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User Authentication Failed")
    
    return db.query(Tasks).filter(Tasks.owner_id == user.get("id")).all()


#GET - get task item by id
@router.get("/{task_id}", status_code = status.HTTP_200_OK)
async def get_task_by_id(user: user_dependency,
                         db: db_dependency,
                         task_id: int):
    
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User Authorization failed!")

    task_item = db.query(Tasks).filter(task_id == Tasks.id).filter(user.get("id") == Tasks.owner_id).first()

    if not task_item:
        raise HTTPException(status_code = 404, detail = "Task item not found")
    
    return task_item




#POST - Create a new item in task for a given user
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_new_task(user: user_dependency,
                          db: db_dependency,
                          task_request: TasksRequest):
    if user is None:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "User Authentication Failed")
    
    task_model = Tasks(**task_request.dict(), owner_id = user.get("id"))

    db.add(task_model)
    db.commit()

    return "Task item is added!"
    

#PUT - Update a given item in Task for a user
@router.put("/{task_id}", status_code= status.HTTP_204_NO_CONTENT)
async def update_task(user: user_dependency,
                      db: db_dependency,
                      task_request: TasksRequest,
                      task_id: int):
    if user is None:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "User is Not Authorized")
    
    curr_item = db.query(Tasks).filter(task_id == Tasks.id).filter(Tasks.owner_id == user.get("id")).first()
    
    if curr_item is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Task item not found")
        
    curr_item.title = task_request.title
    curr_item.description = task_request.description
    curr_item.priority = task_request.priority
    curr_item.status = task_request.status

    db.add(curr_item)
    db.commit()

    return "Task item is now updated!"



#DELETE - delete a given item in Task for a user
@router.delete("/{task_id}", status_code = status.HTTP_204_NO_CONTENT)
async def delete_task_by_id(user: user_dependency,
                        db: db_dependency,
                        task_id: int):
    
    if user is None:
        raise HTTPException(status_code=404, detail="User Authentication Failed")
    
    task_item = db.query(Tasks).filter(Tasks.id == task_id).filter(Tasks.owner_id == user.get("id")).first()

    if task_item is None:
        raise HTTPException(status_code=404, detail = "Task item not found!")


    db.query(Tasks).filter(Tasks.id == task_id).filter(Tasks.owner_id == user.get("id")).delete()
    db.commit()

    
