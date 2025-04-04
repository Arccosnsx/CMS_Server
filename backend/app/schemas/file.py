from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class FileStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class FileBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, example="document.pdf")
    parent_id: Optional[str] = Field(
        None, 
        example="a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8"
    )

class FileCreate(FileBase):
    is_folder: bool = Field(False, example=False)
    owner_type: str = Field(..., example="user", pattern="^(public|group|user)$")

class FileOut(FileBase):
    id: str = Field(..., example="a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8")
    is_folder: bool
    owner_type: str
    owner_id: int
    size: int = Field(..., example=1024, ge=0)
    mime_type: Optional[str] = Field(None, example="application/pdf")
    status: FileStatus
    created_at: datetime
    updated_at: datetime
    created_by: int

    class Config:
        from_attributes = True

class FileMove(BaseModel):
    target_parent_id: str = Field(
        ..., 
        example="b2c3d4e5-f6g7-8901-h2i3-j4k5l6m7n8o9",
        description="目标文件夹ID"
    )