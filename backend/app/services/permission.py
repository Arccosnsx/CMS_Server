from fastapi import HTTPException, status
from app.database.models import User

def check_admin(user: User):
    if user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )

def check_file_permission(user: User, file_owner_type: str, file_owner_id: int):
    # 管理员拥有所有权限
    if user.role == 'admin':
        return True
    
    # 用户对自己文件有权限
    if file_owner_type == 'user' and file_owner_id == user.id:
        return True
    
    # 社团成员对社团文件有权限
    if file_owner_type == 'group' and user.role == 'member':
        return True
    
    # 公共文件对所有激活用户可读
    if file_owner_type == 'public' and user.is_active:
        return True
    
    return False