from fastapi import APIRouter, Depends, UploadFile, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.database.models import User, File
from app.schemas.file import FileOut, FileMove
from app.schemas.file import FileCreate, FileOut, FileMove, FileStatus
from app.dependencies import get_current_active_user
from app.services.file_service import handle_upload, move_file
from app.services.permission import check_file_permission
from typing import Optional
import os

router = APIRouter(prefix="/files", tags=["Files"])

@router.post("/upload/{space_type}", response_model=FileOut)
async def upload_file(
    space_type: str,
    file: UploadFile,
    parent_id: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return handle_upload(db, file, space_type, current_user, parent_id)

@router.get("/download/{file_id}")
async def download_file(
    file_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    file = db.query(File).filter(File.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    if not check_file_permission(current_user, file.owner_type, file.owner_id):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    if file.status != FileStatus.approved:
        raise HTTPException(status_code=403, detail="File not approved")
    
    if not os.path.exists(file.storage_path):
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    return FileResponse(
        file.storage_path,
        filename=file.name,
        media_type=file.mime_type
    )

@router.post("/move/{file_id}", response_model=FileOut)
async def move_file(
    file_id: str,
    move_data: FileMove,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return move_file(db, file_id, move_data.target_parent_id, current_user)

@router.post("/create-folder", response_model=FileOut)
async def create_folder(
    folder_data: FileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建新文件夹"""
    if not folder_data.is_folder:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Use this endpoint only for folder creation"
        )
    
    return create_folder(db, folder_data, current_user)

@router.get("/list/{space_type}", response_model=list[FileOut])
async def list_files(
    space_type: str,
    parent_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """列出目录内容"""
    if space_type not in ('public', 'group', 'user'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid space type"
        )
    
    # 检查权限
    if space_type == 'group' and current_user.role not in ('member', 'admin'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Group space requires member role"
        )
    
    query = db.query(File).filter(
        File.owner_type == space_type,
        File.parent_id == parent_id,
        File.status == FileStatus.approved
    )
    
    if space_type == 'user':
        query = query.filter(File.owner_id == current_user.id)
    elif space_type == 'group':
        query = query.filter(File.owner_id == 1)  # 社团固定ID
    
    return query.all()