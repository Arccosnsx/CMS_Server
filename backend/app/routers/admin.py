from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.database.crud import (
    get_pending_users,
    update_user_role,
    set_storage_quota,
    get_user_storage_usage
)
from app.schemas.user import UserOut, UserUpdate, QuotaSetting
from app.dependencies import get_current_active_user
from app.services.permission import check_admin
from app.database.models import User

router = APIRouter(
    prefix="/admin",
    tags=["Administration"]
)

@router.get("/pending-users", response_model=list[UserOut])
def list_pending_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    check_admin(current_user)
    return get_pending_users(db)

@router.post("/approve-user/{user_id}")
def approve_user(
    user_id: int,
    update_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    check_admin(current_user)
    user = update_user_role(db, user_id, update_data.role, current_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/set-quota", response_model=QuotaSetting)
def set_quota(
    quota: QuotaSetting,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    check_admin(current_user)
    return set_storage_quota(db, quota.quota_type, quota.quota_limit, current_user.id)

@router.get("/storage-usage/{user_id}")
def get_storage_usage(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    check_admin(current_user)
    usage = get_user_storage_usage(db, user_id)
    if not usage:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "used": usage[0],
        "quota": usage[1],
        "percentage": round((usage[0] / usage[1]) * 100, 2)
    }