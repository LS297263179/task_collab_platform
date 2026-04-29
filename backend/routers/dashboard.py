from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas import AuditLogOut, ProjectDashboard, NotificationOut, NotificationCount
from crud import (
    get_audit_logs, get_project_statistics, get_member_workloads, get_project, get_project_members,
    get_notifications, get_unread_count, mark_read, mark_all_read,
)
from dependencies import get_current_user
from models import User

router = APIRouter(prefix="/api", tags=["dashboard"])


@router.get("/projects/{project_id}/dashboard", response_model=ProjectDashboard)
def get_dashboard(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    members = get_project_members(db, project_id)
    stats = get_project_statistics(db, project_id, members)
    workloads = get_member_workloads(db, project_id, members)
    return ProjectDashboard(task_stats=stats, member_workloads=workloads)


@router.get("/projects/{project_id}/audit", response_model=list[AuditLogOut])
def get_audit(project_id: int, limit: int = 50, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return get_audit_logs(db, project_id, limit)


@router.get("/notifications", response_model=list[NotificationOut])
def list_notifications(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_notifications(db, current_user.id)


@router.get("/notifications/unread", response_model=NotificationCount)
def count_unread(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return NotificationCount(unread_count=get_unread_count(db, current_user.id))


@router.post("/notifications/{notification_id}/read")
def mark_as_read(notification_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not mark_read(db, current_user.id, notification_id):
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Marked as read"}


@router.post("/notifications/read-all")
def mark_all_as_read(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    mark_all_read(db, current_user.id)
    return {"message": "All notifications marked as read"}
