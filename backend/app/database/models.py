from sqlalchemy import Column, Integer, String, Boolean, Enum, BigInteger, ForeignKey, TIMESTAMP
from app.database import Base
from sqlalchemy.sql import func

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

class File(Base):
    __tablename__ = "files"
    
    id = Column(String(36), primary_key=True)
    name = Column(String(255))
    size = Column(BigInteger)  # 文件大小(字节)
    owner_type = Column(Enum('public', 'group', 'user'))
    owner_id = Column(Integer)