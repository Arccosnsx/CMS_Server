from sqlalchemy.orm import Session
from app.database.models import User
from app.schemas.user import UserCreate
from app.utils.security import get_password_hash

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password,
        role="member"  # 默认注册为普通成员
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

from sqlalchemy.orm import Session
from app.database.models import User, StorageQuota

def get_pending_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).filter(User.role == 'pending').offset(skip).limit(limit).all()

def update_user_role(db: Session, user_id: int, role: str, approved_by: int):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    user.role = role
    user.is_active = True
    user.approved_by = approved_by
    db.commit()
    db.refresh(user)
    return user

def set_storage_quota(db: Session, quota_type: str, quota_limit: int, updated_by: int):
    quota = db.query(StorageQuota).filter(StorageQuota.quota_type == quota_type).first()
    if quota:
        quota.quota_limit = quota_limit
        quota.updated_by = updated_by
    else:
        quota = StorageQuota(
            quota_type=quota_type,
            quota_limit=quota_limit,
            updated_by=updated_by
        )
        db.add(quota)
    db.commit()
    return quota

def get_user_storage_usage(db: Session, user_id: int):
    return db.query(User.used_storage, User.storage_quota).filter(User.id == user_id).first()