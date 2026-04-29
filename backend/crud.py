from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from models import User, Project, ProjectMember, Task, Comment, Tag, TaskTag, AuditLog, Attachment
from schemas import UserCreate
from auth import hash_password, verify_password


# --- User CRUD ---
def create_user(db: Session, user: UserCreate) -> User:
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    user = get_user_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def search_users(db: Session, keyword: str, exclude_id: int) -> list[User]:
    pattern = f"%{keyword}%"
    return db.query(User).filter(
        User.id != exclude_id,
        User.username.like(pattern) | User.email.like(pattern),
    ).limit(20).all()


# --- Project CRUD ---
def create_project(db: Session, name: str, description: str, cover_color: str, owner_id: int) -> Project:
    project = Project(name=name, description=description, cover_color=cover_color, owner_id=owner_id)
    db.add(project)
    db.flush()
    member = ProjectMember(project_id=project.id, user_id=owner_id, role="owner")
    db.add(member)
    db.commit()
    db.refresh(project)
    return project


def get_projects_by_user(db: Session, user_id: int) -> list[Project]:
    members = db.query(ProjectMember).filter(ProjectMember.user_id == user_id).all()
    project_ids = [m.project_id for m in members]
    if not project_ids:
        return []
    return db.query(Project).filter(Project.id.in_(project_ids)).all()


def get_project(db: Session, project_id: int) -> Project | None:
    return db.query(Project).filter(Project.id == project_id).first()


def update_project(db: Session, project_id: int, **kwargs) -> Project | None:
    project = get_project(db, project_id)
    if not project:
        return None
    for key, value in kwargs.items():
        if value is not None:
            setattr(project, key, value)
    db.commit()
    db.refresh(project)
    return project


def delete_project(db: Session, project_id: int) -> bool:
    project = get_project(db, project_id)
    if not project:
        return False
    db.delete(project)
    db.commit()
    return True


# --- Project Member CRUD ---
def get_project_members(db: Session, project_id: int) -> list[ProjectMember]:
    return db.query(ProjectMember).filter(ProjectMember.project_id == project_id).all()


def add_project_member(db: Session, project_id: int, user_id: int, role: str = "member") -> ProjectMember | None:
    existing = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id, ProjectMember.user_id == user_id
    ).first()
    if existing:
        return None
    member = ProjectMember(project_id=project_id, user_id=user_id, role=role)
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


def remove_project_member(db: Session, project_id: int, user_id: int) -> bool:
    member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id, ProjectMember.user_id == user_id
    ).first()
    if not member:
        return False
    db.delete(member)
    db.commit()
    return True


# --- Task CRUD ---
def get_tasks_by_project(db: Session, project_id: int) -> list[Task]:
    return db.query(Task).filter(Task.project_id == project_id).order_by(Task.position).all()


def create_task(db: Session, **kwargs) -> Task:
    max_pos = db.query(Task).filter(Task.project_id == kwargs["project_id"]).count()
    # 处理前端传来的字符串日期
    if isinstance(kwargs.get("due_date"), str):
        kwargs["due_date"] = datetime.fromisoformat(kwargs["due_date"])
    task = Task(**kwargs, position=max_pos)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def get_task(db: Session, task_id: int) -> Task | None:
    return db.query(Task).filter(Task.id == task_id).first()


def update_task(db: Session, task_id: int, **kwargs) -> Task | None:
    task = get_task(db, task_id)
    if not task:
        return None
    if isinstance(kwargs.get("due_date"), str):
        kwargs["due_date"] = datetime.fromisoformat(kwargs["due_date"])
    for key, value in kwargs.items():
        if value is not None:
            setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task_id: int) -> bool:
    task = get_task(db, task_id)
    if not task:
        return False
    db.delete(task)
    db.commit()
    return True


def get_tasks_by_assignee(db: Session, user_id: int) -> list[Task]:
    return db.query(Task).filter(Task.assignee_id == user_id).all()


# --- Comment CRUD ---
def get_comments_by_task(db: Session, task_id: int) -> list[Comment]:
    return db.query(Comment).filter(Comment.task_id == task_id).order_by(Comment.created_at).all()


def create_comment(db: Session, task_id: int, user_id: int, content: str) -> Comment:
    comment = Comment(task_id=task_id, user_id=user_id, content=content)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def delete_comment(db: Session, comment_id: int, user_id: int) -> bool:
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment or comment.user_id != user_id:
        return False
    db.delete(comment)
    db.commit()
    return True


# --- Tag CRUD ---
def get_tags_by_project(db: Session, project_id: int) -> list[Tag]:
    return db.query(Tag).options(joinedload(Tag.task_tags)).filter(Tag.project_id == project_id).all()


def create_tag(db: Session, project_id: int, name: str, color: str) -> Tag:
    tag = Tag(project_id=project_id, name=name, color=color)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


