from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas import AuditLogOut, ProjectDashboard
from crud import get_audit_logs, get_project_statistics, get_member_workloads, get_project, get_project_members
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
