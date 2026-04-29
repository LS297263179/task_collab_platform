from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator


# --- User ---
class UserBase(BaseModel):
    username: str
    email: str


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserOut(UserBase):
    id: int
    avatar: str = ""
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# --- Project ---
class ProjectCreate(BaseModel):
    name: str
    description: str = ""
    cover_color: str = "#4A90D9"


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    cover_color: Optional[str] = None


class ProjectMemberOut(BaseModel):
    id: int
    user: UserOut
    role: str
    joined_at: datetime

    class Config:
        from_attributes = True


class ProjectOut(BaseModel):
    id: int
    name: str
    description: str
    cover_color: str
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    owner: Optional[UserOut] = None
    members: list[ProjectMemberOut] = []

    class Config:
        from_attributes = True


# --- Task ---
class TaskCreate(BaseModel):
    title: str
    description: str = ""
    priority: str = "medium"
    severity: str = "medium"
    status: str = "todo"
    assignee_id: Optional[int] = None
    project_id: int
    due_date: Optional[datetime] = None
    reproduction_steps: str = ""
    environment: str = ""
    related_bug_ids: list[int] = []
    commit_hash: str = ""


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    assignee_id: Optional[int] = None
    due_date: Optional[datetime] = None
    position: Optional[int] = None
    reproduction_steps: Optional[str] = None
    environment: Optional[str] = None
    related_bug_ids: Optional[list[int]] = None
    commit_hash: Optional[str] = None


class TaskOut(BaseModel):
    id: int
    title: str
    description: str
    status: str
    priority: str
    severity: str
    position: int
    project_id: int
    assignee_id: Optional[int] = None
    creator_id: int
    due_date: Optional[datetime] = None
    reproduction_steps: Optional[str] = ""
    environment: Optional[str] = ""
    related_bug_ids: Optional[list[int]] = []
    commit_hash: Optional[str] = ""
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

    @field_validator("reproduction_steps", "environment", "commit_hash", mode="before")
    @classmethod
    def none_to_empty(cls, v):
        return "" if v is None else v

    @field_validator("related_bug_ids", mode="before")
    @classmethod
    def none_to_list(cls, v):
        return [] if v is None else v

    @field_validator("severity", "status", "priority", mode="before")
    @classmethod
    def enum_to_str(cls, v):
        if v is None:
            return "medium"
        if hasattr(v, "value"):
            return v.value
        return str(v)


# --- Comment ---
class CommentCreate(BaseModel):
    content: str
    task_id: int


class CommentOut(BaseModel):
    id: int
    content: str
    user_id: int
    task_id: int
    created_at: datetime
    user: UserOut

    class Config:
        from_attributes = True


# --- Tag ---
class TagCreate(BaseModel):
    name: str
    color: str = "#888888"


class TaskTagOut(BaseModel):
    task_id: int
    tag_id: int

    class Config:
        from_attributes = True


class TagOut(BaseModel):
    id: int
    name: str
    color: str
    project_id: int
    task_tags: list[TaskTagOut] = []

    class Config:
        from_attributes = True


# --- Auth ---
class Token(BaseModel):
    access_token: str
    token_type: str


# --- Audit Log ---
class AuditLogOut(BaseModel):
    id: int
    user_id: int
    action: str
    entity_type: str
    entity_id: int
    changes: Optional[dict] = None
    created_at: datetime
    user: Optional[UserOut] = None

    class Config:
        from_attributes = True


# --- Attachment ---
class AttachmentOut(BaseModel):
    id: int
    task_id: int
    filename: str
    original_name: str
    file_size: int
    mime_type: str
    uploader_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# --- Statistics ---
class TaskStats(BaseModel):
    by_status: dict  # {"todo": 5, "in_progress": 3, ...}
    by_priority: dict  # {"low": 2, "medium": 5, ...}
    by_severity: dict  # {"low": 2, "medium": 5, "high": 3, "urgent": 1}
    by_assignee: list[dict]  # [{user_id, username, count}]
    total: int
    overdue: int
    completed_this_week: int


class MemberWorkload(BaseModel):
    user_id: int
    username: str
    total_tasks: int
    todo: int
    in_progress: int
    review: int
    done: int
    overdue: int


class ProjectDashboard(BaseModel):
    task_stats: TaskStats
    member_workloads: list[MemberWorkload]


# --- Notification ---
class NotificationOut(BaseModel):
    id: int
    user_id: int
    message: str
    task_id: Optional[int] = None
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationCount(BaseModel):
    unread_count: int
