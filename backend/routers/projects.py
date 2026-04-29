from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas import ProjectCreate, ProjectUpdate, ProjectOut, ProjectMemberOut, UserOut
from crud import (
    create_project, get_project, get_projects_by_user, update_project, delete_project,
    get_project_members, add_project_member, remove_project_member,
)
from dependencies import get_current_user
from models import User

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.post("", response_model=ProjectOut)
def create(data: ProjectCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_project(db, data.name, data.description, data.cover_color, current_user.id)


@router.get("", response_model=list[ProjectOut])
def list_projects(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_projects_by_user(db, current_user.id)


@router.get("/{project_id}", response_model=ProjectOut)
def get_one(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.put("/{project_id}", response_model=ProjectOut)
def update(project_id: int, data: ProjectUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return update_project(db, project_id, **data.model_dump(exclude_unset=True))


@router.delete("/{project_id}")
def delete(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    delete_project(db, project_id)
    return {"message": "Project deleted"}


# --- Members ---
@router.get("/{project_id}/members", response_model=list[ProjectMemberOut])
def list_members(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_project_members(db, project_id)


@router.post("/{project_id}/members/{user_id}", response_model=ProjectMemberOut)
def add_member(project_id: int, user_id: int, role: str = "member",
               db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only owner can add members")
    member = add_project_member(db, project_id, user_id, role)
    if not member:
        raise HTTPException(status_code=400, detail="User already in project")
    return member


@router.delete("/{project_id}/members/{user_id}")
def remove_member(project_id: int, user_id: int,
                  db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = get_project(db, project_id)
    if not project or project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only owner can remove members")
    if not remove_project_member(db, project_id, user_id):
        raise HTTPException(status_code=404, detail="Member not found")
    return {"message": "Member removed"}
