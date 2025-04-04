from pydantic import BaseModel, EmailStr, ConfigDict, Field
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(..., min_length=8)

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    storage_quota: int
    used_storage: int
    
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    role: Optional[str] = None
    is_active: Optional[bool] = None
    storage_quota: Optional[int] = None

class QuotaSetting(BaseModel):
    quota_type: str
    quota_limit: int = Field(..., gt=0, description="限额(字节)")

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None
    role: str | None = None  # 添加角色信息