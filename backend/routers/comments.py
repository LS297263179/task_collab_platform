from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas import CommentCreate, CommentOut
from crud import get_comments_by_task, create_comment, delete_comment, create_audit_log
from dependencies import get_current_user
from models import User

router = APIRouter(prefix="/api/comments", tags=["comments"])


@router.get("/task/{task_id}", response_model=list[CommentOut])
def list_comments(task_id: int, db: Session = Depends(get_db)):
    return get_comments_by_task(db, task_id)


@router.post("", response_model=CommentOut)
def create(data: CommentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    comment = create_comment(db, data.task_id, current_user.id, data.content)
    create_audit_log(db, current_user.id, "create", "comment", comment.id, {"task_id": data.task_id})
    return comment


@router.delete("/{comment_id}")
def delete(comment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not delete_comment(db, comment_id, current_user.id):
        raise HTTPException(status_code=404, detail="Comment not found or not authorized")
    create_audit_log(db, current_user.id, "delete", "comment", comment_id)
    return {"message": "Comment deleted"}
