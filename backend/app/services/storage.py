from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.models import User, StorageQuota, File
from app.dependencies import get_db

def check_storage_quota(db: Session, user_id: int, file_size: int, owner_type: str):
    """
    检查用户和社团的存储配额
    参数:
        db: 数据库会话
        user_id: 用户ID
        file_size: 文件大小(字节)
        owner_type: 文件归属类型 ('public', 'group', 'user')
    """
    # 检查用户是否存在
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 检查个人配额(对所有类型文件都检查)
    if user.used_storage + file_size > user.storage_quota:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Personal storage quota exceeded (Used: {user.used_storage}/{user.storage_quota} bytes)"
        )
    
    # 如果是社团文件，额外检查社团配额
    if owner_type == 'group':
        group_quota = db.query(StorageQuota).filter(
            StorageQuota.quota_type == 'group'
        ).first()
        
        if group_quota:
            group_usage = db.query(func.coalesce(func.sum(File.size), 0)).filter(
                File.owner_type == 'group',
                File.owner_id == 1  # 固定社团ID
            ).scalar()
            
            if group_usage + file_size > group_quota.quota_limit:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Group storage quota exceeded (Used: {group_usage}/{group_quota.quota_limit} bytes)"
                )

def update_storage_usage(db: Session, user_id: int, file_size: int, operation: str = 'add'):
    """
    更新用户存储使用情况
    参数:
        db: 数据库会话
        user_id: 用户ID
        file_size: 文件大小(字节)
        operation: 'add' 或 'remove'
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        if operation == 'add':
            user.used_storage += file_size
        elif operation == 'remove':
            user.used_storage = max(0, user.used_storage - file_size)
        db.commit()