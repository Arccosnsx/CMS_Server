from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.database.models import File, User
from app.schemas.file import FileOut, FileStatus
from app.dependencies import get_current_active_user
from app.services.permission import check_admin
import os

router = APIRouter(prefix="/moderation", tags=["Moderation"])

@router.get("/pending-files", response_model=list[FileOut])
async def get_pending_files(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    check_admin(current_user)
    return db.query(File).filter(File.status == FileStatus.pending).all()

@router.post("/approve/{file_id}", response_model=FileOut)
async def approve_file(
    file_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    check_admin(current_user)
    file = db.query(File).filter(File.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    if file.status != FileStatus.pending:
        raise HTTPException(status_code=400, detail="File is not pending approval")
    
    # 移动文件到正式目录
    new_path = file.storage_path.replace('/temp/', '/approved/')
    os.makedirs(os.path.dirname(new_path), exist_ok=True)
    os.rename(file.storage_path, new_path)
    
    # 更新数据库
    file.status = FileStatus.approved
    file.storage_path = new_path
    db.commit()
    return file