def add_tag_to_task(db: Session, task_id: int, tag_id: int) -> TaskTag | None:
    existing = db.query(TaskTag).filter(TaskTag.task_id == task_id, TaskTag.tag_id == tag_id).first()
    if existing:
        return None
    task_tag = TaskTag(task_id=task_id, tag_id=tag_id)
    db.add(task_tag)
    db.commit()
    db.refresh(task_tag)
    return task_tag


def remove_tag_from_task(db: Session, task_id: int, tag_id: int) -> bool:
    task_tag = db.query(TaskTag).filter(TaskTag.task_id == task_id, TaskTag.tag_id == tag_id).first()
    if not task_tag:
        return False
    db.delete(task_tag)
    db.commit()
    return True


# --- Audit Log ---
def create_audit_log(db: Session, user_id: int, action: str, entity_type: str, entity_id: int, changes: dict | None = None):
    log = AuditLog(user_id=user_id, action=action, entity_type=entity_type, entity_id=entity_id, changes=changes)
    db.add(log)
    db.commit()


def get_audit_logs(db: Session, project_id: int, limit: int = 50) -> list[AuditLog]:
    project_task_ids = db.query(Task.id).filter(Task.project_id == project_id).subquery()
    return db.query(AuditLog).filter(
        AuditLog.entity_id.in_(db.session.query(project_task_ids)),
        AuditLog.entity_type.in_(["task", "comment"]),
    ).order_by(AuditLog.created_at.desc()).limit(limit).all()


# --- Statistics ---
def get_project_statistics(db: Session, project_id: int, members: list[ProjectMember]) -> dict:
    tasks = db.query(Task).filter(Task.project_id == project_id).all()
    now = datetime.utcnow()
    from datetime import timedelta
    week_ago = now - timedelta(days=7)

    by_status = {}
    by_priority = {}
    overdue = 0
    completed_this_week = 0

    for t in tasks:
        by_status[t.status.value if hasattr(t.status, 'value') else str(t.status)] = \
            by_status.get(t.status.value if hasattr(t.status, 'value') else str(t.status), 0) + 1
        by_priority[t.priority.value if hasattr(t.priority, 'value') else str(t.priority)] = \
            by_priority.get(t.priority.value if hasattr(t.priority, 'value') else str(t.priority), 0) + 1
        if t.due_date and t.due_date < now and (t.status.value if hasattr(t.status, 'value') else str(t.status)) != 'done':
            overdue += 1
        if (t.status.value if hasattr(t.status, 'value') else str(t.status)) == 'done' and t.updated_at and t.updated_at >= week_ago:
            completed_this_week += 1

    by_assignee = []
    member_map = {m.user_id: m.user.username for m in members}
    for m in members:
        count = sum(1 for t in tasks if t.assignee_id == m.user_id)
        by_assignee.append({"user_id": m.user_id, "username": m.user.username, "count": count})

    return {
        "by_status": by_status,
        "by_priority": by_priority,
        "by_assignee": by_assignee,
        "total": len(tasks),
        "overdue": overdue,
        "completed_this_week": completed_this_week,
    }


def get_member_workloads(db: Session, project_id: int, members: list[ProjectMember]) -> list[dict]:
    tasks = db.query(Task).filter(Task.project_id == project_id).all()
    now = datetime.utcnow()
    workloads = []
    for m in members:
        mtasks = [t for t in tasks if t.assignee_id == m.user_id]
        status_counts = {"todo": 0, "in_progress": 0, "review": 0, "done": 0}
        ov = 0
        for t in mtasks:
            s = t.status.value if hasattr(t.status, 'value') else str(t.status)
            if s in status_counts:
                status_counts[s] += 1
            if t.due_date and t.due_date < now and s != 'done':
                ov += 1
        workloads.append({
            "user_id": m.user_id,
            "username": m.user.username,
            "total_tasks": len(mtasks),
            **status_counts,
            "overdue": ov,
        })
    return workloads


# --- Attachment ---
def create_attachment(db: Session, task_id: int, filename: str, original_name: str,
                      file_size: int, mime_type: str, uploader_id: int) -> Attachment:
    att = Attachment(
        task_id=task_id, filename=filename, original_name=original_name,
        file_size=file_size, mime_type=mime_type, uploader_id=uploader_id,
    )
    db.add(att)
    db.commit()
    db.refresh(att)
    return att


def get_attachments_by_task(db: Session, task_id: int) -> list[Attachment]:
    return db.query(Attachment).filter(Attachment.task_id == task_id).order_by(Attachment.created_at.desc()).all()


def delete_attachment(db: Session, attachment_id: int, user_id: int) -> bool:
    att = db.query(Attachment).filter(Attachment.id == attachment_id).first()
    if not att or att.uploader_id != user_id:
        return False
    db.delete(att)
    db.commit()
    return att.filename
