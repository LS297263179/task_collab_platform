import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from database import get_db
from schemas import AttachmentOut
from crud import create_attachment, get_attachments_by_task, delete_attachment
from dependencies import get_current_user
from models import User

router = APIRouter(prefix="/api/attachments", tags=["attachments"])

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_TYPES = {
    "image/jpeg", "image/png", "image/gif", "image/webp", "image/svg+xml",
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain", "text/csv",
    "application/zip", "application/x-zip-compressed",
}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("/task/{task_id}", response_model=AttachmentOut)
async def upload_file(
    task_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail=f"不支持的文件类型: {file.content_type}")
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="文件大小超过 10MB 限制")
    ext = os.path.splitext(file.filename)[1] if file.filename else ".bin"
    safe_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_DIR, safe_name)
    with open(file_path, "wb") as f:
        f.write(content)
    return create_attachment(
        db, task_id=task_id, filename=safe_name,
        original_name=file.filename or "unknown",
        file_size=len(content), mime_type=file.content_type or "",
        uploader_id=current_user.id,
    )


@router.get("/task/{task_id}", response_model=list[AttachmentOut])
def list_attachments(task_id: int, db: Session = Depends(get_db)):
    return get_attachments_by_task(db, task_id)


@router.delete("/{attachment_id}")
def delete(attachment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    filename = delete_attachment(db, attachment_id, current_user.id)
    if not filename:
        raise HTTPException(status_code=403, detail="Not authorized")
    file_path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    return {"message": "Attachment deleted"}


@router.get("/files/{filename}")
def serve_file(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, filename=filename)
