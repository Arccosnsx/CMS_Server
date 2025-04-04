import os
import shutil
from uuid import uuid4
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from app.config import settings
from app.database.models import File, User
from app.schemas.file import FileStatus,FileCreate
from .storage import check_storage_quota, update_storage_usage
from .permission import check_file_permission

def sanitize_filename(filename: str) -> str:
    # 移除危险字符
    return "".join(c for c in filename if c.isalnum() or c in (' ', '.', '_', '-'))

def save_upload_file(file: UploadFile, dest_path: str):
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(dest_path, "wb") as buffer:
        buffer.write(file.file.read())

def get_file_storage_path(space_type: str, user_id: int, filename: str) -> str:
    """生成文件存储路径"""
    base_path = {
        'public': os.path.join(settings.PUBLIC_ROOT, 'temp'),
        'group': settings.GROUP_ROOT,
        'user': os.path.join(settings.USER_ROOT, str(user_id))
    }[space_type]
    return os.path.join(base_path, filename)

def handle_upload(
    db: Session,
    file: UploadFile,
    space_type: str,
    user: User,
    parent_id: str = None
) -> File:
    # 检查权限
    if space_type == 'group' and user.role not in ['member', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only members can upload to group space"
        )

    # 获取文件大小
    file_size = len(file.file.read())
    file.file.seek(0)  # 重置文件指针

    # 检查存储配额
    check_storage_quota(db, user.id, file_size, space_type)

    # 生成安全文件名
    safe_name = sanitize_filename(file.filename)
    file_id = str(uuid4())
    storage_path = get_file_storage_path(space_type, user.id, f"{file_id}_{safe_name}")

    # 设置审核状态
    status = FileStatus.pending if space_type == 'public' else FileStatus.approved

    # 创建数据库记录
    db_file = File(
        id=file_id,
        name=safe_name,
        parent_id=parent_id,
        is_folder=False,
        owner_type=space_type,
        owner_id=1 if space_type == 'group' else user.id,
        storage_path=storage_path,
        size=file_size,
        mime_type=file.content_type,
        status=status,
        created_by=user.id
    )
    
    # 保存文件
    try:
        save_upload_file(file, storage_path)
        db.add(db_file)
        db.commit()
        update_storage_usage(db, user.id, file_size, 'add')
    except Exception as e:
        db.rollback()
        if os.path.exists(storage_path):
            os.remove(storage_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File upload failed: {str(e)}"
        )

    return db_file

def move_file(db: Session, file_id: str, target_parent_id: str, user: User):
    # 获取文件和目标文件夹
    file = db.query(File).filter(File.id == file_id).first()
    target_folder = db.query(File).filter(File.id == target_parent_id, File.is_folder == True).first()

    if not file or not target_folder:
        raise HTTPException(status_code=404, detail="File or folder not found")

    # 检查权限
    if not check_file_permission(user, file.owner_type, file.owner_id):
        raise HTTPException(status_code=403, detail="Permission denied")

    if not check_file_permission(user, target_folder.owner_type, target_folder.owner_id):
        raise HTTPException(status_code=403, detail="No permission to target folder")

    # 更新文件位置
    file.parent_id = target_parent_id
    db.commit()
    return file

from enum import Enum
class FileStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

def create_folder(
    db: Session,
    folder_data: FileCreate,
    user: User
) -> File:
    """创建文件夹"""
    if not folder_data.is_folder:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This endpoint is for creating folders only"
        )
    
    # 检查父文件夹权限
    if folder_data.parent_id:
        parent = db.query(File).filter(File.id == folder_data.parent_id).first()
        if not parent or not parent.is_folder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent folder not found"
            )
        
        if not check_file_permission(user, parent.owner_type, parent.owner_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No permission to parent folder"
            )
    
    # 创建文件夹记录
    folder_id = str(uuid4())
    folder = File(
        id=folder_id,
        name=folder_data.name,
        parent_id=folder_data.parent_id,
        is_folder=True,
        owner_type=folder_data.owner_type,
        owner_id=1 if folder_data.owner_type == 'group' else user.id,
        storage_path="",  # 文件夹不需要实际存储路径
        size=0,
        mime_type=None,
        status=FileStatus.approved,  # 文件夹无需审核
        created_by=user.id
    )
    
    try:
        db.add(folder)
        db.commit()
        return folder
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create folder: {str(e)}"
        )