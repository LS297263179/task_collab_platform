from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas import TagCreate, TagOut
from crud import get_tags_by_project, create_tag, add_tag_to_task, remove_tag_from_task
from dependencies import get_current_user
from models import User

router = APIRouter(prefix="/api/tags", tags=["tags"])


@router.get("/project/{project_id}", response_model=list[TagOut])
def list_tags(project_id: int, db: Session = Depends(get_db)):
    return get_tags_by_project(db, project_id)


@router.post("/project/{project_id}", response_model=TagOut)
def create(project_id: int, data: TagCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_tag(db, project_id, data.name, data.color)


@router.post("/{task_id}/{tag_id}")
def add_to_task(task_id: int, tag_id: int, db: Session = Depends(get_db)):
    result = add_tag_to_task(db, task_id, tag_id)
    if result is None:
        raise HTTPException(status_code=400, detail="Tag already on task")
    return {"message": "Tag added"}


@router.delete("/{task_id}/{tag_id}")
def remove_from_task(task_id: int, tag_id: int, db: Session = Depends(get_db)):
    if not remove_tag_from_task(db, task_id, tag_id):
        raise HTTPException(status_code=404, detail="Tag not found on task")
    return {"message": "Tag removed"}
