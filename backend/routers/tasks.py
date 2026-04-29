from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas import TaskCreate, TaskUpdate, TaskOut
from crud import (
    get_tasks_by_project, create_task, get_task, update_task, delete_task, create_audit_log,
    create_notification,
)
from dependencies import get_current_user
from models import User

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("/project/{project_id}", response_model=list[TaskOut])
def list_tasks(project_id: int, db: Session = Depends(get_db)):
    return get_tasks_by_project(db, project_id)


@router.get("/mine", response_model=list[TaskOut])
def list_mine(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    from crud import get_tasks_by_assignee
    return get_tasks_by_assignee(db, current_user.id)


@router.post("", response_model=TaskOut)
def create(data: TaskCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = create_task(db, **data.model_dump(), creator_id=current_user.id)
    create_audit_log(db, current_user.id, "create", "task", task.id, {"title": task.title})
    # Notify assignee if assigned
    if data.assignee_id and data.assignee_id != current_user.id:
        create_notification(db, data.assignee_id, f"{current_user.username} 创建并指派了一个 Bug 给你: {task.title}", task.id)
    return task


@router.get("/{task_id}", response_model=TaskOut)
def get_one(task_id: int, db: Session = Depends(get_db)):
    task = get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=TaskOut)
def update(task_id: int, data: TaskUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    old_task = get_task(db, task_id)
    if not old_task:
        raise HTTPException(status_code=404, detail="Task not found")
    changes = data.model_dump(exclude_unset=True)
    task = update_task(db, task_id, **changes)
    create_audit_log(db, current_user.id, "update", "task", task_id, changes)
    # Notify on assignee change or status change
    if changes.get("assignee_id") and changes["assignee_id"] != current_user.id:
        create_notification(db, changes["assignee_id"], f"{current_user.username} 将 Bug #{task_id} 指派给你", task_id)
    if changes.get("status") and old_task.assignee_id and old_task.assignee_id != current_user.id:
        create_notification(db, old_task.assignee_id, f"{current_user.username} 将 Bug #{task_id} 状态改为 {changes['status']}", task_id)
    return task


@router.delete("/{task_id}")
def delete(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = get_task(db, task_id)
    if task and task.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    if not delete_task(db, task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    create_audit_log(db, current_user.id, "delete", "task", task_id)
    return {"message": "Task deleted"}
