from sqlalchemy import Column, Integer, String, Boolean, Enum, BigInteger, ForeignKey, TIMESTAMP, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from sqlalchemy.sql import func
from enum import Enum as PyEnum

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), unique=True)
    role = Column(Enum('pending','public', 'member', 'admin', name='user_roles'), default='pending')  # 新增pending状态
    is_active = Column(Boolean, default=False)  # 默认未激活
    storage_quota = Column(BigInteger, default=107374182400)  # 默认100GB (单位: bytes)
    used_storage = Column(BigInteger, default=0)

class StorageQuota(Base):
    __tablename__ = "storage_quotas"
    
    id = Column(Integer, primary_key=True)
    quota_type = Column(Enum('public', 'group', 'user', name='quota_types'))
    quota_limit = Column(BigInteger)  # 单位: bytes
    updated_by = Column(Integer, ForeignKey('users.id'))
    updated_at = Column(TIMESTAMP, server_default=func.now())

class FileStatus(str, PyEnum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class OwnerType(str, PyEnum):
    public = "public"
    group = "group"
    user = "user"

class File(Base):
    __tablename__ = "files"
    
    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    parent_id = Column(String(36), ForeignKey('files.id'), index=True)
    is_folder = Column(Boolean, nullable=False, default=False)
    owner_type = Column(Enum(OwnerType), nullable=False)
    owner_id = Column(Integer, nullable=False)
    storage_path = Column(String(512), nullable=False)
    size = Column(BigInteger, nullable=False, default=0)
    mime_type = Column(String(100))
    status = Column(Enum(FileStatus), nullable=False, default=FileStatus.approved)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    md5 = Column(String(32), nullable=True)
    # 关系定义
    parent = relationship("File", remote_side=[id], back_populates="children")
    children = relationship("File", back_populates="parent")